from __future__ import annotations

STANDARD_PROMPT = """Solve the following Python task.
Return only valid Python code.
Do not include explanations, markdown fences, or extra text.

Your solution must define the exact function required by the tests.
Required function signature:
{function_signature}

Task:
{task_text}
"""

READABILITY_PROMPT = """Solve the following Python task.
Return only valid Python code.
Write code that is functionally correct and as easy as possible to understand.
Prefer clear variable names, simple control flow, and low nesting.
Do not include explanations, markdown fences, or extra text.

Your solution must define the exact function required by the tests.
Required function signature:
{function_signature}

Task:
{task_text}
"""

def build_prompt(task_text: str, prompt_type: str, function_signature: str) -> str:
    if prompt_type == "standard":
        return STANDARD_PROMPT.format(
            task_text=task_text,
            function_signature=function_signature
        )
    if prompt_type == "readability":
        return READABILITY_PROMPT.format(
            task_text=task_text,
            function_signature=function_signature
        )
    raise ValueError(f"Unknown prompt_type: {prompt_type}")