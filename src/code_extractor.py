from __future__ import annotations

import re


def extract_python_code(raw_text: str) -> str:
    if not raw_text:
        return ""

    python_fenced = re.findall(r"```python\s*(.*?)```", raw_text, flags=re.DOTALL | re.IGNORECASE)
    if python_fenced:
        return python_fenced[0].strip()

    generic_fenced = re.findall(r"```\s*(.*?)```", raw_text, flags=re.DOTALL)
    if generic_fenced:
        return generic_fenced[0].strip()

    return raw_text.strip()
