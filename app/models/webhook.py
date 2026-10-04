from typing import Any

from pydantic import BaseModel


class WebhookPayload(BaseModel):
    object: str
    entry: list[dict[str, Any]] = []
