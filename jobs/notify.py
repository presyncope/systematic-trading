"""Send a job notification to every configured channel.

- Telegram: TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID in .env (bot from @BotFather; the chat id is
  whatever chat you messaged the bot from, `daily-sync --notify-test` prints it).
- Discord or Slack incoming webhook: NOTIFY_WEBHOOK_URL in .env.
"""

from __future__ import annotations

import logging
import re

import httpx

from brokers.common import config

__all__ = ["DISCORD_LIMIT", "TELEGRAM_LIMIT", "RedactSecrets", "install_log_redaction", "send", "telegram_chat_ids"]

log = logging.getLogger("jobs.notify")

DISCORD_LIMIT = 2000  # characters per message
TELEGRAM_LIMIT = 4096
TELEGRAM_API = "https://api.telegram.org"

# The Telegram bot token is part of the request URL, and httpx logs every URL at INFO.
_BOT_TOKEN = re.compile(r"/bot\d+:[A-Za-z0-9_-]+")


class RedactSecrets(logging.Filter):
    """Mask the bot token and the webhook URL in every log line that passes a handler."""

    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        redacted = _BOT_TOKEN.sub("/bot<redacted>", message)
        webhook = config.notify_webhook_url()
        if webhook:
            redacted = redacted.replace(webhook, "<webhook redacted>")
        if redacted != message:
            record.msg, record.args = redacted, None
        return True


def install_log_redaction() -> None:
    """Attach RedactSecrets to the root handlers; call after logging is configured."""
    for handler in logging.getLogger().handlers:
        if not any(isinstance(f, RedactSecrets) for f in handler.filters):
            handler.addFilter(RedactSecrets())


def _clip(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[: limit - 2] + "\n…"


def _send_webhook(url: str, text: str) -> bool:
    if "discord.com/api/webhooks" in url or "discordapp.com/api/webhooks" in url:
        payload = {"content": _clip(text, DISCORD_LIMIT)}
    else:
        payload = {"text": text}
    try:
        httpx.post(url, json=payload, timeout=15.0).raise_for_status()
    except httpx.HTTPError as e:
        log.error("Webhook notification failed: %s", e)
        return False
    return True


def _send_telegram(token: str, chat_id: str, text: str) -> bool:
    try:
        resp = httpx.post(
            f"{TELEGRAM_API}/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": _clip(text, TELEGRAM_LIMIT), "disable_web_page_preview": True},
            timeout=15.0,
        )
        body = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}
        if resp.status_code >= 400 or not body.get("ok", False):
            log.error(
                "Telegram notification failed (%s): %s", resp.status_code, body.get("description", resp.text[:200])
            )
            return False
    except httpx.HTTPError as e:
        log.error("Telegram notification failed: %s", e)
        return False
    return True


def telegram_chat_ids(token: str) -> list[tuple[str, str]]:
    """(chat id, who) for every chat that has messaged the bot recently (getUpdates)."""
    resp = httpx.get(f"{TELEGRAM_API}/bot{token}/getUpdates", timeout=15.0)
    resp.raise_for_status()
    seen: dict[str, str] = {}
    for update in resp.json().get("result", []):
        msg = update.get("message") or update.get("edited_message") or update.get("channel_post") or {}
        chat = msg.get("chat") or {}
        if "id" in chat:
            who = (
                chat.get("username")
                or chat.get("title")
                or " ".join(p for p in (chat.get("first_name"), chat.get("last_name")) if p)
            )
            seen[str(chat["id"])] = f"{chat.get('type', '')} {who}".strip()
    return list(seen.items())


def send(text: str) -> bool:
    """Post `text` to Telegram and/or the webhook, whichever is configured. False if none is, or all fail."""
    token, chat_id = config.telegram_credentials()
    url = config.notify_webhook_url()
    if not (token and chat_id) and not url:
        log.warning("No notification channel configured (TELEGRAM_* or NOTIFY_WEBHOOK_URL); not sent:\n%s", text)
        return False
    sent = False
    if token and chat_id:
        sent = _send_telegram(token, chat_id, text) or sent
    elif token:
        log.warning("TELEGRAM_CHAT_ID is not set; run `daily-sync --notify-test` to find it")
    if url:
        sent = _send_webhook(url, text) or sent
    return sent
