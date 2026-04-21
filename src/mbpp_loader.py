from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_mbpp_tasks(path: Path) -> list[dict[str, Any]]:
    tasks: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            tasks.append(json.loads(line))
    return tasks


def filter_tasks(
    tasks: list[dict[str, Any]],
    min_id: int | None = None,
    max_id: int | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    filtered: list[dict[str, Any]] = []
    for task in tasks:
        task_id = int(task.get("task_id"))
        if min_id is not None and task_id < min_id:
            continue
        if max_id is not None and task_id > max_id:
            continue
        filtered.append(task)
    if limit is not None:
        filtered = filtered[:limit]
    return filtered
