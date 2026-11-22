import asyncio
import json

from agent.llm import ask_llm
from agent.system_prompt import SYSTEM_PROMPT


class Agent:
    def __init__(self, browser):
        self.browser = browser
        self.history = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    async def run(self, task):
        self.history.append({"role": "user", "content": task})

        for _step in range(10):
            await asyncio.sleep(1.5)

            if await self.browser.is_article_page():
                print("DONE: Открыта статья")
                return

            response = ask_llm(self.history)
            msg = response.choices[0].message

            if msg.tool_calls:
                self.history.append(msg)
                for call in msg.tool_calls:
                    await self.execute(call)
            else:
                self.history.append({
                    "role": "system",
                    "content": "Статья ещё не открыта. Продолжай."
                })

        print("[STOP] Лимит шагов")

    async def execute(self, call):
        name = call.function.name
        args = json.loads(call.function.arguments)

        if name == "navigate":
            await self.browser.navigate(args["url"])

        elif name == "click":
            await self.browser.click_by_text(args["text"])

        elif name == "type_text":
            await self.browser.type_text(args["text"])
