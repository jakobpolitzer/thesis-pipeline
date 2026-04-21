from __future__ import annotations

from google import genai


def call_gemini(model_name: str, prompt: str) -> dict:
    client = genai.Client()

    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
    )

    raw_text = response.text or ""

    usage = getattr(response, "usage_metadata", None)
    input_tokens = 0
    output_tokens = 0

    if usage is not None:
        input_tokens = getattr(usage, "prompt_token_count", 0) or 0
        output_tokens = getattr(usage, "candidates_token_count", 0) or 0

    response_id = getattr(response, "response_id", "") or ""

    return {
        "raw_text": raw_text,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "response_id": response_id,
    }