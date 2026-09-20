"""Send a job notification to a Discord or Slack incoming webhook (NOTIFY_WEBHOOK_URL in .env)."""

from __future__ import annotations

import logging

import httpx

from brokers.toss import config

__all__ = ["DISCORD_LIMIT", "send"]

log = logging.getLogger("jobs.notify")

DISCORD_LIMIT = 2000  # characters per message


def send(text: str, *, url: str | None = None) -> bool:
    """Post `text`. Returns False (after logging) when no webhook is configured or the post fails."""
    url = url or config.notify_webhook_url()
    if not url:
        log.warning("NOTIFY_WEBHOOK_URL is not set; notification not sent:\n%s", text)
        return False
    if "discord.com/api/webhooks" in url or "discordapp.com/api/webhooks" in url:
        payload = {"content": text[: DISCORD_LIMIT - 10] + ("\n…" if len(text) > DISCORD_LIMIT - 10 else "")}
    else:
        payload = {"text": text}
    try:
        resp = httpx.post(url, json=payload, timeout=15.0)
        resp.raise_for_status()
    except httpx.HTTPError as e:
        log.error("Notification failed: %s", e)
        return False
    return True
