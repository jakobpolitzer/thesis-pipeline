from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

from google import genai
from google.genai import types as genai_types
from openai import OpenAI


def _gemini_api_key() -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is missing in environment.")
    return api_key


def _openai_client() -> OpenAI:
    return OpenAI(
        api_key=_gemini_api_key(),
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )


def _genai_client() -> genai.Client:
    return genai.Client(api_key=_gemini_api_key())


def upload_batch_input(jsonl_path: Path, display_name: str) -> str:
    client = _genai_client()
    uploaded = client.files.upload(
        file=str(jsonl_path),
        config=genai_types.UploadFileConfig(
            display_name=display_name,
            mime_type="application/jsonl",
        ),
    )
    return uploaded.name


def create_batch(input_file_id: str) -> dict[str, Any]:
    client = _openai_client()
    batch = client.batches.create(
        input_file_id=input_file_id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
    )
    return batch.model_dump() if hasattr(batch, "model_dump") else dict(batch)


def wait_for_batch(
    batch_name: str,
    poll_seconds: int = 30,
    max_attempts: int | None = None,
) -> dict[str, Any]:
    client = _genai_client()

    completed_states = {
        "JOB_STATE_SUCCEEDED",
        "JOB_STATE_FAILED",
        "JOB_STATE_CANCELLED",
        "JOB_STATE_EXPIRED",
    }

    attempt = 0

    while True:
        attempt += 1
        batch_job = client.batches.get(name=batch_name)
        state = getattr(getattr(batch_job, "state", None), "name", None) or str(
            getattr(batch_job, "state", "")
        )

        print(f"[BATCH POLL] {batch_name} -> {state}")

        if state in completed_states:
            return {
                "name": getattr(batch_job, "name", ""),
                "state": state,
                "dest_file_name": getattr(getattr(batch_job, "dest", None), "file_name", None),
                "raw": batch_job,
            }

        if max_attempts is not None and attempt >= max_attempts:
            raise TimeoutError(
                f"Gemini batch did not finish after {max_attempts} polling attempts. "
                f"Last state: {state}"
            )

        time.sleep(poll_seconds)


def download_batch_output(output_file_id: str, output_path: Path) -> None:
    client = _genai_client()
    content = client.files.download(file=output_file_id)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    if isinstance(content, bytes):
        output_path.write_bytes(content)
    elif isinstance(content, str):
        output_path.write_text(content, encoding="utf-8")
    else:
        output_path.write_bytes(bytes(content))


def parse_batch_output(output_path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    with output_path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            rows.append(json.loads(line))

    return rows