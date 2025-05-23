import unittest
import json
from main import chunk_documents_and_code

class TestChunker(unittest.TestCase):
    def setUp(self):
        self.doc_text = """# Документация проекта

## foo

Функция foo выводит приветствие.

## Bar

Класс Bar содержит метод method.

### method

Описание метода method.
"""

        self.code_text = """def foo():
    print("Hello")

class Bar:
    def method(self):
        pass
"""

        self.doc_filename = "sample.md"
        self.code_filename = "sample.py"

    def save_chunks_to_file(self, chunks, filename="chunks.jsonl"):
        with open(filename, "w", encoding="utf-8") as f:
            for chunk in chunks:
                json_line = json.dumps(chunk, ensure_ascii=False)
                f.write(json_line + "\n")

    def test_basic_chunking(self):
        doc_chunks, code_chunks = chunk_documents_and_code(
            self.doc_text,
            self.code_text,
            self.doc_filename,
            self.code_filename
        )

        all_chunks = doc_chunks + code_chunks

        # Сохраняем в файл
        self.save_chunks_to_file(all_chunks)

        self.assertIsInstance(all_chunks, list)
        self.assertGreater(len(all_chunks), 0)

        for chunk in all_chunks:
            self.assertIn('content', chunk)
            self.assertIn('source', chunk)
            self.assertIn('chunk_type', chunk)

        linked_doc_chunks = [c for c in doc_chunks if len(c.get('linked_chunks', [])) > 0]
        linked_code_chunks = [c for c in code_chunks if len(c.get('linked_chunks', [])) > 0]

        self.assertTrue(len(linked_doc_chunks) > 0)
        self.assertTrue(len(linked_code_chunks) > 0)

    def test_complex_chunking(self):
        doc_text = """# Документация проекта

## foo

Функция foo выводит приветствие.

## Bar

Класс Bar содержит методы:

### method

Описание метода method.

### _private_method

Приватный метод класса Bar.

## Baz

Класс Baz содержит вложенный класс Nested.

### Nested

Вложенный класс Nested внутри Baz.

#### nested_method

Метод nested_method класса Nested.
"""

        code_text = """def foo():
    print("Hello")

class Bar:
    def method(self):
        print("Method called")

    def _private_method(self):
        print("Private method")

class Baz:
    class Nested:
        def nested_method(self):
            print("Nested method")
"""

        doc_filename = "sample.md"
        code_filename = "sample.py"

        doc_chunks, code_chunks = chunk_documents_and_code(doc_text, code_text, doc_filename, code_filename)
        all_chunks = doc_chunks + code_chunks

        # Сохраняем в файл
        self.save_chunks_to_file(all_chunks)

        self.assertTrue(any("foo" in c.get('section', '') for c in all_chunks))
        self.assertTrue(any("Bar" in c.get('section', '') for c in all_chunks))
        self.assertTrue(any("method" in c.get('section', '') for c in all_chunks))
        self.assertTrue(any("Nested" in c.get('section', '') for c in all_chunks))


if __name__ == "__main__":
    unittest.main()
