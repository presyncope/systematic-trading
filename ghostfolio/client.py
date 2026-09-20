"""Minimal Ghostfolio REST client (self-hosted instance, see deploy/ghostfolio).

Auth: the security token shown once at "Get Started" is exchanged for a JWT via
POST /api/v1/auth/anonymous; every other call sends it as a Bearer token.
Endpoints used (3.71.0): GET /api/v1/account, POST /api/v1/account-balance.
"""

from __future__ import annotations

import logging
from datetime import date, datetime, time
from decimal import Decimal

import httpx

__all__ = ["GhostfolioClient", "GhostfolioError"]

log = logging.getLogger("ghostfolio.client")


class GhostfolioError(RuntimeError):
    pass


class GhostfolioClient:
    def __init__(self, base_url: str, access_token: str, *, http: httpx.Client | None = None):
        self.base_url = base_url.rstrip("/")
        self.http = http or httpx.Client(timeout=30.0)
        self._jwt = self._login(access_token)

    def close(self) -> None:
        self.http.close()

    def __enter__(self) -> GhostfolioClient:
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    def _login(self, access_token: str) -> str:
        resp = self.http.post(f"{self.base_url}/api/v1/auth/anonymous", json={"accessToken": access_token})
        if resp.status_code != 200:
            raise GhostfolioError(f"Ghostfolio login failed ({resp.status_code}): check GHOSTFOLIO_ACCESS_TOKEN")
        return resp.json()["authToken"]

    def _request(self, method: str, path: str, **kwargs) -> dict:
        resp = self.http.request(
            method, f"{self.base_url}{path}", headers={"Authorization": f"Bearer {self._jwt}"}, **kwargs
        )
        if resp.status_code >= 400:
            raise GhostfolioError(f"{method} {path} -> {resp.status_code}: {resp.text[:300]}")
        return resp.json()

    def accounts(self) -> list[dict]:
        return self._request("GET", "/api/v1/account").get("accounts") or []

    def account_by_name(self, name: str) -> dict | None:
        return next((a for a in self.accounts() if a.get("name", "").lower() == name.lower()), None)

    def set_cash_balance(self, account_id: str, balance: Decimal, on: date) -> dict:
        """Create or replace the account's cash balance entry for the given day."""
        stamp = datetime.combine(on, time(0)).isoformat(timespec="milliseconds") + "Z"
        return self._request(
            "POST",
            "/api/v1/account-balance",
            json={"accountId": account_id, "balance": float(balance), "date": stamp},
        )
