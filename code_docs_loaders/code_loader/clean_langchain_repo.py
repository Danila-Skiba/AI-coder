import os
from code_docs_loaders.settings import *


def clean_langchain_repo():
    """
    Очищает репозиторий от всех файлов, кроме исходного кода на Python

    Сохраняются только '.py' файлы, в указанных папках
    Все остальные файлы и директории удаляются
    Также удаляются пустые директории

    Пример:
        clean_langchain_repo()
    """
    allowed_dirs = [CODE_DIR, os.path.join(*ALLOWED_DIRS)]
    allowed_exts = [".py"]

    def is_allowed(file_path):
        if not file_path.endswith(tuple(allowed_exts)):
            return False
        for allowed in allowed_dirs:
            if os.path.commonpath(
                    [os.path.abspath(file_path), os.path.abspath(os.path.join(CODE_DIR, allowed))]) == os.path.abspath(
                os.path.join(CODE_DIR, allowed)):
                return True
        return False

    for root, dirs, files in os.walk(CODE_DIR, topdown=False):
        for name in files:
            full_path = os.path.join(root, name)
            if not is_allowed(full_path):
                os.remove(full_path)
        for name in dirs:
            full_path = os.path.join(root, name)
            if not os.listdir(full_path):
                os.rmdir(full_path)

    print("[info] Removed unnecessary files")
