import os


def clean_langchain_repo(repo_path):
    """
    Очищает репозиторий LangChain от всех файлов, кроме исходного кода библиотеки на Python

    Сохраняются только `.py` файлы, находящиеся в папках `langchain/` и `libs/langchain/`
    Все остальные файлы и директории удаляются
    Также удаляются пустые директории

    Параметры:
        repo_path (str): Путь к корневой директории извлечённого репозитория

    Пример:
        clean_langchain_repo("langchain")
    """
    allowed_dirs = ["langchain", os.path.join("libs", "langchain")]
    allowed_exts = [".py"]

    def is_allowed(file_path):
        if not file_path.endswith(tuple(allowed_exts)):
            return False
        for allowed in allowed_dirs:
            if os.path.commonpath(
                    [os.path.abspath(file_path), os.path.abspath(os.path.join(repo_path, allowed))]) == os.path.abspath(
                os.path.join(repo_path, allowed)):
                return True
        return False

    for root, dirs, files in os.walk(repo_path, topdown=False):
        for name in files:
            full_path = os.path.join(root, name)
            if not is_allowed(full_path):
                os.remove(full_path)
        for name in dirs:
            full_path = os.path.join(root, name)
            if not os.listdir(full_path):
                os.rmdir(full_path)

    print("[info] Removed unnecessary files")


clean_langchain_repo("langchain")
