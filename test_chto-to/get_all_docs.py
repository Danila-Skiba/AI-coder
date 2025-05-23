import asyncio
import os
from urllib.parse import urljoin, urlparse

from playwright.async_api import async_playwright

BASE_URL = "https://python.langchain.com/docs/"
OUTPUT_DIR = "html_docs"

async def fetch_doc_pages():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(BASE_URL, timeout=60000)

        # ⬇️ Дожидаемся полной загрузки и появления меню
        await page.wait_for_selector("nav a[href^='/docs/']")

        # ⬇️ Собираем ВСЕ ссылки на документацию
        links = await page.eval_on_selector_all(
            "nav a[href^='/docs/']",
            "els => Array.from(new Set(els.map(el => el.getAttribute('href').split('#')[0])))"
        )

        print(f"[info] Найдено {len(links)} уникальных ссылок")

        for href in links:
            url = urljoin(BASE_URL, href)
            # /docs/modules/chains -> docs_modules_chains.html
            path = urlparse(href).path.strip("/").replace("/", "_") or "index"
            filename = os.path.join(OUTPUT_DIR, f"{path}.html")

            if os.path.exists(filename):
                print(f"[skip] {filename} уже скачан")
                continue

            print(f"[fetch] {url} -> {filename}")
            try:
                await page.goto(url, timeout=60000)
                await page.wait_for_selector("article")  # ⬅️ контейнер основного текста
                content = await page.content()
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(content)
            except Exception as e:
                print(f"[error] Ошибка при загрузке {url}: {e}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(fetch_doc_pages())
