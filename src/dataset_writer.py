from __future__ import annotations

import csv
from pathlib import Path

FIELDNAMES = [
    "run_id",
    "timestamp_utc",
    "provider_latency_seconds",
    "task_id",
    "model_name",
    "provider",
    "prompt_type",
    "test_status",
    "returncode",
    "input_tokens",
    "output_tokens",
    "response_id",
    "stdout",
    "stderr",
    "cognitive_complexity",
    "cyclomatic_complexity",
    "lines_of_code",
    "code_smells",
    "raw_response_path",
    "code_path",
]


def init_csv(csv_path: Path) -> None:
    if not csv_path.exists():
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()


def append_result(csv_path: Path, row: dict) -> None:
    with csv_path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writerow(row)
