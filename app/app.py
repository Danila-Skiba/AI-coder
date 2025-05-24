import streamlit as st
import os
from pathlib import Path
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.retrievers import BM25Retriever, EnsembleRetriever
from langchain.vectorstores.faiss import FAISS
from langchain_core.documents import Document
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_gigachat.chat_models import GigaChat
from langchain_gigachat.embeddings.gigachat import GigaChatEmbeddings
import chardet
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document


st.set_page_config(
    page_title="LangChain RAG Assistant",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 LangChain RAG Assistant")
st.markdown("Задайте вопрос о библиотеке LangChain")

API_KEY = os.getenv("GIGACHAT_API_KEY", "YjllY2FhYjgtNGRlMC00MDA4LWIwZmYtNjdlNjY0ZmI5OTc4OmRkMjZhOWFjLThhNTctNGM3ZC1iZjFkLWQ3NGY1NmRjNTQzMQ==")
DOC_PATH = "../data/documentation"
CODE_PATH = "../data/code"

DOC_CHUNK_SIZE = 1000
DOC_CHUNK_OVERLAP = 200
CODE_CHUNK_SIZE = 500
CODE_CHUNK_OVERLAP = 100
K_DOCUMENTS = 5

def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        raw_data = f.read(10000)
    result = chardet.detect(raw_data)
    return result['encoding']

def safe_read_text(path):
    encoding = detect_encoding(path)
    return Path(path).read_text(encoding=encoding, errors="ignore")

@st.cache_resource
def initialize_rag_system():
    """Инициализация RAG системы с кэшированием"""
    
    try:
        doc_files = list(Path(DOC_PATH).rglob("*.md"))[:3]
        code_files = list(Path(CODE_PATH).rglob("*.py"))[:3]
        
        if not doc_files and not code_files:
            st.error("Не удалось найти документы для инициализации системы")
            return None, None
        
        doc_splitter = RecursiveCharacterTextSplitter(
            chunk_size=DOC_CHUNK_SIZE, 
            chunk_overlap=DOC_CHUNK_OVERLAP
        )
        code_splitter = RecursiveCharacterTextSplitter(
            separators=["\nclass", "\ndef", "\n"], 
            chunk_size=CODE_CHUNK_SIZE, 
            chunk_overlap=CODE_CHUNK_OVERLAP
        )
        
        docs = []
        for file in doc_files:
            try:
                content = safe_read_text(file)
                chunks = doc_splitter.split_text(content)
                for chunk in chunks:
                    docs.append(Document(
                        page_content=chunk, 
                        metadata={"source": "doc", "file": str(file.name)}
                    ))
            except Exception as e:
                st.warning(f"Ошибка при обработке документации: {e}")
        
        code_docs = []
        for file in code_files:
            try:
                content = safe_read_text(file)
                chunks = code_splitter.split_text(content)
                for chunk in chunks:
                    code_docs.append(Document(
                        page_content=chunk, 
                        metadata={"source": "code", "file": str(file.name)}
                    ))
            except Exception as e:
                st.warning(f"Ошибка при обработке кода: {e}")
        
        documents = docs + code_docs
        
        if not documents:
            st.error("Не удалось загрузить документы")
            return None, None
        
        embedding = GigaChatEmbeddings(
            credentials=API_KEY,
            scope="GIGACHAT_API_PERS",
            verify_ssl_certs=False,
        )
        
        vector_store = FAISS.from_documents(documents, embedding=embedding)
        retriever = vector_store.as_retriever(search_kwargs={"k": K_DOCUMENTS})
        
        llm = GigaChat(
            credentials=API_KEY,
            verify_ssl_certs=False,
        )
        
        prompt = ChatPromptTemplate.from_template('''Ты — технический помощник, работающий с библиотекой LangChain. У тебя есть доступ к документации и к исходному коду библиотеки.

Твоя задача — ответить на вопрос пользователя, используя и документацию, и код. Следуй этим правилам:

---

1. 📄 Если информация взята из документации, укажи, из какого именно документа она была получена. Пример:  
   _"Согласно документации (load_chain.md)..."_

2. 🧩 Если информация взята из исходного кода, укажи, из какого файла она была получена. Пример:  
   _"В коде (loader.py) реализована только цепочка summarize_chain..."_

3. ⚠️ Если документация и код противоречат друг другу, всё равно сформулируй полезный ответ, но обязательно предупреди об этом. Пример:  
   _"Документация (load_chain.md) утверждает, что поддерживаются 3 цепочки, однако в коде (loader.py) реализована только одна. Это потенциальное несоответствие."_

4. ❓ Если ты не уверен, соответствует ли документация коду, также предупреди об этом. Пример:  
   _"Не удалось однозначно проверить, соответствует ли описание в документации (agent_overview.md) текущей реализации кода (agent/base.py). Будьте внимательны."_

5. 💬 Избегай вымышленных деталей — все факты должны быть подтверждены фрагментами из кода или документации.

---

В конце ответа сделай краткое заключение:
- Указан ли источник каждого утверждения?
- Есть ли возможные противоречия?

---

Контекст для ответа:
{context}

Вопрос пользователя: {input}''')
        
        document_chain = create_stuff_documents_chain(
            llm=llm,
            prompt=prompt
        )
        
        retrieval_chain = create_retrieval_chain(retriever, document_chain)
        
        return retrieval_chain, len(documents)
        
    except Exception as e:
        st.error(f"Ошибка при инициализации системы: {e}")
        return None, None

def main():
    with st.spinner("Загрузка системы..."):
        retrieval_chain, doc_count = initialize_rag_system()
    
    if retrieval_chain:
        st.success("✅ Система готова к работе!")
        
        with st.expander("📝 Примеры вопросов"):
            example_questions = [
                "What is LangSmith?",
                "Как агент принимает решение, что делать?",
                "Какие векторные базы поддерживает LangChain?",
                "Что произойдет, если передать неизвестную цепочку в load_chain?",
                "Как реализовать собственную цепочку?",
                "Как использовать PromptTemplate?",
                "Приведи пример загрузки файлов из директории",
                "Какие ошибки бывают в LangChain и когда они возникают?"
            ]
            
            for i, example in enumerate(example_questions):
                if st.button(f"📌 {example}", key=f"example_{i}"):
                    st.session_state.user_question = example
        
        user_question = st.text_area(
            "Введите ваш вопрос:",
            value=st.session_state.get('user_question', ''),
            height=100,
            placeholder="Например: Как использовать векторные хранилища в LangChain?"
        )
        
        col1, col2, col3 = st.columns([1, 1, 4])
        with col1:
            ask_button = st.button("🚀 Задать вопрос", type="primary")
        with col2:
            clear_button = st.button("🗑️ Очистить")
        
        if clear_button:
            st.session_state.user_question = ''
            st.rerun()
        
        if ask_button and user_question.strip():
            with st.spinner("🔍 Поиск ответа..."):
                try:
                    response = retrieval_chain.invoke({'input': user_question})
                    
                    st.markdown("---")
                    st.subheader("🤖 Ответ")
                    st.markdown(response['answer'])
                    
                    with st.expander("📚 Источники информации"):
                        for i, doc in enumerate(response['context']):
                            st.markdown(f"**Источник {i+1}:**")
                            st.markdown(f"- **Тип:** {'Документация' if doc.metadata.get('source') == 'doc' else 'Исходный код'}")
                            if 'file' in doc.metadata:
                                st.markdown(f"- **Файл:** {doc.metadata['file']}")
                            st.markdown(f"- **Фрагмент:**")
                            st.code(doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content)
                            st.markdown("---")
                    
                except Exception as e:
                    st.error(f"Произошла ошибка при обработке вопроса: {e}")
                    st.error("Попробуйте переформулировать вопрос или обратитесь к администратору")
        
        elif ask_button:
            st.warning("⚠️ Пожалуйста, введите вопрос")
    
    else:
        st.error("❌ Не удалось инициализировать систему. Обратитесь к администратору.")

if 'user_question' not in st.session_state:
    st.session_state.user_question = ''

with st.sidebar:
    st.markdown("### ℹ️ О приложении")
    st.markdown("""
    Этот ассистент поможет вам найти ответы на вопросы о библиотеке LangChain.
    
    **Возможности:**
    - Поиск по документации LangChain
    - Анализ исходного кода библиотеки
    - Указание источников информации
    - Выявление несоответствий между документацией и кодом
    
    Просто введите ваш вопрос и получите подробный ответ!
    """)
    
    st.markdown("---")
    st.markdown("**💡 Совет:** Формулируйте вопросы конкретно для получения более точных ответов.")

if __name__ == "__main__":
    main()
