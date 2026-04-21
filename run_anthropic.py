from datetime import datetime, timezone
import argparse

from src.config import (
    ANTHROPIC_API_KEY,
    CODE_DIR,
    ENABLE_SONAR,
    MBPP_FILE,
    RAW_DIR,
    RESULTS_DIR,
    SONAR_DIR,
    SONAR_HOST_URL,
    SONAR_TOKEN,
)
from src.mbpp_loader import filter_tasks, load_mbpp_tasks
from src.pipeline_core import run_pipeline
from src.providers.anthropic_provider import call_anthropic


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-task-id", type=int, default=11)
    parser.add_argument("--max-task-id", type=int, default=510)
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()

    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY is missing in environment.")

    tasks = load_mbpp_tasks(MBPP_FILE)
    tasks = filter_tasks(
        tasks,
        min_id=args.min_task_id,
        max_id=args.max_task_id,
        limit=args.limit,
    )

    run_id = datetime.now(timezone.utc).strftime("anthropic_%Y%m%dT%H%M%SZ")

    run_pipeline(
        tasks=tasks,
        provider_name="anthropic",
        model_name="claude-sonnet-4-6",
        provider_call=call_anthropic,
        csv_path=RESULTS_DIR / "anthropic_results.csv",
        raw_dir=RAW_DIR,
        code_dir=CODE_DIR,
        sonar_dir=SONAR_DIR,
        enable_sonar=ENABLE_SONAR,
        sonar_host_url=SONAR_HOST_URL,
        sonar_token=SONAR_TOKEN,
        run_id=run_id,
    )


if __name__ == "__main__":
    main()