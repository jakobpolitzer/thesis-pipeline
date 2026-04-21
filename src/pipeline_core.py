from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Any, Callable

from src.code_extractor import extract_python_code
from src.dataset_writer import append_result, init_csv
from src.prompts import build_prompt
from src.sonar_runner import create_sonar_project, run_sonar_scan, wait_for_sonar_measures
from src.test_runner import run_mbpp_tests

ProviderCallable = Callable[[str, str], dict[str, Any]]


def extract_function_signature(reference_code: str) -> str:
    match = re.search(
        r"^\s*def\s+[A-Za-z_][A-Za-z0-9_]*\s*\(.*?\)\s*:",
        reference_code,
        re.MULTILINE,
    )
    if not match:
        raise ValueError("Could not extract function signature from reference code.")
    return match.group(0).strip()


def process_single_response(
    *,
    task: dict[str, Any],
    provider_name: str,
    model_name: str,
    prompt_type: str,
    raw_text: str,
    response_meta: dict[str, Any],
    csv_path: Path,
    raw_dir: Path,
    code_dir: Path,
    sonar_dir: Path,
    enable_sonar: bool,
    sonar_host_url: str | None,
    sonar_token: str | None,
    sonar_poll_seconds: int,
    sonar_max_poll_attempts: int,
    timeout_seconds: int,
    run_id: str,
) -> None:
    task_id = int(task["task_id"])
    test_setup_code = str(task.get("test_setup_code", "") or "")
    test_list = list(task.get("test_list", []))

    code = extract_python_code(raw_text)

    safe_stem = f"{provider_name}_{model_name}_{task_id}_{prompt_type}".replace("/", "_")
    raw_path = raw_dir / f"{safe_stem}.txt"
    raw_path.write_text(raw_text, encoding="utf-8")

    code_path = code_dir / f"{safe_stem}.py"
    code_path.write_text(code, encoding="utf-8")

    test_result = run_mbpp_tests(
        code=code,
        test_setup_code=test_setup_code,
        test_list=test_list,
        timeout=timeout_seconds,
    )

    row = {
        "run_id": run_id,
        "timestamp_utc": response_meta.get("timestamp_utc", datetime.now(timezone.utc).isoformat()),
        "provider_latency_seconds": response_meta.get("provider_latency_seconds", ""),
        "task_id": task_id,
        "model_name": model_name,
        "provider": provider_name,
        "prompt_type": prompt_type,
        "test_status": test_result["status"],
        "returncode": test_result["returncode"],
        "input_tokens": response_meta.get("input_tokens", 0),
        "output_tokens": response_meta.get("output_tokens", 0),
        "response_id": response_meta.get("response_id", ""),
        "stdout": test_result["stdout"],
        "stderr": test_result["stderr"],
        "cognitive_complexity": "",
        "cyclomatic_complexity": "",
        "lines_of_code": "",
        "code_smells": "",
        "raw_response_path": str(raw_path),
        "code_path": str(code_path),
    }

    if enable_sonar and test_result["status"] == "pass":
        if not sonar_host_url or not sonar_token:
            raise ValueError("SonarQube is enabled, but SONAR_HOST_URL or SONAR_TOKEN is missing.")

        project_dir = sonar_dir / safe_stem
        create_sonar_project(project_dir, code)
        scan_result = run_sonar_scan(project_dir, sonar_host_url, sonar_token)

        if scan_result["status"] == "ok":
            measures = wait_for_sonar_measures(
                sonar_host_url=sonar_host_url,
                sonar_token=sonar_token,
                project_key=project_dir.name,
                poll_seconds=sonar_poll_seconds,
                max_attempts=sonar_max_poll_attempts,
            )
            row["cognitive_complexity"] = measures.get("cognitive_complexity", "")
            row["cyclomatic_complexity"] = measures.get("complexity", "")
            row["lines_of_code"] = measures.get("ncloc", "")
            row["code_smells"] = measures.get("code_smells", "")
        else:
            row["stderr"] = f"{row['stderr']}\nSONAR ERROR:\n{scan_result['stderr']}".strip()

    append_result(csv_path, row)


def run_pipeline(
    tasks: list[dict[str, Any]],
    provider_name: str,
    model_name: str,
    provider_call: ProviderCallable,
    csv_path: Path,
    raw_dir: Path,
    code_dir: Path,
    sonar_dir: Path,
    enable_sonar: bool = False,
    sonar_host_url: str | None = None,
    sonar_token: str | None = None,
    sonar_poll_seconds: int = 2,
    sonar_max_poll_attempts: int = 20,
    timeout_seconds: int = 10,
    run_id: str = "run_unknown",
) -> None:
    init_csv(csv_path)

    for task in tasks:
        task_text = str(task["text"])
        reference_code = str(task.get("code", "") or "")
        function_signature = extract_function_signature(reference_code)

        for prompt_type in ["standard", "readability"]:
            prompt = build_prompt(task_text, prompt_type, function_signature)

            started = perf_counter()
            response = provider_call(model_name, prompt)
            latency = perf_counter() - started

            process_single_response(
                task=task,
                provider_name=provider_name,
                model_name=model_name,
                prompt_type=prompt_type,
                raw_text=str(response.get("raw_text", "")),
                response_meta={
                    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                    "provider_latency_seconds": round(latency, 4),
                    "input_tokens": response.get("input_tokens", 0),
                    "output_tokens": response.get("output_tokens", 0),
                    "response_id": response.get("response_id", ""),
                },
                csv_path=csv_path,
                raw_dir=raw_dir,
                code_dir=code_dir,
                sonar_dir=sonar_dir,
                enable_sonar=enable_sonar,
                sonar_host_url=sonar_host_url,
                sonar_token=sonar_token,
                sonar_poll_seconds=sonar_poll_seconds,
                sonar_max_poll_attempts=sonar_max_poll_attempts,
                timeout_seconds=timeout_seconds,
                run_id=run_id,
            )