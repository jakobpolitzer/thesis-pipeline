from __future__ import annotations
from datetime import datetime, timezone

import argparse

from src.config import (
    CODE_DIR,
    DEFAULT_LIMIT,
    DEFAULT_MAX_TASK_ID,
    DEFAULT_MIN_TASK_ID,
    DEFAULT_MODEL_NAME,
    DEFAULT_TIMEOUT_SECONDS,
    ENABLE_SONAR,
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
from src.providers.openai_provider import call_openai


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the OpenAI MBPP pipeline.")
    parser.add_argument("--min-task-id", type=int, default=DEFAULT_MIN_TASK_ID)
    parser.add_argument("--max-task-id", type=int, default=DEFAULT_MAX_TASK_ID)
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    parser.add_argument("--model", type=str, default=DEFAULT_MODEL_NAME)
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    return parser.parse_args()


def main() -> None:
    run_id = datetime.now(timezone.utc).strftime("openai_%Y%m%dT%H%M%SZ")
    args = parse_args()

    tasks = load_mbpp_tasks(MBPP_FILE)
    tasks = filter_tasks(
        tasks,
        min_id=args.min_task_id,
        max_id=args.max_task_id,
        limit=args.limit,
    )

    run_pipeline(
        tasks=tasks,
        provider_name="openai",
        model_name=args.model,
        provider_call=call_openai,
        csv_path=RESULTS_DIR / "openai_results.csv",
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
    )

if __name__ == "__main__":
    main()
