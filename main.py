import asyncio
from browser.controller import BrowserController
from agent.planner import Agent


async def main():
    browser = BrowserController()
    await browser.start()

    agent = Agent(browser)

    try:
        await agent.run(
            "Зайди на wikipedia.org и открой статью про FastAPI"
        )
    finally:
        await browser.close()

asyncio.run(main())
