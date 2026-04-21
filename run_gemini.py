from datetime import datetime, timezone

from src.config import (
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
from src.pipeline_core import run_pipeline
from src.providers.gemini_provider import call_gemini


def main() -> None:
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is missing in environment.")

    tasks = load_mbpp_tasks(MBPP_FILE)
    tasks = filter_tasks(tasks, min_id=11, max_id=510, limit=5)

    run_id = datetime.now(timezone.utc).strftime("gemini_%Y%m%dT%H%M%SZ")

    run_pipeline(
        tasks=tasks,
        provider_name="gemini",
        model_name="gemini-2.5-pro",
        provider_call=call_gemini,
        csv_path=RESULTS_DIR / "gemini_results.csv",
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