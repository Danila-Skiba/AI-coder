import os
from pathlib import Path
from typing import List, Optional, Tuple
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain_gigachat.embeddings.gigachat import GigaChatEmbeddings

# -- Класс для чанкинга кода и документации с метаданными --
class CodeDocChunker:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 100):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

    def chunk_code_file(self, text: str, file_id: str, relative_path: str) -> List[Document]:
        chunks = self.text_splitter.split_text(text)
        documents = []
        for i, chunk in enumerate(chunks):
            metadata = {
                "file_id": file_id,
                "chunk_index": i,
                "type": "code",
                "relative_path": relative_path,
                "related_docs": self.find_related_docs_for_chunk(file_id, chunk),
            }
            documents.append(Document(page_content=chunk, metadata=metadata))
        return documents

    def chunk_doc_file(self, text: str, doc_id: str, relative_path: str) -> List[Document]:
        chunks = self.text_splitter.split_text(text)
        documents = []
        for i, chunk in enumerate(chunks):
            metadata = {
                "doc_id": doc_id,
                "chunk_index": i,
                "type": "doc",
                "relative_path": relative_path,
            }
            documents.append(Document(page_content=chunk, metadata=metadata))
        return documents

    def find_related_docs_for_chunk(self, file_id: str, chunk_text: str) -> List[str]:
        # TODO: реализовать алгоритм поиска связанных документов
        return []

    def load_files_and_chunk(
        self,
        code_dir: Optional[Path] = None,
        doc_dir: Optional[Path] = None,
        code_exts: Optional[List[str]] = None,
        doc_exts: Optional[List[str]] = None
    ) -> List[Document]:
        """
        Загрузка файлов из директорий с нужными расширениями и чанкирование с метаданными.
        """
        code_exts = code_exts or [".py", ".js", ".java"]  # Можно расширять
        doc_exts = doc_exts or [".md", ".txt", ".rst"]

        documents = []

        if code_dir is not None:
            for filepath in code_dir.rglob("*"):
                if filepath.suffix.lower() in code_exts:
                    try:
                        text = filepath.read_text(encoding="utf-8")
                        file_id = filepath.name
                        rel_path = str(filepath.relative_to(code_dir))
                        documents.extend(self.chunk_code_file(text, file_id, rel_path))
                    except Exception as e:
                        print(f"Ошибка чтения кода файла {filepath}: {e}")

        if doc_dir is not None:
            for filepath in doc_dir.rglob("*"):
                if filepath.suffix.lower() in doc_exts:
                    try:
                        text = filepath.read_text(encoding="utf-8")
                        doc_id = filepath.name
                        rel_path = str(filepath.relative_to(doc_dir))
                        documents.extend(self.chunk_doc_file(text, doc_id, rel_path))
                    except Exception as e:
                        print(f"Ошибка чтения документа {filepath}: {e}")

        return documents


# -- Обёртка для FAISS с методами сохранения и поиска --
class FAISSVectorStoreWithMetadata:
    def __init__(self, embeddings, vector_store_path="vector_store"):
        self.embeddings = embeddings
        self.vector_store_path = vector_store_path
        self.vector_store = None

    def create_vector_store(self, documents: List[Document]) -> None:
        if not documents:
            raise ValueError("Documents list is empty")
        self.vector_store = FAISS.from_documents(documents, self.embeddings)

    def save_vector_store(self)-> None:
        if self.vector_store is None:
            raise ValueError("Vector store not initialized")
        self.vector_store.save_local(self.vector_store_path)

    def load_vector_store(self) -> bool:
        if os.path.exists(self.vector_store_path):
            try:
                self.vector_store = FAISS.load_local(
                    self.vector_store_path, self.embeddings, allow_dangerous_deserialization=True
                )
                return True
            except Exception as e:
                print(f"Error loading vector store: {e}")
                return False
        return False

    def get_retriever(self, search_kwargs: Optional[dict] = None, k: int = 5):
        if self.vector_store is None:
            raise ValueError("Vector store not initialized")
        search_kwargs = search_kwargs or {"k": k}
        return self.vector_store.as_retriever(search_kwargs=search_kwargs)

    def search(self, query: str, k: int = 5) -> Tuple[List[Document], object]:
        """
        Возвращает кортеж (список документов, retriever)
        """
        retriever = self.get_retriever({"k": k})
        results = retriever.get_relevant_documents(query)
        return results, retriever

