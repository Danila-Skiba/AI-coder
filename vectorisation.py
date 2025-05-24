import os
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from langchain.docstore.document import Document
from langchain.vectorstores import FAISS
from langchain_gigachat.embeddings.gigachat import GigaChatEmbeddings
import pickle

class VectorStore(ABC):
    
    def __init__(self, embeddings: GigaChatEmbeddings, vector_store_path: str = "vector_store"):

        self.embeddings = embeddings
        self.vector_store_path = vector_store_path
        self.vector_store = None

    @abstractmethod
    def create_vector_store(self, documents: List[Document]) -> None:
        pass

    @abstractmethod
    def search(self, query: str, k: int = 4) -> List[Document]:
        pass

    @abstractmethod
    def save_vector_store(self) -> None:
        pass

    @abstractmethod
    def load_vector_store(self) -> bool:
        pass

class FAISSVectorStore(VectorStore):
    
    def __init__(self, embeddings: GigaChatEmbeddings, vector_store_path: str = "vector_store"):
        super().__init__(embeddings, vector_store_path)
        self.vector_store = None

    def create_vector_store(self, documents: List[Document]) -> None:
        if not documents:
            raise ValueError("Список документов не может быть пустым")
        self.vector_store = FAISS.from_documents(documents, self.embeddings)

    def search(self, query: str, k: int = 4) -> List[Document]:
        """
        Выполняет поиск по запросу в векторной базе.
        
        Args:
            query: Текстовый запрос пользователя.
            k: Количество возвращаемых результатов.
            
        Returns:
            Список релевантных документов.
        """
        if self.vector_store is None:
            raise ValueError("Векторная база не инициализирована")
        return self.vector_store.similarity_search(query, k=k)

    def save_vector_store(self) -> None:
        """Сохраняет векторную базу в файл."""
        if self.vector_store is None:
            raise ValueError("Векторная база не инициализирована")
        self.vector_store.save_local(self.vector_store_path)

    def load_vector_store(self) -> bool:
        try:
            if os.path.exists(self.vector_store_path):
                self.vector_store = FAISS.load_local(self.vector_store_path, self.embeddings, allow_dangerous_deserialization=True)
                return True
            return False
        except Exception as e:
            print(f"Ошибка при загрузке векторной базы: {e}")
            return False

def load_vector_store(vector_store_path: str, embeddings: GigaChatEmbeddings) -> FAISSVectorStore:
    vector_store = FAISSVectorStore(embeddings, vector_store_path)
    if not vector_store.load_vector_store():
        print("Векторная база не найдена, требуется создать новую")
    return vector_store

def save_vector_store(vector_store: FAISSVectorStore) -> None:
    vector_store.save_vector_store()