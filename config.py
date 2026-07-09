"""Runtime config loaded from .env.

Split into LLM and browser sections so a single wrong key surfaces cleanly.
Reconstructed after data loss — variable names locked to what the original
code loaded (see git blob of agent/llm.py and test_llm.py).
"""
import os
from dotenv import load_dotenv

load_dotenv()


def _get(name: str, default: str | None = None, required: bool = False) -> str | None:
    value = os.getenv(name, default)
    if required and not value:
        raise RuntimeError(f"Missing required env var: {name}")
    return value


# --- LLM (GLM/Zhipu, OpenAI-compatible) ---
GLM_API_KEY = _get("GLM_API_KEY", required=True)
GLM_BASE_URL = _get("GLM_BASE_URL", "https://open.bigmodel.cn/api/paas/v4/")
LLM_MODEL = _get("LLM_MODEL", "glm-4-flash")
LLM_TEMPERATURE = float(_get("LLM_TEMPERATURE", "0.1"))
LLM_MAX_TOKENS = int(_get("LLM_MAX_TOKENS", "1024"))

# --- Browser ---
BROWSER_HEADLESS = _get("BROWSER_HEADLESS", "true").lower() in ("1", "true", "yes")
BROWSER_TIMEOUT_MS = int(_get("BROWSER_TIMEOUT_MS", "15000"))
