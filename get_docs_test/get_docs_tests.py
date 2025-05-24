import asyncio
import os
from urllib.parse import urljoin, urlparse

from playwright.async_api import async_playwright
from markdownify import markdownify as md

BASE_URL = "https://python.langchain.com/docs/"
OUTPUT_DIR = "html_docs_test"


def save_html_and_md(content: str, path: str):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    html_file = os.path.join(OUTPUT_DIR, f"{path}.html")
    md_file = os.path.join(OUTPUT_DIR, f"{path}.md")

    with open(html_file, "w", encoding="utf-8") as f:
        f.write(content)

    md_text = md(content, heading_style="ATX")
    with open(md_file, "w", encoding="utf-8") as f:
        f.write(md_text)


def matches_keywords(href: str, keywords: list[str]) -> bool:
    href_lower = href.lower()
    return any(kw.lower() in href_lower for kw in keywords)


async def fetch_doc_pages(keywords=None):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(BASE_URL, timeout=60000)
        await page.wait_for_selector("nav a[href^='/docs/']")

        links = await page.eval_on_selector_all(
            "nav a[href^='/docs/']",
            "els => Array.from(new Set(els.map(el => el.getAttribute('href').split('#')[0])))"
        )

        if keywords:
            links = [href for href in links if matches_keywords(href, keywords)]

        print(f"[info] Found {len(links)} links")

        for href in links:
            url = urljoin(BASE_URL, href)
            path = urlparse(href).path.strip("/").replace("/", "_") or "index"
            html_file = os.path.join(OUTPUT_DIR, f"{path}.html")
            md_file = os.path.join(OUTPUT_DIR, f"{path}.md")

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
    keywords = input().split()
    asyncio.run(fetch_doc_pages(keywords if keywords else None))
