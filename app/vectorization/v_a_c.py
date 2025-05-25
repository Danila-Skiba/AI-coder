import os
import re
from pathlib import Path
from typing import List
from dataclasses import dataclass

from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.schema import BaseRetriever
from langchain.prompts import ChatPromptTemplate
from pydantic import Field


@dataclass
class SearchResult:
    """Результат умного поиска"""
    documents: List[Document]
    search_type: str
    primary_chunks: List[Document]
    related_chunks: List[Document]


class QueryAnalyzer:
    """Анализирует запросы для определения приоритета поиска"""
    
    def __init__(self):
        self.code_keywords = [
            "implementation", "реализация", "как работает", "внутри", 
            "алгоритм", "код", "функция", "метод", "класс", 
            "source", "исходный", "внутренний", "механизм",
            "debug", "отладка", "ошибка", "баг", "how does", "internally"
        ]
        
        self.doc_keywords = [
            "example", "пример", "как использовать", "tutorial", 
            "guide", "руководство", "документация", "инструкция",
            "getting started", "начало работы", "quickstart",
            "demo", "демо", "показать", "usage", "использование", "how to"
        ]
    
    def analyze_query(self, query: str) -> str:
        """Возвращает: code-first, doc-first или balanced"""
        query_lower = query.lower()
        
        code_score = sum(1 for keyword in self.code_keywords if keyword in query_lower)
        doc_score = sum(1 for keyword in self.doc_keywords if keyword in query_lower)
        
        # Дополнительные эвристики
        if any(phrase in query_lower for phrase in ["how does", "как работает"]):
            code_score += 2
        if any(phrase in query_lower for phrase in ["example", "пример", "how to"]):
            doc_score += 2
        if re.search(r'\b(class|function|method|def |import )\b', query_lower):
            code_score += 1
            
        if code_score > doc_score + 1:
            return "code-first"
        elif doc_score > code_score + 1:
            return "doc-first"
        else:
            return "balanced"


class SmartCodeDocSystem:
    """Полная система для работы с кодом и документацией"""
    
    def __init__(self, embeddings, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.embeddings = embeddings
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        self.query_analyzer = QueryAnalyzer()
        self.vector_store = None
        self.documents = []

    def load_and_process_files(self, code_dir: Path, doc_dir: Path) -> List[Document]:
        """Загружает файлы из директорий и создает чанки"""
        
        print("Загрузка и обработка файлов...")
        documents = []
        
        # Обрабатываем файлы кода (.py)
        print(f"Обработка кода из {code_dir}")
        code_files = list(code_dir.rglob("*.py"))
        for i, filepath in enumerate(code_files):
            try:
                text = filepath.read_text(encoding="utf-8")
                if len(text.strip()) < 10:  # Пропускаем слишком короткие файлы
                    continue
                    
                chunks = self.text_splitter.split_text(text)
                for j, chunk in enumerate(chunks):
                    metadata = {
                        "file_id": filepath.name,
                        "chunk_index": j,
                        "type": "code",
                        "relative_path": str(filepath.relative_to(code_dir)),
                        "content_summary": self._extract_code_summary(chunk)
                    }
                    documents.append(Document(page_content=chunk, metadata=metadata))
                
                if (i + 1) % 10 == 0:
                    print(f"  Обработано {i + 1}/{len(code_files)} файлов кода")
                    
            except Exception as e:
                print(f"Ошибка при чтении {filepath}: {e}")

        print(f"Загружено {len(code_files)} файлов кода")
        
        # Обрабатываем документацию (.md)
        print(f"Обработка документации из {doc_dir}")
        doc_files = list(doc_dir.rglob("*.md"))
        for i, filepath in enumerate(doc_files):
            try:
                text = filepath.read_text(encoding="utf-8")
                if len(text.strip()) < 10:
                    continue
                    
                chunks = self.text_splitter.split_text(text)
                for j, chunk in enumerate(chunks):
                    metadata = {
                        "doc_id": filepath.name,
                        "chunk_index": j,
                        "type": "doc",
                        "relative_path": str(filepath.relative_to(doc_dir)),
                        "content_summary": self._extract_doc_summary(chunk)
                    }
                    documents.append(Document(page_content=chunk, metadata=metadata))
                
                if (i + 1) % 5 == 0:
                    print(f"  Обработано {i + 1}/{len(doc_files)} файлов документации")
                    
            except Exception as e:
                print(f"Ошибка при чтении {filepath}: {e}")

        print(f"Загружено {len(doc_files)} файлов документации")
        
        self.documents = documents
        print(f"Всего создано {len(documents)} чанков")
        print(f"  - Код: {len([d for d in documents if d.metadata['type'] == 'code'])}")
        print(f"  - Документация: {len([d for d in documents if d.metadata['type'] == 'doc'])}")
        
        return documents

    def _extract_code_summary(self, chunk: str) -> str:
        """Извлекает краткое описание из кода"""
        lines = chunk.split('\n')
        summary_parts = []
        
        for line in lines[:15]:
            line = line.strip()
            if line.startswith('class '):
                class_name = line.split('(')[0].replace('class ', '')
                summary_parts.append(f"Class: {class_name}")
            elif line.startswith('def '):
                func_name = line.split('(')[0].replace('def ', '')
                summary_parts.append(f"Function: {func_name}")
            elif '"""' in line or "'''" in line:
                summary_parts.append("Has docstring")
                
        return "; ".join(summary_parts[:3]) if summary_parts else "Code block"

    def _extract_doc_summary(self, chunk: str) -> str:
        """Извлекает краткое описание из документации"""
        lines = chunk.split('\n')
        for line in lines[:5]:
            line = line.strip()
            if line.startswith('#'):
                return f"Section: {line.replace('#', '').strip()}"
            elif len(line) > 30 and not line.startswith('```'):
                return f"Content: {line[:60]}..."
        return "Documentation block"

    def create_vector_store(self, save_path: str = "vector_store"):
        """Создает и сохраняет векторное хранилище"""
        
        if not self.documents:
            raise ValueError("Нет документов для векторизации")
        
        print("Создание векторного хранилища...")
        self.vector_store = FAISS.from_documents(self.documents, self.embeddings)
        
        print(f"Сохранение в {save_path}")
        self.vector_store.save_local(save_path)
        print("Векторное хранилище создано и сохранено")

    def load_vector_store(self, load_path: str = "vector_store") -> bool:
        """Загружает существующее векторное хранилище"""
        
        if os.path.exists(load_path):
            try:
                print(f"Загрузка векторного хранилища из {load_path}")
                self.vector_store = FAISS.load_local(
                    load_path, self.embeddings, allow_dangerous_deserialization=True
                )
                print("Векторное хранилище загружено")
                return True
            except Exception as e:
                print(f"Ошибка загрузки: {e}")
                return False
        return False

    def smart_search(self, query: str, k: int = 6, related_k: int = 2) -> SearchResult:
        """Умный поиск с адаптивным выбором типа контента"""
        
        if self.vector_store is None:
            raise ValueError("Векторное хранилище не инициализировано")
        
        # Анализируем запрос
        search_type = self.query_analyzer.analyze_query(query)
        
        # Получаем больше результатов для лучшей фильтрации
        all_results = self.vector_store.similarity_search(query, k=k*2)
        
        if search_type == "code-first":
            # Приоритет коду, но добавляем документацию
            code_chunks = [d for d in all_results if d.metadata.get("type") == "code"][:k//2+1]
            doc_chunks = [d for d in all_results if d.metadata.get("type") == "doc"][:k//2]
            primary_chunks = code_chunks
            related_chunks = doc_chunks
            
        elif search_type == "doc-first":
            # Приоритет документации, но добавляем код
            doc_chunks = [d for d in all_results if d.metadata.get("type") == "doc"][:k//2+1]
            code_chunks = [d for d in all_results if d.metadata.get("type") == "code"][:k//2]
            primary_chunks = doc_chunks
            related_chunks = code_chunks
            
        else:  # balanced
            # Равномерное распределение
            code_chunks = [d for d in all_results if d.metadata.get("type") == "code"][:k//2]
            doc_chunks = [d for d in all_results if d.metadata.get("type") == "doc"][:k//2]
            primary_chunks = doc_chunks + code_chunks
            related_chunks = []
        
        # Объединяем и убираем дубликаты
        all_documents = primary_chunks + related_chunks
        seen_content = set()
        unique_documents = []
        
        for doc in all_documents:
            content_hash = hash(doc.page_content[:100])  # Используем начало для проверки
            if content_hash not in seen_content:
                seen_content.add(content_hash)
                unique_documents.append(doc)
        
        return SearchResult(
            documents=unique_documents[:k],
            search_type=search_type,
            primary_chunks=primary_chunks,
            related_chunks=related_chunks
        )


class SmartRetriever(BaseRetriever):
    """Ретривер для LangChain, использующий умный поиск"""
    
    # Объявляем поля для Pydantic модели
    smart_system: SmartCodeDocSystem = Field(description="Smart code documentation system")
    k: int = Field(default=6, description="Number of documents to retrieve")
    
    def __init__(self, smart_system: SmartCodeDocSystem, k: int = 6, **kwargs):
        # Инициализируем родительский класс с полями
        super().__init__(smart_system=smart_system, k=k, **kwargs)
    
    def _get_relevant_documents(self, query: str, **kwargs) -> List[Document]:
        search_result = self.smart_system.smart_search(query, k=self.k)
        return search_result.documents
    
    async def _aget_relevant_documents(self, query: str, **kwargs) -> List[Document]:
        return self._get_relevant_documents(query, **kwargs)


def create_smart_prompt() -> ChatPromptTemplate:
    """Создает оптимизированный промпт для работы с кодом и документацией"""
    
    template = '''Ты — эксперт по библиотеке LangChain. У тебя есть доступ к исходному коду и документации библиотеки.

КОНТЕКСТ:
{context}

ИНСТРУКЦИИ:
1. Анализируй предоставленный контекст (код и/или документацию).
2. Если есть код — объясни принципы его работы.
3. Если есть документация — покажи примеры использования.
4. Комбинируй информацию для полного и точного ответа.
5. Уделяй особое внимание **правдоподобности и точности кода**:
   - Проверяй, существует ли используемый API в кодовой базе.
   - Убеждайся, что импорты, сигнатуры функций и параметры соответствуют текущей версии библиотеки.
   - Не придумывай методы, классы или параметры — опирайся на код.
   - Если есть сомнение, лучше объясни, почему что-то может не работать.
6. Будь конкретным, практичным и лаконичным.
7. Указывай источники (файлы, модули), если это помогает понять структуру или происхождение функций.
8. Если документация и код противоречат друг другу — опирайся на код и **явно сообщи пользователю о противоречии и его сути**, без излишней формалистики или размышлений.

ВОПРОС: {input}

ОТВЕТ:
'''
    
    return ChatPromptTemplate.from_template(template)