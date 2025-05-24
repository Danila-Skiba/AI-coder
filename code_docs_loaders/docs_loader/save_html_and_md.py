import os
from markdownify import markdownify as md
from code_docs_loaders.settings import *


def save_html_and_md(content: str, path: str):
    """
    Сохраняет HTML-контент в файл и конвертирует его в Markdown

    HTML и соответствующий Markdown сохраняются в папки HTML_DIR и MD_DIR соответственно
    Названия файлов формируются на основе переданного пути

    Параметры:
        content (str): HTML-содержимое для сохранения и конвертации
        path (str): Имя файла без расширения (используется для формирования имени файла)

    Исключения:
        OSError: Если возникают ошибки при создании директорий или записи файлов

    Пример:
        save_html_and_md("<h1>Hello</h1>", "intro")
    """
    os.makedirs(HTML_DIR, exist_ok=True)
    os.makedirs(MD_DIR, exist_ok=True)

    html_file = os.path.join(HTML_DIR, f"{path}.html")
    md_file = os.path.join(MD_DIR, f"{path}.md")

    with open(html_file, "w", encoding="utf-8") as f:
        f.write(content)

    md_text = md(content, heading_style="ATX")
    with open(md_file, "w", encoding="utf-8") as f:
        f.write(md_text)
