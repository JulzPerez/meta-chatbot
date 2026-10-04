import hashlib
import hmac
import json

from fastapi.testclient import TestClient

APP_SECRET = "test_secret"
VERIFY_TOKEN = "test_token"


def _sign(body: bytes) -> str:
    return "sha256=" + hmac.new(APP_SECRET.encode(), body, hashlib.sha256).hexdigest()


def test_health(client: TestClient):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_verify_webhook_success(client: TestClient):
    resp = client.get(
        "/webhook",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": VERIFY_TOKEN,
            "hub.challenge": "abc123",
        },
    )
    assert resp.status_code == 200
    assert resp.text == "abc123"


def test_verify_webhook_wrong_token(client: TestClient):
    resp = client.get(
        "/webhook",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "wrong_token",
            "hub.challenge": "abc123",
        },
    )
    assert resp.status_code == 403


def test_receive_webhook_bad_signature(client: TestClient):
    body = json.dumps({"object": "page", "entry": []}).encode()
    resp = client.post(
        "/webhook",
        content=body,
        headers={
            "X-Hub-Signature-256": "sha256=invalidsig",
            "Content-Type": "application/json",
        },
    )
    assert resp.status_code == 401


def test_receive_webhook_valid_page(client: TestClient):
    body = json.dumps({"object": "page", "entry": []}).encode()
    resp = client.post(
        "/webhook",
        content=body,
        headers={
            "X-Hub-Signature-256": _sign(body),
            "Content-Type": "application/json",
        },
    )
    assert resp.status_code == 200
