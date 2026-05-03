from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "outputs"
LOG_DIR = OUTPUT_DIR / "logs"
RAW_DIR = OUTPUT_DIR / "raw_responses"
CODE_DIR = OUTPUT_DIR / "generated_code"
SONAR_DIR = OUTPUT_DIR / "sonar_projects"
RESULTS_DIR = OUTPUT_DIR / "results"
BATCH_INPUT_DIR = OUTPUT_DIR / "batch_inputs"
BATCH_OUTPUT_DIR = OUTPUT_DIR / "batch_outputs"

for directory in [LOG_DIR, RAW_DIR, CODE_DIR, SONAR_DIR, RESULTS_DIR, BATCH_INPUT_DIR, BATCH_OUTPUT_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

MBPP_FILE = DATA_DIR / "mbpp.jsonl"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

ENABLE_SONAR = os.getenv("ENABLE_SONAR", "false").lower() == "true"
SONAR_HOST_URL = os.getenv("SONAR_HOST_URL", "http://localhost:9000")
SONAR_TOKEN = os.getenv("SONAR_TOKEN", "")
GENERATION_TEMPERATURE = float(os.getenv("GENERATION_TEMPERATURE", "0.2"))
SONAR_POLL_SECONDS = int(os.getenv("SONAR_POLL_SECONDS", "5"))
SONAR_MAX_POLL_ATTEMPTS = int(os.getenv("SONAR_MAX_POLL_ATTEMPTS", "120"))

DEFAULT_MODEL_NAME = "gpt-5.4"
DEFAULT_MIN_TASK_ID = 11
DEFAULT_MAX_TASK_ID = 510
DEFAULT_LIMIT = 10
DEFAULT_TIMEOUT_SECONDS = 10
