from __future__ import annotations

import argparse
from datetime import datetime, timezone

from src.config import (
    CODE_DIR,
    DEFAULT_LIMIT,
    DEFAULT_MAX_TASK_ID,
    DEFAULT_MIN_TASK_ID,
    DEFAULT_TIMEOUT_SECONDS,
    ENABLE_SONAR,
    GEMINI_API_KEY,
    GENERATION_TEMPERATURE,
    MBPP_FILE,
    RAW_DIR,
    RESULTS_DIR,
    SONAR_DIR,
    SONAR_HOST_URL,
    SONAR_MAX_POLL_ATTEMPTS,
    SONAR_POLL_SECONDS,
    SONAR_TOKEN,
)
from src.mbpp_loader import filter_tasks, load_mbpp_tasks
from src.pipeline_core import run_pipeline
from src.providers.gemini_provider import call_gemini


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Gemini MBPP pipeline.")
    parser.add_argument("--min-task-id", type=int, default=DEFAULT_MIN_TASK_ID)
    parser.add_argument("--max-task-id", type=int, default=DEFAULT_MAX_TASK_ID)
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    parser.add_argument("--model", type=str, default="gemini-2.5-pro")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    return parser.parse_args()


def main() -> None:
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is missing in environment.")

    args = parse_args()
    run_id = datetime.now(timezone.utc).strftime("gemini_%Y%m%dT%H%M%SZ")

    tasks = load_mbpp_tasks(MBPP_FILE)
    tasks = filter_tasks(
        tasks,
        min_id=args.min_task_id,
        max_id=args.max_task_id,
        limit=args.limit,
    )

    run_pipeline(
        tasks=tasks,
        provider_name="gemini",
        model_name=args.model,
        provider_call=call_gemini,
        csv_path=RESULTS_DIR / "gemini_results.csv",
        raw_dir=RAW_DIR,
        code_dir=CODE_DIR,
        sonar_dir=SONAR_DIR,
        enable_sonar=ENABLE_SONAR,
        sonar_host_url=SONAR_HOST_URL,
        sonar_token=SONAR_TOKEN,
        sonar_poll_seconds=SONAR_POLL_SECONDS,
        sonar_max_poll_attempts=SONAR_MAX_POLL_ATTEMPTS,
        timeout_seconds=args.timeout,
        run_id=run_id,
        generation_temperature=GENERATION_TEMPERATURE,
    )


if __name__ == "__main__":
    main()
    