import json
from chunkers.doc_chunker import DocChunker
from chunkers.code_chunker import CodeChunker

def chunk_documents_and_code(doc_text, code_text, doc_filename, code_filename):
    doc_chunks = DocChunker(doc_text, doc_filename).chunk()
    code_chunks = CodeChunker(code_text, code_filename).chunk()

    # Связываем чанки с одинаковым именем секции
    doc_map = {chunk["section"]: chunk for chunk in doc_chunks}
    code_map = {chunk["section"]: chunk for chunk in code_chunks}

    for sec, code_chunk in code_map.items():
        if sec in doc_map:
            # Добавляем ссылки в обе стороны
            code_chunk["linked_chunks"].append(doc_map[sec]["id"])
            doc_map[sec]["linked_chunks"].append(code_chunk["id"])

    # Возвращаем объединённый список чанков
    return doc_chunks + code_chunks

if __name__ == "__main__":
    doc_text = """# Документация проекта
## foo

Функция foo выводит приветствие.

## Bar

Класс Bar содержит метод method.
"""
    code_text = """def foo():
    print("Hello")

class Bar:
    def method(self):
        pass
"""

    chunks = chunk_documents_and_code(doc_text, code_text, "sample.md", "sample.py")

    # Сохраняем чанки в файл chunks.jsonl
    with open("chunks.jsonl", "w", encoding="utf-8") as f:
        for chunk in chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")

    print("Чанки сохранены в файл chunks.jsonl")
