from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
from typing import Any


def run_mbpp_tests(
    code: str,
    test_setup_code: str,
    test_list: list[str],
    timeout: int = 10,
) -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        script_path = tmp_path / "candidate.py"

        parts = []
        if test_setup_code:
            parts.append(test_setup_code.strip())
        parts.append(code.strip())
        parts.extend(test_list)
        full_script = "\n\n".join(part for part in parts if part)
        script_path.write_text(full_script, encoding="utf-8")

        try:
            result = subprocess.run(
                ["python3", str(script_path)],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=tmp_path,
            )
            passed = result.returncode == 0
            return {
                "status": "pass" if passed else "fail",
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {
                "status": "timeout",
                "stdout": "",
                "stderr": "Execution timed out.",
                "returncode": -1,
            }
        except Exception as exc:  # pragma: no cover
            return {
                "status": "error",
                "stdout": "",
                "stderr": str(exc),
                "returncode": -2,
            }
