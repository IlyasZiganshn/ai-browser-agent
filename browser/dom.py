async def extract_semantic_dom(page):
    elements = await page.evaluate("""
        () => {
            const els = [];
            document.querySelectorAll("button, a, input").forEach(e => {
                els.push({
                    tag: e.tagName,
                    text: e.innerText || e.value || "",
                    aria: e.getAttribute("aria-label")
                });
            });
            return els.slice(0, 50);
        }
    """)
    return elements
