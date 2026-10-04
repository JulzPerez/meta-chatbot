import hashlib
import hmac
import logging

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse, Response
from pydantic import ValidationError

from app.config import settings
from app.models.webhook import WebhookPayload
from app.services.messenger import handle_messenger
from app.services.whatsapp import handle_whatsapp

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.get("/webhook", response_class=PlainTextResponse)
async def verify_webhook(
    hub_mode: str | None = Query(None, alias="hub.mode"),
    hub_verify_token: str | None = Query(None, alias="hub.verify_token"),
    hub_challenge: str | None = Query(None, alias="hub.challenge"),
):
    if not all([hub_mode, hub_verify_token, hub_challenge]):
        raise HTTPException(status_code=400, detail="Missing required parameters")
    if hub_mode == "subscribe" and hub_verify_token == settings.meta_verify_token:
        return hub_challenge
    raise HTTPException(status_code=403, detail="Forbidden")


@router.post("/webhook")
async def receive_webhook(request: Request, background_tasks: BackgroundTasks):
    body = await request.body()

    sig_header = request.headers.get("X-Hub-Signature-256", "")
    expected = "sha256=" + hmac.new(
        settings.meta_app_secret.encode(), body, hashlib.sha256
    ).hexdigest()
    if not hmac.compare_digest(expected, sig_header):
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        payload = WebhookPayload.model_validate_json(body)
    except (ValueError, ValidationError):
        raise HTTPException(status_code=400, detail="Invalid payload")

    client = request.app.state.http

    for entry in payload.entry:
        if payload.object == "whatsapp_business_account":
            background_tasks.add_task(handle_whatsapp, client, entry)
        elif payload.object in ("page", "instagram"):
            background_tasks.add_task(handle_messenger, client, payload.object, entry)
        else:
            logger.warning("Unknown object type: %s", payload.object)

    return Response(status_code=200)
