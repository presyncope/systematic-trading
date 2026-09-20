"""KIS Open API access token issuance and caching.

From the docs (agent-docs/kis/oauth/tokenP.md):
- POST /oauth2/tokenP, JSON body {grant_type: client_credentials, appkey, appsecret}.
- A token is valid for 24 hours. Calling the endpoint again within 6 hours returns the same
  token, and calling it too often is rejected ("잠시 후 다시 시도", EGW00133), so the token is
  cached in a file (config: [kis] token_cache) and reused until shortly before it expires.
- The response's access_token_token_expired ("YYYY-MM-DD HH:MM:SS", KST) is the expiry used
  for the cache; expires_in is the fallback.
- POST /oauth2/revokeP {appkey, appsecret, token} discards a token early.
- Errors come back as {"error_code": ..., "error_description": ...}.

Usage:
    uv run kis-auth              # reuse the cache if valid, otherwise issue
    uv run kis-auth --status     # print cache status only (no network call)
    uv run kis-auth --force      # issue again (within 6 hours this returns the same token)
    uv run kis-auth --print      # print the token string to stdout (for curl etc.)
    uv run kis-auth --revoke     # revoke the cached token and delete the cache
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from datetime import datetime
from zoneinfo import ZoneInfo

import httpx

from brokers.common.config import REPO_ROOT
from brokers.common.tokencache import DEFAULT_EXPIRY_MARGIN, TokenCache, fmt_ts
from brokers.kis import config

__all__ = [
    "KST",
    "REVOKE_PATH",
    "TOKEN_PATH",
    "KisAuthError",
    "credentials",
    "get_access_token",
    "invalidate_cache",
    "issue_token",
    "main",
    "revoke_token",
]

log = logging.getLogger("kis.auth")

TOKEN_PATH = "/oauth2/tokenP"
REVOKE_PATH = "/oauth2/revokeP"
KST = ZoneInfo("Asia/Seoul")


class KisAuthError(RuntimeError):
    """Token issuance failed. The message carries KIS's error code and a hint."""


def _cache() -> TokenCache:
    return TokenCache(config.token_cache_path())


def credentials() -> tuple[str, str]:
    app_key, app_secret = config.credentials()
    if not app_key or not app_secret:
        raise KisAuthError(
            f"KIS_APP_KEY / KIS_APP_SECRET are not set. Set them in {REPO_ROOT / '.env'} (see .env.example)."
        )
    return app_key, app_secret


def _error_text(resp: httpx.Response) -> str:
    try:
        body = resp.json()
    except ValueError:
        return resp.text[:300]
    if isinstance(body, dict):
        code = body.get("error_code") or body.get("msg_cd") or body.get("rt_cd")
        desc = body.get("error_description") or body.get("msg1") or body.get("message")
        return f"{code}: {desc}" if code else str(desc or body)[:300]
    return str(body)[:300]


def _expires_at(body: dict, issued_at: float) -> float:
    stamp = body.get("access_token_token_expired")
    if stamp:
        try:
            return datetime.strptime(stamp, "%Y-%m-%d %H:%M:%S").replace(tzinfo=KST).timestamp()
        except ValueError:
            log.warning("Unexpected access_token_token_expired %r; using expires_in", stamp)
    return issued_at + int(body.get("expires_in", 86400))


def issue_token(client: httpx.Client | None = None, *, max_retries: int = 3) -> dict:
    """POST /oauth2/tokenP and store the result in the cache.

    Returns: {"access_token", "token_type", "expires_in", "issued_at", "expires_at"}
    """
    app_key, app_secret = credentials()
    url = config.base_url() + TOKEN_PATH
    body = {"grant_type": "client_credentials", "appkey": app_key, "appsecret": app_secret}
    own_client = client is None
    client = client or httpx.Client(timeout=15.0)
    try:
        for attempt in range(1, max_retries + 1):
            log.info("Requesting token (appkey=%s…, attempt=%d)", app_key[:4], attempt)
            resp = client.post(url, json=body, headers={"content-type": "application/json; charset=utf-8"})
            if resp.status_code == 200:
                break
            if resp.status_code in (401, 403):
                raise KisAuthError(
                    f"Token request rejected ({resp.status_code}): {_error_text(resp)}. "
                    "Check KIS_APP_KEY / KIS_APP_SECRET (live-trading keys) or wait a minute if the last "
                    "request was recent."
                )
            if 500 <= resp.status_code < 600 and attempt < max_retries:
                wait = 2.0 * attempt
                log.warning("%d server error. Retrying in %.0fs", resp.status_code, wait)
                time.sleep(wait)
                continue
            raise KisAuthError(f"Token issuance failed ({resp.status_code}): {_error_text(resp)}")
        else:
            raise KisAuthError(f"Token issuance exceeded {max_retries} retries")
    finally:
        if own_client:
            client.close()

    data = resp.json()
    if "access_token" not in data:
        raise KisAuthError(f"Token response has no access_token: {_error_text(resp)}")
    now = time.time()
    token = {
        "access_token": data["access_token"],
        "token_type": data.get("token_type", "Bearer"),
        "expires_in": int(data.get("expires_in", 86400)),
        "issued_at": now,
        "expires_at": _expires_at(data, now),
    }
    _cache().write(token)
    log.info("Token issued. Expires: %s", fmt_ts(token["expires_at"]))
    return token


def get_access_token(
    *,
    force: bool = False,
    margin: int = DEFAULT_EXPIRY_MARGIN,
    client: httpx.Client | None = None,
) -> str:
    """Return a valid access token string. Reuses the cache if valid, otherwise issues a new one."""
    if not force:
        cached = _cache().valid(margin)
        if cached:
            return cached["access_token"]
    return issue_token(client)["access_token"]


def revoke_token(client: httpx.Client | None = None) -> bool:
    """POST /oauth2/revokeP for the cached token, then delete the cache. False if nothing was cached."""
    cached = _cache().read()
    if not cached:
        return False
    app_key, app_secret = credentials()
    own_client = client is None
    client = client or httpx.Client(timeout=15.0)
    try:
        resp = client.post(
            config.base_url() + REVOKE_PATH,
            json={"appkey": app_key, "appsecret": app_secret, "token": cached["access_token"]},
            headers={"content-type": "application/json; charset=utf-8"},
        )
    finally:
        if own_client:
            client.close()
    if resp.status_code != 200:
        raise KisAuthError(f"Token revocation failed ({resp.status_code}): {_error_text(resp)}")
    _cache().clear()
    log.info("Token revoked and cache removed")
    return True


def invalidate_cache() -> None:
    """Delete the cache file (the server-side token stays valid)."""
    _cache().clear()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Issue/cache a KIS Open API access token")
    parser.add_argument("--status", action="store_true", help="print cache status only (no network call)")
    parser.add_argument("--force", action="store_true", help="ignore the cache and request a token again")
    parser.add_argument("--print", dest="print_token", action="store_true", help="print the token string to stdout")
    parser.add_argument("--revoke", action="store_true", help="revoke the cached token and delete the cache")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        stream=sys.stderr,
    )
    if not args.verbose:
        logging.getLogger("httpx").setLevel(logging.WARNING)

    if args.status:
        return _cache().print_status()

    try:
        if args.revoke:
            print("revoked" if revoke_token() else "no cached token")
            return 0
        token = get_access_token(force=args.force)
    except KisAuthError as e:
        log.error("%s", e)
        return 2

    if args.print_token:
        print(token)
    else:
        _cache().print_status()
    return 0


if __name__ == "__main__":
    sys.exit(main())
