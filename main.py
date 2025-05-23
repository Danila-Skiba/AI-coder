import re
import json

from chunkers.doc_chunker import DocChunker
from chunkers.code_chunker import CodeChunker

def normalize_key(s):
    s = s.lower().strip()
    s = re.sub(r"\b(метод|функция|класс|class|def|function|method)\b", "", s)
    s = re.sub(r"[\s\-_]+", "", s)
    return s

def extract_names_from_section(section):
    return section.split(" > ")[-1].strip()

def chunk_documents_and_code(doc_text, code_text, doc_filename, code_filename):
    doc_chunks = DocChunker(doc_text, doc_filename).chunk()
    code_chunks = CodeChunker(code_text, code_filename).chunk()

    doc_index = {}
    for chunk in doc_chunks:
        name = extract_names_from_section(chunk["section"])
        norm_name = normalize_key(name)
        doc_index.setdefault(norm_name, []).append(chunk)

    code_index = {}
    for chunk in code_chunks:
        norm_name = normalize_key(chunk["section"])
        code_index.setdefault(norm_name, []).append(chunk)

    # Связываем чанки
    for norm_name, code_chunks_list in code_index.items():
        if norm_name in doc_index:
            doc_chunks_list = doc_index[norm_name]
            for code_chunk in code_chunks_list:
                for doc_chunk in doc_chunks_list:
                    if doc_chunk["id"] not in code_chunk["linked_chunks"]:
                        code_chunk["linked_chunks"].append(doc_chunk["id"])
                    if code_chunk["id"] not in doc_chunk["linked_chunks"]:
                        doc_chunk["linked_chunks"].append(code_chunk["id"])

    combined = doc_chunks + code_chunks
    return combined

def save_chunks_to_jsonl(chunks, filepath="chunks.jsonl"):
    # Открываем файл в режиме добавления, чтобы записать в существующий
    with open(filepath, "a", encoding="utf-8") as f:
        for chunk in chunks:
            json.dump(chunk, f, ensure_ascii=False)
            f.write("\n")

if __name__ == "__main__":
    # Замените пути на свои файлы с документацией и кодом
    with open("test_data/sample.md", encoding="utf-8") as f:
        doc_text = f.read()
    with open("test_data/sample.py", encoding="utf-8") as f:
        code_text = f.read()

    chunks = chunk_documents_and_code(doc_text, code_text, "sample.md", "sample.py")
    save_chunks_to_jsonl(chunks, "chunks.jsonl")

    # Выводим в консоль только чанки с непустыми linked_chunks
    print("Чанки с непустыми linked_chunks:")
    for c in chunks:
        if c["linked_chunks"]:
            print(f"Chunk id={c['id']} связан с: {c['linked_chunks']}")
