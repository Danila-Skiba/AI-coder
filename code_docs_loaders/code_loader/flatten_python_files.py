import os
import shutil
from code_docs_loaders.settings import *


def flatten_python_files() -> None:
    """
    Копирует все .py файлы из SOURCE_DIR (включая вложенные папки)
    в одну плоскую директорию OUTPUT_DIR, удаляя структуру папок

    Если файлы с одинаковыми именами встречаются, они переименовываются с добавлением номера (_1, _2, ...).
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    name_counts = {}

    for dirpath, _, filenames in os.walk(SOURCE_DIR):
        for filename in filenames:
            if filename.endswith(".py"):
                src_path = os.path.join(dirpath, filename)

                if filename not in name_counts:
                    name_counts[filename] = 0
                    dst_name = filename
                else:
                    name_counts[filename] += 1
                    name, ext = os.path.splitext(filename)
                    dst_name = f"{name}_{name_counts[filename]}{ext}"

                dst_path = os.path.join(OUTPUT_DIR, dst_name)
                shutil.copy2(src_path, dst_path)
    print("[info] Finished copying .py files")
