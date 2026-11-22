from openai import OpenAI

from config import (
    GLM_API_KEY,
    GLM_BASE_URL,
    LLM_MAX_TOKENS,
    LLM_MODEL,
    LLM_TEMPERATURE,
)
from tools.schema import TOOLS

client = OpenAI(
    api_key=GLM_API_KEY,
    base_url=GLM_BASE_URL,
    timeout=60.0,
)


def ask_llm(messages):
    return client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",
        temperature=LLM_TEMPERATURE,
        max_tokens=LLM_MAX_TOKENS,
    )
