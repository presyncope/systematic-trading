"""Access-token cache file shared by the broker auth modules.

One JSON file per broker (mode 0600, written atomically) so that every process of this repo
reuses the same token: brokers invalidate or rate-limit re-issuance, so independent
issuance per process is not an option.

Layout: {"access_token", "token_type", "expires_in", "issued_at", "expires_at"} (epoch seconds).
"""

from __future__ import annotations

import contextlib
import json
import logging
import os
import tempfile
import time
from datetime import UTC, datetime
from pathlib import Path

__all__ = ["DEFAULT_EXPIRY_MARGIN", "TokenCache", "fmt_ts"]

log = logging.getLogger("common.tokencache")

# Treat the token as expired this many seconds before actual expiry and re-issue early.
DEFAULT_EXPIRY_MARGIN = 300


def fmt_ts(epoch: float) -> str:
    return datetime.fromtimestamp(epoch, tz=UTC).astimezone().isoformat(timespec="seconds")


class TokenCache:
    def __init__(self, path: Path):
        self.path = path

    def read(self) -> dict | None:
        if not self.path.exists():
            return None
        try:
            data = json.loads(self.path.read_text())
        except (OSError, ValueError) as e:
            log.warning("Ignoring unreadable token cache: %s", e)
            return None
        if not isinstance(data, dict) or "access_token" not in data or "expires_at" not in data:
            return None
        return data

    def valid(self, margin: int = DEFAULT_EXPIRY_MARGIN) -> dict | None:
        """The cached token if it is still good for at least `margin` seconds."""
        cached = self.read()
        if cached and cached["expires_at"] - margin > time.time():
            return cached
        return None

    def write(self, data: dict) -> None:
        """Write to a temp file, then swap in with os.replace (atomic), mode 0600."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=self.path.parent, prefix=".tok-", suffix=".tmp")
        try:
            with os.fdopen(fd, "w") as f:
                json.dump(data, f)
            os.chmod(tmp, 0o600)
            os.replace(tmp, self.path)
        except BaseException:
            with contextlib.suppress(OSError):
                os.unlink(tmp)
            raise

    def clear(self) -> None:
        """Delete the cache file (the server-side token stays valid)."""
        with contextlib.suppress(FileNotFoundError):
            self.path.unlink()

    def print_status(self) -> int:
        cached = self.read()
        if not cached:
            print(f"No cache: {self.path}")
            return 1
        remaining = cached["expires_at"] - time.time()
        state = "valid" if remaining > DEFAULT_EXPIRY_MARGIN else ("expiring soon" if remaining > 0 else "expired")
        print(f"Cache file : {self.path}")
        print(f"Issued at  : {fmt_ts(cached['issued_at'])}")
        print(f"Expires at : {fmt_ts(cached['expires_at'])}")
        print(f"Remaining  : {int(remaining)}s ({state})")
        print(f"Token      : {cached['access_token'][:12]}… (length {len(cached['access_token'])})")
        return 0
