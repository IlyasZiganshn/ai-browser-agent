"""Playwright-обёртка над одной вкладкой.

Реконструировано после потери данных. Контракт вытащен из agent/planner.py:
- start(), close(), is_article_page()
- navigate(url), click_by_text(text), type_text(text)
и из tools/schema.py: scroll(pixels).

Одна страница, никаких контекстов — минимум состояния, легко объяснять на интервью.
Timeout на все действия — иначе агент зависает при неточной подсказке от LLM.
"""
from __future__ import annotations

from playwright.async_api import async_playwright, Page, Browser, TimeoutError as PWTimeout
from config import BROWSER_HEADLESS, BROWSER_TIMEOUT_MS


class BrowserController:
    def __init__(self):
        self._playwright = None
        self._browser: Browser | None = None
        self._page: Page | None = None

    async def start(self) -> None:
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(headless=BROWSER_HEADLESS)
        context = await self._browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (compatible; ai-browser-agent/0.1)",
        )
        self._page = await context.new_page()
        self._page.set_default_timeout(BROWSER_TIMEOUT_MS)

    async def close(self) -> None:
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()

    @property
    def page(self) -> Page:
        if not self._page:
            raise RuntimeError("Browser not started")
        return self._page

    # --- actions used by planner ---

    async def navigate(self, url: str) -> None:
        await self.page.goto(url, wait_until="domcontentloaded")

    async def click_by_text(self, text: str) -> None:
        # get_by_text устойчивее CSS-классов — работает после ребрендинга фронта.
        try:
            await self.page.get_by_text(text, exact=False).first.click()
        except PWTimeout:
            # fallback: role-based (кнопка/ссылка с этим текстом)
            await self.page.get_by_role("link", name=text).first.click(timeout=BROWSER_TIMEOUT_MS // 2)

    async def type_text(self, text: str) -> None:
        # Ищем первое видимое поле ввода. Для мультиполей — planner должен уточнять фокус.
        locator = self.page.locator("input:visible, textarea:visible").first
        await locator.click()
        await locator.fill(text)
        await locator.press("Enter")

    async def scroll(self, pixels: int = 800) -> None:
        await self.page.evaluate(f"window.scrollBy(0, {pixels})")

    # --- goal check ---

    async def is_article_page(self) -> bool:
        """Эвристика: страница считается «статьёй», если у неё есть <article>
        или главный <h1> и заметный объём текста. Специфично под Wikipedia
        расширяется в подклассе — сейчас общий, достаточно универсальный сигнал.
        """
        return await self.page.evaluate(
            """
            () => {
                if (document.querySelector('article')) return true;
                const h1 = document.querySelector('h1');
                if (!h1) return false;
                const bodyText = (document.body.innerText || '').length;
                return h1.innerText.trim().length > 3 && bodyText > 1500;
            }
            """
        )
