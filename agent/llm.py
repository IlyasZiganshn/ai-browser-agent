from openai import OpenAI
from config import (
    GLM_API_KEY,
    GLM_BASE_URL,
    LLM_MODEL,
    LLM_TEMPERATURE,
    LLM_MAX_TOKENS,
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
