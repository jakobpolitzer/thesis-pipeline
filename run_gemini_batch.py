from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from src.config import (
    BATCH_INPUT_DIR,
    BATCH_OUTPUT_DIR,
    CODE_DIR,
    ENABLE_SONAR,
    GEMINI_API_KEY,
    MBPP_FILE,
    RAW_DIR,
    RESULTS_DIR,
    SONAR_DIR,
    SONAR_HOST_URL,
    SONAR_TOKEN,
)
from src.mbpp_loader import filter_tasks, load_mbpp_tasks
from src.pipeline_core import extract_function_signature, process_single_response
from src.prompts import build_prompt
from src.providers.gemini_batch_provider import (
    create_batch,
    download_batch_output,
    parse_batch_output,
    upload_batch_input,
    wait_for_batch,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-task-id", type=int, default=11)
    parser.add_argument("--max-task-id", type=int, default=510)
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--poll-seconds", type=int, default=30)
    args = parser.parse_args()

    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is missing in environment.")

    tasks = load_mbpp_tasks(MBPP_FILE)
    tasks = filter_tasks(
        tasks,
        min_id=args.min_task_id,
        max_id=args.max_task_id,
        limit=args.limit,
    )

    run_id = datetime.now(timezone.utc).strftime("gemini_batch_%Y%m%dT%H%M%SZ")
    model_name = "gemini-2.5-pro"
    provider_name = "gemini"

    task_lookup: dict[str, dict] = {}
    jsonl_path = BATCH_INPUT_DIR / f"{run_id}.jsonl"

    with jsonl_path.open("w", encoding="utf-8") as f:
        for task in tasks:
            task_id = int(task["task_id"])
            task_text = str(task["text"])
            reference_code = str(task.get("code", "") or "")
            function_signature = extract_function_signature(reference_code)

            for prompt_type in ["standard", "readability"]:
                prompt = build_prompt(task_text, prompt_type, function_signature)
                custom_id = f"task_{task_id}_{prompt_type}"

                task_lookup[custom_id] = {
                    "task": task,
                    "prompt_type": prompt_type,
                }

                line = {
                    "custom_id": custom_id,
                    "method": "POST",
                    "url": "/v1/chat/completions",
                    "body": {
                        "model": model_name,
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                    },
                }
                f.write(json.dumps(line, ensure_ascii=False) + "\n")

    input_file_id = upload_batch_input(jsonl_path, display_name=run_id)
    batch = create_batch(input_file_id)

    # OpenAI-compat returns id; native Gemini polling expects resource name batches/<id>
    batch_id = batch["id"]
    batch_name = batch_id if str(batch_id).startswith("batches/") else f"batches/{batch_id}"
    
    print(f"Input file uploaded: {input_file_id}")
    print(f"Batch created: batch_id={batch_id}, batch_name={batch_name}")

    meta_path = BATCH_OUTPUT_DIR / f"{run_id}_batch_meta.json"
    meta_path.write_text(
        json.dumps(
            {
                "run_id": run_id,
                "input_file_id": input_file_id,
                "batch_id": batch_id,
                "batch_name": batch_name,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"Batch metadata written to: {meta_path}")

    final_batch = wait_for_batch(batch_name, poll_seconds=args.poll_seconds)
    if final_batch.get("state") != "JOB_STATE_SUCCEEDED":
        raise RuntimeError(f"Gemini batch finished with state={final_batch.get('state')}")

    output_file_id = final_batch.get("dest_file_name")
    if not output_file_id:
        raise RuntimeError("Gemini batch completed but dest.file_name is missing.")

    output_path = BATCH_OUTPUT_DIR / f"{run_id}_output.jsonl"
    download_batch_output(output_file_id, output_path)
    batch_rows = parse_batch_output(output_path)

    from src.dataset_writer import init_csv
    csv_path = RESULTS_DIR / "gemini_results.csv"
    init_csv(csv_path)

    for item in batch_rows:
        custom_id = item["custom_id"]
        meta = task_lookup[custom_id]
        task = meta["task"]
        prompt_type = meta["prompt_type"]

        response_body = item.get("response", {}).get("body", {})
        choices = response_body.get("choices", [])
        raw_text = ""
        if choices:
            raw_text = choices[0].get("message", {}).get("content", "") or ""

        usage = response_body.get("usage", {}) or {}
        response_id = response_body.get("id", "") or ""

        process_single_response(
            task=task,
            provider_name=provider_name,
            model_name=model_name,
            prompt_type=prompt_type,
            raw_text=raw_text,
            response_meta={
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "provider_latency_seconds": "",
                "input_tokens": usage.get("promptTokens", 0),
                "output_tokens": usage.get("completionTokens", 0),
                "response_id": response_id,
            },
            csv_path=csv_path,
            raw_dir=RAW_DIR,
            code_dir=CODE_DIR,
            sonar_dir=SONAR_DIR,
            enable_sonar=ENABLE_SONAR,
            sonar_host_url=SONAR_HOST_URL,
            sonar_token=SONAR_TOKEN,
            sonar_poll_seconds=3,
            sonar_max_poll_attempts=60,
            timeout_seconds=10,
            run_id=run_id,
        )


if __name__ == "__main__":
    main()