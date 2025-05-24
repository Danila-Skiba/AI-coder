import os
from code_docs_loaders.settings import *


def remove_empty_py_files():
    """
    Удаляет все пустые .py файлы в указанной директории (не рекурсивно)
    """
    removed_count = 0

    for filename in os.listdir(OUTPUT_DIR):
        if filename.endswith(".py"):
            filepath = os.path.join(OUTPUT_DIR, filename)
            if os.path.isfile(filepath) and os.path.getsize(filepath) == 0:
                os.remove(filepath)
                removed_count += 1
    print(f"[info] Removed {removed_count} empty files")
