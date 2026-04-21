from __future__ import annotations

from anthropic import Anthropic


def call_anthropic(model_name: str, prompt: str) -> dict:
    client = Anthropic()

    response = client.messages.create(
        model=model_name,
        max_tokens=2000,
        messages=[
            {"role": "user", "content": prompt},
        ],
    )

    text_parts: list[str] = []
    for block in response.content:
        block_text = getattr(block, "text", None)
        if block_text:
            text_parts.append(block_text)

    raw_text = "\n".join(text_parts).strip()

    usage = getattr(response, "usage", None)
    input_tokens = getattr(usage, "input_tokens", 0) if usage else 0
    output_tokens = getattr(usage, "output_tokens", 0) if usage else 0

    response_id = getattr(response, "id", "") or ""

    return {
        "raw_text": raw_text,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "response_id": response_id,
    }