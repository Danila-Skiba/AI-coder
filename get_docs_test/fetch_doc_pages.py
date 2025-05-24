import asyncio
import os
from urllib.parse import urljoin, urlparse

from playwright.async_api import async_playwright

from get_docs_test.save_html_and_md import save_html_and_md
from settings import *


async def fetch_doc_pages():
    """
    Асинхронно загружает и сохраняет документацию LangChain в формате Markdown

    Загружает все уникальные страницы документации с сайта LangChain,
    извлекая только содержимое основного блока с классом `theme-doc-markdown markdown`
    HTML и конвертированные Markdown-версии сохраняются в папки `html_docs/` и `md_docs/`

    Повторные загрузки уже скачанных страниц пропускаются

    Использует библиотеку Playwright для навигации по страницам и парсинга DOM

    Исключения:
        playwright.async_api.Error: При ошибках загрузки страниц или отсутствующем элементе
        OSError: При проблемах с доступом к файловой системе

    Пример:
        asyncio.run(fetch_doc_pages())
    """
    os.makedirs(HTML_DIR, exist_ok=True)
    os.makedirs(MD_DIR, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(BASE_URL, timeout=60000)
        await page.wait_for_selector("nav a[href^='/docs/']")

        links = await page.eval_on_selector_all(
            "nav a[href^='/docs/']",
            "els => Array.from(new Set(els.map(el => el.getAttribute('href').split('#')[0])))"
        )

        print(f"[info] Found {len(links)} links")

        for href in links:
            url = urljoin(BASE_URL, href)
            path = urlparse(href).path.strip("/").replace("/", "_") or "index"
            md_file = os.path.join(MD_DIR, f"{path}.md")

            if os.path.exists(md_file):
                print(f"[skip] {md_file} already exists")
                continue

            print(f"[fetch] {url}")
            try:
                await page.goto(url, timeout=60000)
                await page.wait_for_selector("div.theme-doc-markdown.markdown")

                element = await page.query_selector("div.theme-doc-markdown.markdown")
                if not element:
                    print(f"[warn] Content not found at link {url}")
                    continue

                content = await element.inner_html()
                save_html_and_md(content, path)

            except Exception as e:
                print(f"[error] Error while loading {url}: {e}")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(fetch_doc_pages())
