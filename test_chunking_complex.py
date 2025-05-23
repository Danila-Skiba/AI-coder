import json

from main import chunk_documents_and_code

def test_complex_chunking():
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

    chunks = chunk_documents_and_code(doc_text, code_text, "sample.md", "sample.py")

    # Запись в chunks.jsonl — по одному JSON-объекту на строку
    with open("chunks.jsonl", "w", encoding="utf-8") as f:
        for chunk in chunks:
            json_line = json.dumps(chunk, ensure_ascii=False)
            f.write(json_line + "\n")

    # Основные проверки
    assert any("foo" in chunk['section'] for chunk in chunks)
    assert any("Bar" in chunk['section'] for chunk in chunks)
    assert any("method" in chunk['section'] for chunk in chunks)
    assert any("Nested" in chunk['section'] for chunk in chunks)
