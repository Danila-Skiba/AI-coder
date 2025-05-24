import os
from code_docs_loaders.settings import *
import re


def remove_docstring_only_files():
    """
    Удаляет .py файлы, которые содержат только одну строку документации в тройных кавычках
    или полностью пустые (0 символов, 0 байт)
    """
    removed_count = 0
    triple_quote_pattern = re.compile(r'^\s*(["\']{3})(.*?)\1\s*$', re.DOTALL)

    for filename in os.listdir(OUTPUT_DIR):
        if filename.endswith(".py"):
            filepath = os.path.join(OUTPUT_DIR, filename)
            if not os.path.isfile(filepath):
                continue

            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read().strip()

            if not content or triple_quote_pattern.fullmatch(content):
                os.remove(filepath)
                removed_count += 1

    print(f"[info] Removed {removed_count} empty files")
