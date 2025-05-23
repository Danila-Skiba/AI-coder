import os
import json
import argparse
from typing import List, Dict
from chunkers.code_chunker import CodeChunker
from chunkers.doc_chunker import DocChunker

def load_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

def save_chunks(chunks, out_path):
    with open(out_path, "w", encoding="utf-8") as f:
        for chunk in chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")

def link_chunks(code_chunks: List[Dict], doc_chunks: List[Dict]) -> None:
    """
    Для каждого чанка кода ищем документацию с похожим section (имя функции/класса)
    и наоборот.
    Добавляем взаимные ссылки в linked_chunks.
    """
    doc_index = {}
    for doc in doc_chunks:
        key = doc['section'].lower()
        if key not in doc_index:
            doc_index[key] = []
        doc_index[key].append(doc)

    for code in code_chunks:
        code_sec = code['section'].lower()
        linked_docs = doc_index.get(code_sec, [])

        for doc in linked_docs:
            if doc['id'] not in code['linked_chunks']:
                code['linked_chunks'].append(doc['id'])
            if code['id'] not in doc['linked_chunks']:
                doc['linked_chunks'].append(code['id'])

def chunk_documents_and_code(input_dir, max_chunk_size=1000) -> List[Dict]:
    code_chunker = CodeChunker()
    doc_chunker = DocChunker()
    all_chunks = []

    code_chunks = []
    doc_chunks = []

    for root, _, files in os.walk(input_dir):
        for filename in files:
            filepath = os.path.join(root, filename)
            ext = os.path.splitext(filename)[1].lower()

            try:
                content = load_file(filepath)
            except Exception as e:
                print(f"Не удалось прочитать файл {filepath}: {e}")
                continue

            if ext == ".py":
                chunks = code_chunker.chunk_code(content, filename)
                code_chunks.extend(chunks)
            elif ext in [".md", ".rst", ".txt"]:
                chunks = doc_chunker.chunk_doc(content, filename, max_chunk_size)
                doc_chunks.extend(chunks)
            else:
                continue

    link_chunks(code_chunks, doc_chunks)

    all_chunks = code_chunks + doc_chunks
    return all_chunks

def main(input_dir, output_file):
    chunks = chunk_documents_and_code(input_dir)
    save_chunks(chunks, output_file)
    print(f"Всего чанков сохранено: {len(chunks)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Чанкирование кода и документации с привязкой")
    parser.add_argument("--input_dir", type=str, required=True, help="Путь к папке с исходниками и документацией")
    parser.add_argument("--output_file", type=str, required=True, help="Путь к файлу для сохранения чанков JSONL")
    args = parser.parse_args()

    main(args.input_dir, args.output_file)
