"""KIS Open API REST client (live-trading domain).

Every call (agent-docs/kis/README.md):
- headers: authorization "Bearer <token>", appkey, appsecret, tr_id (one per API), custtype P,
  tr_cont ("" first page, "N" for the next one)
- body: {rt_cd: "0" = success, msg_cd, msg1, output...}; failures may come with HTTP 200 or 500,
  so rt_cd decides, not the status.
- continuation: the response header tr_cont is F/M when more pages exist. The next request
  sends header tr_cont=N and the response body's ctx_area_fk100/ctx_area_nk100 (or the 200
  variants) back as CTX_AREA_FK100/CTX_AREA_NK100. paged() does this.

Retries: a token error (EGW0012x) re-issues once; "초당 거래건수 초과" (EGW00201 personal,
EGW00215 ledger) waits and retries; 5xx without a KIS body and network errors back off.
Calls are spaced by MIN_INTERVAL so the per-app rate limit (portal: 20/s live, not in the
exported docs) is not approached.
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from collections.abc import Iterator
from dataclasses import dataclass

import httpx

from brokers.kis import auth, config
from brokers.kis.config import Account

__all__ = [
    "MIN_INTERVAL",
    "RATE_LIMIT_CODES",
    "TOKEN_CODES",
    "KisApiError",
    "KisClient",
    "KisResponse",
    "main",
]

log = logging.getLogger("kis.client")

MIN_INTERVAL = 0.1  # seconds between requests (10/s)
# EGW00215 is documented (inquire-balance.md); EGW00201 is the personal-quota variant from the portal.
RATE_LIMIT_CODES = {"EGW00201", "EGW00215"}
# Invalid / expired token, from the portal's error list (not in the exported docs): re-issue once.
TOKEN_CODES = {"EGW00121", "EGW00123"}


class KisApiError(RuntimeError):
    def __init__(self, status: int, msg_cd: str | None, msg1: str | None, tr_id: str | None):
        super().__init__(f"HTTP {status} {msg_cd}: {(msg1 or '').strip()} (tr_id={tr_id})")
        self.status = status
        self.msg_cd = msg_cd
        self.msg1 = (msg1 or "").strip()
        self.tr_id = tr_id


@dataclass(frozen=True)
class KisResponse:
    body: dict
    tr_cont: str  # response header: F/M = more pages, D/E = last

    @property
    def has_more(self) -> bool:
        return self.tr_cont in ("F", "M")


def _is_rate_limited(msg_cd: str | None, msg1: str | None) -> bool:
    return (msg_cd or "") in RATE_LIMIT_CODES or "초당 거래건수" in (msg1 or "")


def _is_token_error(msg_cd: str | None, msg1: str | None) -> bool:
    return (msg_cd or "") in TOKEN_CODES or "token" in (msg1 or "").lower()


class KisClient:
    def __init__(
        self,
        *,
        base_url: str | None = None,
        http: httpx.Client | None = None,
        max_attempts: int = 8,
        min_interval: float = MIN_INTERVAL,
    ):
        self.base_url = (base_url or config.base_url()).rstrip("/")
        self.http = http or httpx.Client(timeout=30.0)
        self.max_attempts = max_attempts
        self.min_interval = min_interval
        self._app_key, self._app_secret = auth.credentials()
        self._token = auth.get_access_token(client=self.http)
        self._last_call = 0.0

    def close(self) -> None:
        self.http.close()

    def __enter__(self) -> KisClient:
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    def _throttle(self) -> None:
        wait = self._last_call + self.min_interval - time.monotonic()
        if wait > 0:
            time.sleep(wait)
        self._last_call = time.monotonic()

    def request(
        self, method: str, path: str, *, tr_id: str, params: dict | None = None, tr_cont: str = ""
    ) -> KisResponse:
        url = self.base_url + path
        reissued = False
        for attempt in range(1, self.max_attempts + 1):
            headers = {
                "content-type": "application/json; charset=utf-8",
                "authorization": f"Bearer {self._token}",
                "appkey": self._app_key,
                "appsecret": self._app_secret,
                "tr_id": tr_id,
                "custtype": "P",
                "tr_cont": tr_cont,
            }
            self._throttle()
            try:
                resp = self.http.request(method, url, params=params, headers=headers)
            except httpx.TransportError as e:
                if attempt >= self.max_attempts:
                    raise KisApiError(0, "transport-error", f"{type(e).__name__}: {e}", tr_id) from e
                wait = min(60.0, 2.0**attempt)
                log.warning("Network error %s: %s. Waiting %.0fs (attempt %d)", type(e).__name__, e, wait, attempt)
                time.sleep(wait)
                continue

            try:
                body = resp.json()
            except ValueError:
                body = None
            if isinstance(body, dict) and body.get("rt_cd") == "0":
                return KisResponse(body, resp.headers.get("tr_cont", "").strip())

            msg_cd = body.get("msg_cd") if isinstance(body, dict) else None
            msg1 = body.get("msg1") if isinstance(body, dict) else resp.text[:300]

            if _is_rate_limited(msg_cd, msg1):  # before the token check: its message may mention the token
                if attempt >= self.max_attempts:
                    raise KisApiError(resp.status_code, msg_cd, msg1, tr_id)
                wait = min(10.0, 0.5 * attempt)
                log.warning("Rate limited (%s). Waiting %.1fs (attempt %d)", msg_cd, wait, attempt)
                time.sleep(wait)
                continue
            if _is_token_error(msg_cd, msg1) and not reissued:
                log.info("%s %s -> re-issuing token and retrying", resp.status_code, msg_cd)
                self._token = auth.issue_token(self.http)["access_token"]
                reissued = True
                continue
            if msg_cd is None and 500 <= resp.status_code < 600 and attempt < self.max_attempts:
                wait = min(60.0, 2.0**attempt)
                log.warning("%d without a KIS body. Waiting %.0fs (attempt %d)", resp.status_code, wait, attempt)
                time.sleep(wait)
                continue
            raise KisApiError(resp.status_code, msg_cd, msg1, tr_id)

        raise KisApiError(0, "retry-exhausted", f"Exceeded {self.max_attempts} retries: {method} {path}", tr_id)

    def paged(self, path: str, *, tr_id: str, params: dict, ctx: str = "100") -> Iterator[dict]:
        """GET every page of a continuation-keyed query, yielding each response body.

        `ctx` is the width KIS uses in the key names for this API: CTX_AREA_FK100/NK100 or
        the 200 variants (agent-docs/kis/<api>.md, Request Query Parameter).
        """
        fk, nk = f"CTX_AREA_FK{ctx}", f"CTX_AREA_NK{ctx}"
        params = {**params, fk: params.get(fk, ""), nk: params.get(nk, "")}
        tr_cont = ""
        seen: set[tuple[str, str]] = set()
        while True:
            resp = self.request("GET", path, tr_id=tr_id, params=params, tr_cont=tr_cont)
            yield resp.body
            if not resp.has_more:
                return
            body = {k.lower(): v for k, v in resp.body.items()}  # the docs show lowercase keys; be safe
            key = (str(body.get(fk.lower(), "")).strip(), str(body.get(nk.lower(), "")).strip())
            if key in seen or not any(key):
                log.warning("%s: continuation key repeated or empty although tr_cont=%s; stopping", tr_id, resp.tr_cont)
                return
            seen.add(key)
            params = {**params, fk: key[0], nk: key[1]}
            tr_cont = "N"

    # --- endpoints ---------------------------------------------------------

    def domestic_balance(self, account: Account) -> list[dict]:
        """주식잔고조회 TTTC8434R: every page's body. output1 = holdings (list); output2 = totals as a
        one-element list, dnca_tot_amt = 예수금."""
        cano, prdt = account
        params = {
            "CANO": cano,
            "ACNT_PRDT_CD": prdt,
            "AFHR_FLPR_YN": "N",
            "OFL_YN": "",
            "INQR_DVSN": "01",
            "UNPR_DVSN": "01",
            "FUND_STTL_ICLD_YN": "N",
            "FNCG_AMT_AUTO_RDPT_YN": "N",
            "PRCS_DVSN": "00",
        }
        return list(self.paged("/uapi/domestic-stock/v1/trading/inquire-balance", tr_id="TTTC8434R", params=params))

    def overseas_balance(self, account: Account, *, exchange: str = "NASD", currency: str = "USD") -> list[dict]:
        """해외주식 잔고 TTTS3012R. On the live domain NASD covers every US exchange. output1 = holdings
        (list); output2 = totals as a dict (no cash: that is CTRP6504R / TTTC2101R)."""
        cano, prdt = account
        params = {"CANO": cano, "ACNT_PRDT_CD": prdt, "OVRS_EXCG_CD": exchange, "TR_CRCY_CD": currency}
        return list(
            self.paged("/uapi/overseas-stock/v1/trading/inquire-balance", tr_id="TTTS3012R", params=params, ctx="200")
        )


# --- CLI: connectivity probe ---------------------------------------------------


def _probe(account: Account) -> int:
    with KisClient() as client:
        pages = client.domestic_balance(account)
        items = [r for p in pages for r in p.get("output1") or [] if r.get("hldg_qty", "0") not in ("", "0")]
        totals = (pages[-1].get("output2") or [{}])[0] if pages else {}
        cash = totals.get("dnca_tot_amt")
        print(f"Domestic (TTTC8434R): {len(pages)} page(s), {len(items)} holding(s), 예수금 {cash} KRW")
        for r in items[:5]:
            print(f"  {r.get('pdno')} {r.get('prdt_name')}: {r.get('hldg_qty')}")

        pages = client.overseas_balance(account)
        items = [r for p in pages for r in p.get("output1") or []]
        print(f"Overseas (TTTS3012R NASD/USD): {len(pages)} page(s), {len(items)} holding(s)")
        for r in items[:5]:
            print(f"  {r.get('ovrs_pdno')} {r.get('ovrs_item_name')}: {r.get('ovrs_cblc_qty')}")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="KIS API connectivity probe")
    p.add_argument("--probe", action="store_true", help="call the domestic and overseas balance APIs once")
    p.add_argument("--account", default=None, help="CANO-PRDT, default KIS_ACCOUNT from .env")
    p.add_argument("-v", "--verbose", action="store_true")
    args = p.parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        stream=sys.stderr,
    )
    if not args.verbose:
        logging.getLogger("httpx").setLevel(logging.WARNING)
    if not args.probe:
        p.print_help()
        return 0
    try:
        account = config.parse_account(args.account) if args.account else config.account()
        if account is None:
            log.error("KIS_ACCOUNT is not set in .env (or pass --account 12345678-01)")
            return 2
        return _probe(account)
    except (auth.KisAuthError, ValueError) as e:
        log.error("%s", e)
        return 2
    except KisApiError as e:
        log.error("API error: %s", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
