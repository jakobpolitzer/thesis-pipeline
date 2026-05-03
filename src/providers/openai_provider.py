from __future__ import annotations

from typing import Any

from openai import OpenAI

from src.config import OPENAI_API_KEY

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set.")
        _client = OpenAI(api_key=OPENAI_API_KEY)
    return _client


def call_openai(model_name: str, prompt: str, temperature: float = 0.2) -> dict[str, Any]:
    client = _get_client()
    response = client.responses.create(
        model=model_name,
        input=prompt,
        temperature=temperature,
    )

    usage = getattr(response, "usage", None)
    input_tokens = getattr(usage, "input_tokens", 0) if usage else 0
    output_tokens = getattr(usage, "output_tokens", 0) if usage else 0

    raw_text = getattr(response, "output_text", "") or ""
    response_id = getattr(response, "id", "") or ""

    return {
        "raw_text": raw_text,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "response_id": response_id,
    }
