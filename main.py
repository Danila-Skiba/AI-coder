import asyncio

from code_docs_loaders.code_loader.clean_langchain_repo import clean_langchain_repo
from code_docs_loaders.code_loader.download_and_extract_github_repo import download_and_extract_github_repo
from code_docs_loaders.code_loader.flatten_python_files import flatten_python_files
from code_docs_loaders.code_loader.remove_empty_py_files import remove_empty_py_files
from code_docs_loaders.docs_loader.fetch_doc_pages import fetch_doc_pages

if __name__ == "__main__":
    # asyncio.run(fetch_doc_pages())
    #
    # download_and_extract_github_repo()
    # clean_langchain_repo()
    # flatten_python_files()
    remove_empty_py_files()

