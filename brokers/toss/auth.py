"""Toss Securities Open API access token issuance and caching.

Constraints from the spec (agent-docs/toss/openapi.json, POST /oauth2/token):
- OAuth 2.0 Client Credentials Grant. Request body is application/x-www-form-urlencoded.
- No refresh token. Re-issue via the same endpoint when expired.
- Only one valid token per client. Re-issuing immediately invalidates the previous token,
  so multiple processes issuing independently would revoke each other -> share via a file cache.
- The token endpoint's error response uses the flat OAuth2 shape
  ({"error": "...", "error_description": "..."}), unlike every other API.

Usage:
    uv run toss-auth              # reuse the cache if valid, otherwise issue
    uv run toss-auth --status     # print cache status only (no network call)
    uv run toss-auth --force      # force re-issue (invalidates the existing token)
    uv run toss-auth --print      # print the token string to stdout (for curl etc.)

Settings: credentials come from .env (TOSS_CLIENT_ID, TOSS_CLIENT_SECRET);
base_url / token_cache path come from the [toss] section of config.toml.
"""

from __future__ import annotations

import argparse
import contextlib
import json
import logging
import os
import sys
import tempfile
import time
from datetime import UTC, datetime
from pathlib import Path

import httpx

from brokers.toss import config

__all__ = [
    "DEFAULT_EXPIRY_MARGIN",
    "TOKEN_PATH",
    "TossAuthError",
    "get_access_token",
    "invalidate_cache",
    "issue_token",
    "main",
]

log = logging.getLogger("toss.auth")

TOKEN_PATH = "/oauth2/token"
# Treat the token as expired this many seconds before actual expiry and re-issue early.
DEFAULT_EXPIRY_MARGIN = 300


class TossAuthError(RuntimeError):
    """Token issuance failed. The message carries the spec's error code and a hint."""


def _cache_path() -> Path:
    return config.token_cache_path()


def _credentials() -> tuple[str, str]:
    client_id, client_secret = config.credentials()
    if not client_id or not client_secret:
        raise TossAuthError(
            "TOSS_CLIENT_ID / TOSS_CLIENT_SECRET are not set. "
            f"Set them in {config.REPO_ROOT / '.env'} (see .env.example)."
        )
    return client_id, client_secret


def _read_cache() -> dict | None:
    path = _cache_path()
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text())
    except (OSError, ValueError) as e:
        log.warning("Ignoring unreadable token cache: %s", e)
        return None
    if not isinstance(data, dict) or "access_token" not in data or "expires_at" not in data:
        return None
    return data


def _write_cache(data: dict) -> None:
    """Write to a temp file, then swap in with os.replace (atomic), mode 0600."""
    path = _cache_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".tok-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f)
        os.chmod(tmp, 0o600)
        os.replace(tmp, path)
    except BaseException:
        with contextlib.suppress(OSError):
            os.unlink(tmp)
        raise


def _fmt_ts(epoch: float) -> str:
    return datetime.fromtimestamp(epoch, tz=UTC).astimezone().isoformat(timespec="seconds")


def _oauth_error_text(resp: httpx.Response) -> str:
    """Render the token endpoint's error body (flat OAuth2 shape) as a readable string."""
    try:
        body = resp.json()
    except ValueError:
        return resp.text[:300]
    if isinstance(body, dict):
        err = body.get("error")
        # Defensive: also handle the common envelope ({"error": {"code": ...}}) just in case
        if isinstance(err, dict):
            return f"{err.get('code')}: {err.get('message')}"
        desc = body.get("error_description")
        return f"{err}: {desc}" if desc else str(err)
    return str(body)[:300]


def issue_token(client: httpx.Client | None = None, *, max_retries: int = 3) -> dict:
    """Issue a new token via POST /oauth2/token and store it in the cache.

    Note: the previous token is invalidated as soon as this call succeeds.
    Returns: {"access_token", "token_type", "expires_in", "issued_at", "expires_at"}
    """
    client_id, client_secret = _credentials()
    url = config.base_url() + TOKEN_PATH
    form = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
    }
    own_client = client is None
    client = client or httpx.Client(timeout=15.0)
    try:
        for attempt in range(1, max_retries + 1):
            log.info("Requesting token (client_id=%s, attempt=%d)", client_id[:6] + "…", attempt)
            resp = client.post(url, data=form, headers={"Accept": "application/json"})
            if resp.status_code == 200:
                break
            if resp.status_code == 429:
                wait = float(resp.headers.get("Retry-After", "1"))
                log.warning("429 rate limit exceeded. Retrying in %.0fs", wait)
                time.sleep(wait)
                continue
            if resp.status_code == 401:
                raise TossAuthError(
                    f"Client authentication failed (401): {_oauth_error_text(resp)}. "
                    "Check client_id / client_secret and that the client is active."
                )
            if resp.status_code == 403:
                raise TossAuthError(
                    f"IP not allowed (403): {_oauth_error_text(resp)}. "
                    "Register the current IP under Toss Securities WTS Settings > Open API > Allowed IPs."
                )
            if resp.status_code == 400:
                raise TossAuthError(f"Bad request (400): {_oauth_error_text(resp)}")
            if 500 <= resp.status_code < 600 and attempt < max_retries:
                wait = 2.0 * attempt
                log.warning("%d server error. Retrying in %.0fs", resp.status_code, wait)
                time.sleep(wait)
                continue
            raise TossAuthError(f"Token issuance failed ({resp.status_code}): {_oauth_error_text(resp)}")
        else:
            raise TossAuthError(f"Token issuance exceeded {max_retries} retries")
    finally:
        if own_client:
            client.close()

    body = resp.json()
    now = time.time()
    token = {
        "access_token": body["access_token"],
        "token_type": body.get("token_type", "Bearer"),
        "expires_in": int(body["expires_in"]),
        "issued_at": now,
        "expires_at": now + int(body["expires_in"]),
    }
    _write_cache(token)
    log.info("Token issued. Expires: %s", _fmt_ts(token["expires_at"]))
    return token


def get_access_token(
    *,
    force: bool = False,
    margin: int = DEFAULT_EXPIRY_MARGIN,
    client: httpx.Client | None = None,
) -> str:
    """Return a valid access token string. Reuses the cache if valid, otherwise issues a new one."""
    if not force:
        cached = _read_cache()
        if cached and cached["expires_at"] - margin > time.time():
            return cached["access_token"]
    return issue_token(client)["access_token"]


def invalidate_cache() -> None:
    """Delete the cache file (the server-side token stays valid)."""
    with contextlib.suppress(FileNotFoundError):
        _cache_path().unlink()


def _print_status() -> int:
    cached = _read_cache()
    path = _cache_path()
    if not cached:
        print(f"No cache: {path}")
        return 1
    remaining = cached["expires_at"] - time.time()
    state = "valid" if remaining > DEFAULT_EXPIRY_MARGIN else ("expiring soon" if remaining > 0 else "expired")
    print(f"Cache file : {path}")
    print(f"Issued at  : {_fmt_ts(cached['issued_at'])}")
    print(f"Expires at : {_fmt_ts(cached['expires_at'])}")
    print(f"Remaining  : {int(remaining)}s ({state})")
    print(f"Token      : {cached['access_token'][:12]}… (length {len(cached['access_token'])})")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Issue/cache a Toss Securities Open API access token")
    parser.add_argument("--status", action="store_true", help="print cache status only (no network call)")
    parser.add_argument(
        "--force", action="store_true", help="ignore the cache and force re-issue (invalidates the previous token)"
    )
    parser.add_argument("--print", dest="print_token", action="store_true", help="print the token string to stdout")
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
        return _print_status()

    try:
        token = get_access_token(force=args.force)
    except TossAuthError as e:
        log.error("%s", e)
        return 2

    if args.print_token:
        print(token)
    else:
        _print_status()
    return 0


if __name__ == "__main__":
    sys.exit(main())
