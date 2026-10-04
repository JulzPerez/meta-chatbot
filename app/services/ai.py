import logging
from collections import defaultdict

from app.config import settings

logger = logging.getLogger(__name__)

# Per-user conversation history stored as OpenAI-style dicts: {"role": ..., "content": ...}
_history: dict[str, list[dict]] = defaultdict(list)
MAX_HISTORY_MESSAGES = 20


def _append_and_trim(user_id: str, role: str, content: str) -> None:
    _history[user_id].append({"role": role, "content": content})
    if len(_history[user_id]) > MAX_HISTORY_MESSAGES:
        _history[user_id] = _history[user_id][-MAX_HISTORY_MESSAGES:]


async def get_ai_response(user_id: str, user_message: str) -> str:
    _append_and_trim(user_id, "user", user_message)

    provider = settings.ai_provider.lower()
    try:
        if provider == "claude":
            reply = await _call_claude(user_id)
        elif provider == "openai":
            reply = await _call_openai(user_id)
        elif provider == "gemini":
            reply = await _call_gemini(user_id)
        else:
            raise ValueError(f"Unknown AI_PROVIDER: {provider!r}. Use 'claude', 'openai', or 'gemini'.")

        _append_and_trim(user_id, "assistant", reply)
        return reply
    except Exception as exc:
        logger.error("AI call failed for provider=%s user=%s: %s", provider, user_id, exc)
        # Roll back the user message so the failed turn isn't stuck in history
        _history[user_id].pop()
        return "Sorry, I ran into an issue processing your message. Please try again."


async def _call_claude(user_id: str) -> str:
    import anthropic

    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    response = await client.messages.create(
        model=settings.ai_model or "claude-sonnet-4-6",
        max_tokens=1024,
        system=settings.ai_system_prompt,
        messages=_history[user_id],
    )
    return response.content[0].text


async def _call_openai(user_id: str) -> str:
    import openai

    client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
    messages = [{"role": "system", "content": settings.ai_system_prompt}] + _history[user_id]
    response = await client.chat.completions.create(
        model=settings.ai_model or "gpt-4o",
        messages=messages,
        max_tokens=1024,
    )
    return response.choices[0].message.content


async def _call_gemini(user_id: str) -> str:
    import google.generativeai as genai

    genai.configure(api_key=settings.gemini_api_key)
    model = genai.GenerativeModel(
        model_name=settings.ai_model or "gemini-2.0-flash",
        system_instruction=settings.ai_system_prompt,
    )

    messages = _history[user_id]
    # Pass all prior turns as history; send only the latest user message
    prior = messages[:-1]
    current_text = messages[-1]["content"]

    gemini_history = [
        {
            "role": "user" if msg["role"] == "user" else "model",
            "parts": [{"text": msg["content"]}],
        }
        for msg in prior
    ]

    chat = model.start_chat(history=gemini_history)
    response = await chat.send_message_async(current_text)
    return response.text
