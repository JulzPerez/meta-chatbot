from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI

from app.routers.webhook import router as webhook_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http = httpx.AsyncClient(timeout=10.0)
    yield
    await app.state.http.aclose()


def create_app() -> FastAPI:
    app = FastAPI(title="Meta Chatbot", lifespan=lifespan)
    app.include_router(webhook_router)
    return app
