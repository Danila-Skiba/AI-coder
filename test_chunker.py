import unittest
import os
import json
from main import chunk_documents_and_code  # импорт функции из твоего main.py

class TestChunker(unittest.TestCase):
    def setUp(self):
        # Папка с тестовыми файлами
        self.test_dir = "./test_data"
        self.max_chunk_size = 500  # пример, как в основном коде

    def test_chunking_output(self):
        chunks = chunk_documents_and_code(self.test_dir, self.max_chunk_size)
        
        self.assertIsInstance(chunks, list, "Результат должен быть списком чанков")
        self.assertGreater(len(chunks), 0, "Должны быть сгенерированы чанки")

        for chunk in chunks:
            # Проверяем, что есть все необходимые поля
            self.assertIn('content', chunk)
            self.assertIn('source', chunk)
            self.assertIn('chunk_type', chunk)

            # Проверяем типы полей
            self.assertIsInstance(chunk['content'], str)
            self.assertIsInstance(chunk['source'], str)
            self.assertIn(chunk['chunk_type'], ['code', 'documentation'])

            # Проверяем размер чанка (длина контента)
            self.assertLessEqual(len(chunk['content']), self.max_chunk_size + 10)  # небольшая погрешность

        # Проверяем, что есть чанки как кода, так и документации
        chunk_types = set(chunk['chunk_type'] for chunk in chunks)
        self.assertTrue('code' in chunk_types)
        self.assertTrue('documentation' in chunk_types)

if __name__ == "__main__":
    unittest.main()
