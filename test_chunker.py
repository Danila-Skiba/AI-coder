import unittest
from main import chunk_documents_and_code

class TestChunker(unittest.TestCase):
    def setUp(self):
        self.doc_text = """# Документация проекта
## foo

Функция foo выводит приветствие.

## Bar

Класс Bar содержит метод method.
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

        self.assertIsInstance(chunks, list, "Результат должен быть списком чанков")
        self.assertGreater(len(chunks), 0, "Должны быть сгенерированы чанки")

        for chunk in chunks:
            self.assertIn('content', chunk)
            self.assertIn('source', chunk)
            self.assertIn('chunk_type', chunk)

            self.assertIsInstance(chunk['content'], str)
            self.assertIsInstance(chunk['source'], str)
            self.assertIn(chunk['chunk_type'], ['code', 'documentation'])

        chunk_types = set(chunk['chunk_type'] for chunk in chunks)
        self.assertIn('code', chunk_types)
        self.assertIn('documentation', chunk_types)

        linked_chunks_exist = any(len(chunk.get('linked_chunks', [])) > 0 for chunk in chunks)
        self.assertTrue(linked_chunks_exist, "Должна быть хотя бы одна связь между чанками")

if __name__ == "__main__":
    unittest.main()
