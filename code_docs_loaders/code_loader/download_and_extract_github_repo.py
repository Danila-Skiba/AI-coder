import requests, zipfile, io, os, shutil
from code_docs_loaders.settings import *


def download_and_extract_github_repo():
    """
    Скачивает и распаковывает исходный код GitHub-репозитория в формате ZIP

    Извлечённый код сохраняется в указанную директорию. Если она уже существует — она будет перезаписана

    Исключения:
        requests.HTTPError: Если запрос к GitHub завершился с ошибкой

    Пример:
        download_and_extract_github_repo()
    """
    print(f"[info] Donloading zip from: {ZIP_URL}")
    response = requests.get(ZIP_URL, stream=True)
    response.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
        tmp_dir = f"tmp_{CODE_DIR}_download"
        zip_file.extractall(tmp_dir)

        extracted_root = os.path.join(tmp_dir, os.listdir(tmp_dir)[0])
        if os.path.exists(CODE_DIR):
            shutil.rmtree(CODE_DIR)
        shutil.move(extracted_root, CODE_DIR)
        shutil.rmtree(tmp_dir)
    print(f"[info] Repo extracted to: {CODE_DIR}")
