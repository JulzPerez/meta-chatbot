import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


async def send_text(client: httpx.AsyncClient, recipient_id: str, text: str) -> None:
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text},
        "messaging_type": "RESPONSE",
    }
    resp = await client.post(
        f"{settings.graph_api_url}/me/messages",
        json=payload,
        params={"access_token": settings.page_access_token},
    )
    if resp.status_code != 200:
        logger.error("send_text failed: %s %s", resp.status_code, resp.text)


async def handle_messenger(
    client: httpx.AsyncClient, platform: str, entry: dict
) -> None:
    try:
        messaging = entry["messaging"][0]
        sender_id: str = messaging["sender"]["id"]
        text: str = messaging["message"]["text"]
    except (KeyError, IndexError, TypeError):
        return

    logger.info("[%s] sender=%s text=%r", platform, sender_id, text)
    await send_text(client, sender_id, f"You said: {text}")
