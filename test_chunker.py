import unittest
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

    def test_chunking_output(self):
        chunks = chunk_documents_and_code(
            self.doc_text,
            self.code_text,
            self.doc_filename,
            self.code_filename
        )

        self.assertIsInstance(chunks, list)
        self.assertGreater(len(chunks), 0)

        for chunk in chunks:
            self.assertIn('content', chunk)
            self.assertIn('source', chunk)
            self.assertIn('chunk_type', chunk)

        # Проверка, что есть связь между doc и code
        linked_doc_chunks = [c for c in chunks if c['chunk_type'] == 'documentation' and len(c.get('linked_chunks', [])) > 0]
        linked_code_chunks = [c for c in chunks if c['chunk_type'] == 'code' and len(c.get('linked_chunks', [])) > 0]

        self.assertTrue(len(linked_doc_chunks) > 0)
        self.assertTrue(len(linked_code_chunks) > 0)

if __name__ == "__main__":
    unittest.main()
