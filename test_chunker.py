import unittest
from typing import List, Dict
from main import chunk_documents_and_code

class TestChunker(unittest.TestCase):
    def setUp(self):
        self.test_dir = "./test_data"
        self.max_chunk_size = 500

    def test_chunking_output(self):
        chunks = chunk_documents_and_code(self.test_dir, self.max_chunk_size)

        self.assertIsInstance(chunks, list, "Результат должен быть списком чанков")
        self.assertGreater(len(chunks), 0, "Должны быть сгенерированы чанки")

        for chunk in chunks:
            self.assertIn('content', chunk)
            self.assertIn('source', chunk)
            self.assertIn('chunk_type', chunk)

            self.assertIsInstance(chunk['content'], str)
            self.assertIsInstance(chunk['source'], str)
            self.assertIn(chunk['chunk_type'], ['code', 'documentation'])

            self.assertLessEqual(len(chunk['content']), self.max_chunk_size + 10)

        chunk_types = set(chunk['chunk_type'] for chunk in chunks)
        self.assertTrue('code' in chunk_types)
        self.assertTrue('documentation' in chunk_types)

if __name__ == "__main__":
    unittest.main()
