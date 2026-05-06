from __future__ import annotations

from typing import Any

from google import genai
from google.genai import types as genai_types

from src.config import GEMINI_API_KEY

_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set.")
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client


def call_gemini(model_name: str, prompt: str, temperature: float = 0.2) -> dict[str, Any]:
    client = _get_client()

    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config=genai_types.GenerateContentConfig(
            temperature=temperature,
        ),
    )

    raw_text = getattr(response, "text", "") or ""

    usage = getattr(response, "usage_metadata", None)
    input_tokens = getattr(usage, "prompt_token_count", 0) if usage else 0
    output_tokens = getattr(usage, "candidates_token_count", 0) if usage else 0

    response_id = getattr(response, "response_id", "") or ""

    return {
        "raw_text": raw_text,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "response_id": response_id,
    }
