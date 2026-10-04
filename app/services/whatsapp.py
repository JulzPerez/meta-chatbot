import logging

import httpx

from app.config import settings
from app.services.ai import get_ai_response

logger = logging.getLogger(__name__)


async def send_text(
    client: httpx.AsyncClient, phone_number_id: str, to: str, text: str
) -> None:
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "text",
        "text": {"body": text},
    }
    resp = await client.post(
        f"{settings.graph_api_url}/{phone_number_id}/messages",
        json=payload,
        params={"access_token": settings.page_access_token},
    )
    if resp.status_code != 200:
        logger.error("send_text failed: %s %s", resp.status_code, resp.text)


async def handle_whatsapp(client: httpx.AsyncClient, entry: dict) -> None:
    try:
        change = entry["changes"][0]["value"]
        msg = change["messages"][0]
        phone: str = msg["from"]
        text: str = msg["text"]["body"]
        phone_number_id: str = change["metadata"]["phone_number_id"]
    except (KeyError, IndexError, TypeError):
        return

    logger.info("[whatsapp] from=%s text=%r", phone, text)
    reply = await get_ai_response(user_id=f"wa:{phone}", user_message=text)
    await send_text(client, phone_number_id, phone, reply)
