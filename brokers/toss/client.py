"""Toss Securities Open API REST client.

Handles the Bearer token, the X-Tossinvest-Account header, and retries:
- 401 (expired/invalid/revoked by re-issue) -> re-issue the token once and retry.
- 429 -> wait for Retry-After.
- 5xx / network errors -> error.data.retryAfterSeconds (maintenance) or exponential backoff.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Literal

import httpx

from brokers.toss import auth, config

__all__ = [
    "REISSUE_CODES",
    "OrderQuery",
    "OrderStatus",
    "TossApiError",
    "TossClient",
]

log = logging.getLogger("toss.client")

# 401 codes that a token re-issue resolves. login-user-not-found is not one of them.
REISSUE_CODES = {"expired-token", "invalid-token", "token-revoked"}

# Lifecycle group filter for GET /api/v1/orders (not the per-order orders[].status).
OrderStatus = Literal["OPEN", "CLOSED"]


class TossApiError(RuntimeError):
    def __init__(self, status: int, code: str | None, message: str | None, request_id: str | None):
        super().__init__(f"HTTP {status} {code}: {message} (requestId={request_id})")
        self.status = status
        self.code = code
        self.message = message
        self.request_id = request_id


def _parse_error(resp: httpx.Response) -> tuple[str | None, str | None, str | None, dict | None]:
    """Extract (code, message, requestId, data) from the common ErrorResponse envelope."""
    try:
        body = resp.json()
    except ValueError:
        return None, resp.text[:300], resp.headers.get("X-Request-Id"), None
    err = body.get("error") if isinstance(body, dict) else None
    if not isinstance(err, dict):
        return None, str(body)[:300], resp.headers.get("X-Request-Id"), None
    return err.get("code"), err.get("message"), err.get("requestId"), err.get("data")


@dataclass(frozen=True)
class OrderQuery:
    """Filter for GET /api/v1/orders.

    Per the spec, status=CLOSED is cursor-paginated (limit max 100) while status=OPEN returns
    everything and ignores limit/cursor, so those two params are only sent for CLOSED.
    """

    status: OrderStatus
    symbol: str | None = None
    from_date: str | None = None
    to_date: str | None = None
    limit: int = 100

    @property
    def paginated(self) -> bool:
        return self.status == "CLOSED"

    def params(self, cursor: str | None = None) -> dict:
        params: dict = {"status": self.status}
        if self.paginated:
            params["limit"] = self.limit
            if cursor:
                params["cursor"] = cursor
        if self.symbol:
            params["symbol"] = self.symbol
        if self.from_date:
            params["from"] = self.from_date
        if self.to_date:
            params["to"] = self.to_date
        return params


class TossClient:
    """Thin REST client handling the Bearer token, account header, and retries."""

    def __init__(self, *, base_url: str | None = None, http: httpx.Client | None = None, max_attempts: int = 8):
        self.base_url = (base_url or config.base_url()).rstrip("/")
        self.http = http or httpx.Client(timeout=30.0)
        self.max_attempts = max_attempts
        self._token = auth.get_access_token(client=self.http)

    def close(self) -> None:
        self.http.close()

    def __enter__(self) -> TossClient:
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    def request(self, method: str, path: str, *, params: dict | None = None, account_seq: int | None = None) -> dict:
        url = self.base_url + path
        reissued = False
        for attempt in range(1, self.max_attempts + 1):
            headers = {"Authorization": f"Bearer {self._token}", "Accept": "application/json"}
            if account_seq is not None:
                headers["X-Tossinvest-Account"] = str(account_seq)
            try:
                resp = self.http.request(method, url, params=params, headers=headers)
            except httpx.TransportError as e:
                # Network errors (connect/read timeouts etc.) retry with the same backoff as 5xx.
                if attempt >= self.max_attempts:
                    raise TossApiError(0, "transport-error", f"{type(e).__name__}: {e}", None) from e
                wait = min(60.0, 2.0**attempt)
                log.warning("Network error %s: %s. Waiting %.0fs (attempt %d)", type(e).__name__, e, wait, attempt)
                time.sleep(wait)
                continue

            if resp.status_code == 200:
                return resp.json()

            code, message, request_id, data = _parse_error(resp)

            if resp.status_code == 401:
                if code in REISSUE_CODES and not reissued:
                    if code == "token-revoked":
                        log.warning(
                            "Token was revoked by a re-issue from another process. Re-issuing will invalidate that one."
                        )
                    log.info("401 %s -> re-issuing token and retrying", code)
                    self._token = auth.issue_token(self.http)["access_token"]
                    reissued = True
                    continue
                raise TossApiError(401, code, message, request_id)

            if resp.status_code == 429:
                wait = float(resp.headers.get("Retry-After", "1"))
                log.warning("429 rate limit exceeded. Waiting %.1fs (attempt %d)", wait, attempt)
                time.sleep(wait)
                continue

            if 500 <= resp.status_code < 600:
                if attempt >= self.max_attempts:
                    raise TossApiError(resp.status_code, code, message, request_id)
                # Maintenance responses carry the wait time in data.retryAfterSeconds.
                hint = (data or {}).get("retryAfterSeconds") if isinstance(data, dict) else None
                wait = float(hint) if hint else min(60.0, 2.0**attempt)
                log.warning("%d %s: %s. Waiting %.0fs (attempt %d)", resp.status_code, code, message, wait, attempt)
                time.sleep(wait)
                continue

            raise TossApiError(resp.status_code, code, message, request_id)

        raise TossApiError(0, "retry-exhausted", f"Exceeded {self.max_attempts} retries: {method} {path}", None)

    # --- Endpoint wrappers -----------------------------------------------

    def list_accounts(self) -> list[dict]:
        return self.request("GET", "/api/v1/accounts")["result"]

    def get_orders_page(self, account_seq: int, query: OrderQuery, cursor: str | None = None) -> dict:
        return self.request("GET", "/api/v1/orders", params=query.params(cursor), account_seq=account_seq)["result"]
