from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path
from typing import Any

import requests

SONAR_METRIC_KEYS = [
    "cognitive_complexity",
    "complexity",
    "ncloc",
    "code_smells",
]


def create_sonar_project(project_dir: Path, code: str) -> None:
    project_dir.mkdir(parents=True, exist_ok=True)
    (project_dir / "candidate.py").write_text(code, encoding="utf-8")

    sonar_project_properties = f"""
sonar.projectKey={project_dir.name}
sonar.projectName={project_dir.name}
sonar.sources=.
sonar.sourceEncoding=UTF-8
""".strip()

    (project_dir / "sonar-project.properties").write_text(
        sonar_project_properties,
        encoding="utf-8",
    )


def run_sonar_scan(project_dir: Path, sonar_host_url: str, sonar_token: str) -> dict[str, Any]:
    env = dict(os.environ)
    env["SONAR_TOKEN"] = sonar_token

    result = subprocess.run(
        [
            "sonar-scanner",
            f"-Dsonar.host.url={sonar_host_url}",
            f"-Dsonar.token={sonar_token}",
        ],
        cwd=project_dir,
        capture_output=True,
        text=True,
        env=env,
    )

    return {
        "status": "ok" if result.returncode == 0 else "error",
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode,
    }


def fetch_sonar_measures(
    sonar_host_url: str,
    sonar_token: str,
    project_key: str,
) -> dict[str, str]:
    url = f"{sonar_host_url.rstrip('/')}/api/measures/component"
    response = requests.get(
        url,
        params={
            "component": project_key,
            "metricKeys": ",".join(SONAR_METRIC_KEYS),
        },
        auth=(sonar_token, ""),
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()

    measures = {key: "" for key in SONAR_METRIC_KEYS}
    for item in payload.get("component", {}).get("measures", []):
        metric = item.get("metric")
        value = item.get("value", "")
        if metric in measures:
            measures[metric] = value
    return measures


def wait_for_sonar_measures(
    sonar_host_url: str,
    sonar_token: str,
    project_key: str,
    poll_seconds: int,
    max_attempts: int,
) -> dict[str, str]:
    last_error: Exception | None = None
    for _ in range(max_attempts):
        try:
            return fetch_sonar_measures(sonar_host_url, sonar_token, project_key)
        except Exception as exc:  # pragma: no cover
            last_error = exc
            time.sleep(poll_seconds)
    if last_error:
        raise last_error
    raise RuntimeError("Failed to fetch SonarQube measures.")
