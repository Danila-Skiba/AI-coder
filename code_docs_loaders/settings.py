# Setting up documentation downloads
from pipes import SOURCE

BASE_URL = "https://python.langchain.com/docs/"
HTML_DIR = "html_docs"
MD_DIR = "md_docs"
HTML_DOCS_CLASS = "div.theme-doc-markdown.markdown"

# Setting up code downloads
CODE_DIR = "langchain"
ZIP_URL = "https://github.com/langchain-ai/langchain/archive/refs/heads/master.zip"

# Setting up code cleaner
ALLOWED_DIRS = ["libs", "langchain"]

# Setting up the transfer of all files to one folder
SOURCE_DIR = "langchain"
OUTPUT_DIR = "langchain_code"