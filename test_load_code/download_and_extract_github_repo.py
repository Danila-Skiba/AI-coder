import requests, zipfile, io, os, shutil


def download_and_extract_github_repo(owner, repo, branch="master", extract_to="langchain"):
    """
    Скачивает и распаковывает исходный код GitHub-репозитория в формате ZIP

    Извлечённый код сохраняется в указанную директорию. Если она уже существует — она будет перезаписана

    Параметры:
        owner (str): Имя пользователя или организации на GitHub
        repo (str): Название репозитория
        branch (str): Ветка, которую нужно скачать (по умолчанию "master")
        extract_to (str): Папка, в которую будет извлечён исходный код (по умолчанию "langchain")

    Исключения:
        requests.HTTPError: Если запрос к GitHub завершился с ошибкой

    Пример:
        download_and_extract_github_repo("langchain-ai", "langchain", branch="master", extract_to="langchain")
    """
    zip_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/{branch}.zip"

    print(f"[info] Donloading zip from: {zip_url}")
    response = requests.get(zip_url, stream=True)
    response.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
        tmp_dir = f"tmp_{repo}_download"
        zip_file.extractall(tmp_dir)

        extracted_root = os.path.join(tmp_dir, os.listdir(tmp_dir)[0])
        if os.path.exists(extract_to):
            shutil.rmtree(extract_to)
        shutil.move(extracted_root, extract_to)
        shutil.rmtree(tmp_dir)
    print(f"[info] Repo extracted to: {extract_to}")


download_and_extract_github_repo("langchain-ai", "langchain", "master", "langchain")
