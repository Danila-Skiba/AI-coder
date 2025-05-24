import asyncio

from code_loader.clean_langchain_repo import clean_langchain_repo
from code_loader.download_and_extract_github_repo import download_and_extract_github_repo
from docs_loader.fetch_doc_pages import fetch_doc_pages

if __name__ == "__main__":
    asyncio.run(fetch_doc_pages())

    download_and_extract_github_repo()
    clean_langchain_repo()
