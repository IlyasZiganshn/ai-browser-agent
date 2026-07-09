# Interview Notes — ai-browser-agent

## Одно предложение

> "Автономный агент: LLM планирует, `BrowserController` (Playwright) исполняет. Планирование — OpenAI-compatible tool-calling (navigate/click/scroll/type_text), goal-check в `is_article_page()`, бюджет 10 шагов на задачу."

## Ключевые решения

### 1. LLM как планер, browser как чистый I/O

- Разделение: `Agent.run()` не знает, что такое браузер. Знает только `browser.is_article_page()` и `browser.<action>(args)`.
- `BrowserController` не знает про LLM. Только про Playwright.
- Плюс: swapping LLM провайдера — 1 переменная (`GLM_BASE_URL`). Swapping браузера (Firefox/WebKit) — 1 строка в `start()`.
- Trade-off: если LLM галлюцинирует action не из schema — упаду с TypeError. В прод-версии добавил бы валидацию + retry.

### 2. Actions через семантический DOM, не CSS-селекторы

- `page.get_by_text("Джеффри Эпштейн")` устойчив к ребрендингу вёрстки.
- Fallback на `get_by_role("link", name=...)` если text вернул несколько или ничего.
- Специально НЕ использую `page.locator(".css-1x2y3z")` — эти классы генерятся, ломаются на каждом deploy.

### 3. Один LLM-call per step, одно action per step

- Проще для дебага: если что-то пошло не так — точно видно, на каком шаге.
- Проще для safety: guardrails применяются к одному action, а не к цепочке.
- Trade-off: медленно. Для сложных задач (заполнить многостраничную форму) — переехал бы на планер с multi-step plans + validator.

### 4. Bounded step budget (10)

- Защита от бесконечного цикла, если LLM залипает или задача невыполнима.
- Число подобрано под demo (Wikipedia): реальные задачи типа "сравни 3 товара" требуют 20-30, но там был бы другой goal-check и другой system prompt.

### 5. Goal-check как отдельный метод

- `is_article_page()` — эвристика: `<article>`, или h1+много текста. Специфично под Wikipedia, но общая форма работает на большинстве news/wiki-сайтов.
- В прод-версии goal-check передавался бы как параметр в `Agent(browser, goal_check=...)`. Так же для чистой абстракции.

### 6. Safety = blunt keyword filter

- `agent/safety.py` блочит "оплата", "удаление", "подтвердить платёж". Не sec-boundary — user, знающий обход, обойдёт.
- Смысл: не дать LLM случайно выполнить деструктив, если сгаллюцинировал шаг с покупкой.
- В прод — human-in-the-loop подтверждение перед любой destructive action.

## Вопросы, которые могут задать

**Q: Почему GLM/Zhipu, а не OpenAI/Claude?**
A: GLM-4-Flash — дёшево, быстро, российский юзер получает нормальный latency. Мигрируется на любой OpenAI-compatible provider через `GLM_BASE_URL` — код не меняется.

**Q: Как проверяешь, что LLM выбрал правильный action?**
A: Никак — планер доверяет LLM. Если action ошибочен, следующий step увидит, что цель не достигнута, и LLM попробует иначе. Grounding — через `dom.py::extract_semantic_dom()` (кладу 50 видимых элементов в промпт).

**Q: Что если браузер завис?**
A: `set_default_timeout(15000)` — каждое действие падает через 15 сек. Планер словит exception и решит, что делать (в текущей версии — просто продолжит; в прод — retry или abort).

**Q: Reproducibility?**
A: `temperature=0.1` — почти детерминистично, но не полностью. Для воспроизводимых тестов взял бы `seed` (не все провайдеры поддерживают) или заказал бы фиксированные mock LLM responses в тестах.

**Q: Как масштабируется?**
A: Одна задача — один process. Параллелизация — через process pool (browser context не потокобезопасен на CPython). Общий Redis/DB для мониторинга и очереди задач.

**Q: MCP? Agentic frameworks (LangGraph, CrewAI)?**
A: Специально не использовал — хотел минимальный custom loop, полностью объяснимый. В моих Claude Code кастомизациях (privately) я строю MCP-серверы для tool-use; здесь взял OpenAI function-calling для минимальной зависимости.

## Что честно НЕ знаешь

- Не гонял агента на > 20 разнородных задач. Не знаю, какая точность на, скажем, "закажи такси" — это тестировать надо на живых юзерах.
- Не сравнивал `get_by_text` vs скриншот-based grounding (Anthropic Computer Use, OpenAI vision). Верю, что скриншот+vision точнее, но дороже в 10-100 раз по латентности.
- Не измерил токены за run. Приблизительно 2-5K за задачу в 5-8 шагов.

## Про восстановление

`config.py` и `browser/controller.py` были восстановлены после сбоя файловой системы — их blob'ы в `.git/objects` оказались повреждены (inflate: data stream error). Восстановлены по контракту, который явно виден в остальных файлах:
- `config.py` — по import'ам в `agent/llm.py` (`GLM_API_KEY, GLM_BASE_URL, LLM_MODEL, LLM_TEMPERATURE, LLM_MAX_TOKENS`)
- `browser/controller.py` — по вызовам в `agent/planner.py` (`navigate`, `click_by_text`, `type_text`, `is_article_page`) + tools/schema.py (`scroll`)

На интервью — говорю прямо: "оригинал был утерян, эти два файла я переписал по контракту". Логика планера, LLM-клиент, tool-schema, safety, dom-extraction — оригинальные.
