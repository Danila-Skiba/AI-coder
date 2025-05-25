import streamlit as st
import os
from pathlib import Path
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_gigachat.chat_models import GigaChat
from langchain_gigachat.embeddings.gigachat import GigaChatEmbeddings
from langchain.embeddings import HuggingFaceEmbeddings
from vectorization.v_a_c import SmartCodeDocSystem, SmartRetriever, create_smart_prompt
import os

from dotenv import load_dotenv
load_dotenv()


st.set_page_config(
    page_title="LangChain RAG Assistant",
    page_icon="🤖",
    layout="wide"
)

st.title("LangChain RAG Assistant")
st.markdown("Задайте вопрос о библиотеке LangChain")

API_KEY = os.getenv("GIGACHAT_CREDENTIALS")
VECTOR_STORE_PATH = os.path.join(os.path.dirname(__file__), "langchain_vector_store")


@st.cache_resource
def initialize_rag_system():
    """Инициализация RAG системы с кэшированием"""
    try:
        embeddings = GigaChatEmbeddings(
            credentials=API_KEY,
            scope="GIGACHAT_API_PERS",
            verify_ssl_certs=False,
        )

        system = SmartCodeDocSystem(embeddings, chunk_size=600, chunk_overlap=100)
        
        system.load_vector_store(VECTOR_STORE_PATH)

        llm = GigaChat(
            credentials=API_KEY,
            verify_ssl_certs=False,
            model="GigaChat-Pro"
        )

        smart_retriever = SmartRetriever(smart_system=system, k=150)
        prompt = create_smart_prompt()
        document_chain = create_stuff_documents_chain(llm=llm, prompt=prompt)
        retrieval_chain = create_retrieval_chain(smart_retriever, document_chain)

        return retrieval_chain, system

    except Exception as e:
        st.error(f"Ошибка при инициализации системы: {e}")
        return None, None

def main():
    with st.spinner("Загрузка системы..."):
        retrieval_chain, system = initialize_rag_system()

    if retrieval_chain and system:
        st.success("Система готова к работе!")

        with st.expander("Примеры вопросов"):
            example_questions = [
                "How to use FAISS vectorstore in LangChain?",
                "What is LangSmith?",
                "Какие векторные базы поддерживает LangChain?",
                "Как реализовать собственную цепочку?",
                "Как использовать PromptTemplate?"
            ]

            for i, example in enumerate(example_questions):
                if st.button(f"{example}", key=f"example_{i}"):
                    st.session_state.user_question = example

        user_question = st.text_area(
            "Введите ваш вопрос:",
            value=st.session_state.get('user_question', ''),
            height=100,
            placeholder="Например: How to use FAISS vectorstore in LangChain?"
        )

        col1, col2, col3 = st.columns([1, 1, 4])
        with col1:
            ask_button = st.button("Задать вопрос", type="primary")

        if ask_button and user_question.strip():
            with st.spinner("Поиск ответа..."):
                try:
                    response = retrieval_chain.invoke({'input': user_question})

                    search_result = system.smart_search(user_question, k=150)

                    st.markdown("---")
                    st.subheader("Ответ")
                    st.markdown(response['answer'])

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Тип поиска", search_result.search_type)
                    with col2:
                        code_count = len([d for d in search_result.documents if d.metadata.get('type') == 'code'])
                        st.metric("Документы кода", code_count)
                    with col3:
                        doc_count = len([d for d in search_result.documents if d.metadata.get('type') == 'doc'])
                        st.metric("Документация", doc_count)

                    with st.expander("Источники информации"):
                        for i, doc in enumerate(response['context']):
                            st.markdown(f"**Источник {i + 1}:**")

                            doc_type = doc.metadata.get('type', 'unknown')
                            if doc_type == 'code':
                                st.markdown(f"- **Тип:** Исходный код")
                            elif doc_type == 'doc':
                                st.markdown(f"- **Тип:** Документация")
                            else:
                                st.markdown(f"- **Тип:** Неизвестно")

                            if 'file' in doc.metadata:
                                st.markdown(f"- **Файл:** {doc.metadata['file']}")

                            if 'source' in doc.metadata:
                                st.markdown(f"- **Источник:** {doc.metadata['source']}")

                            st.markdown(f"- **Фрагмент:**")
                            content_preview = doc.page_content[:400] + "..." if len(
                                doc.page_content) > 400 else doc.page_content
                            st.code(content_preview, language="python" if doc_type == 'code' else "markdown")
                            st.markdown("---")

                    with st.expander("Детали поиска"):
                        st.markdown(f"**Тип поиска:** {search_result.search_type}")
                        st.markdown(f"**Всего найдено документов:** {len(search_result.documents)}")

                        if hasattr(search_result, 'scores') and search_result.scores:
                            st.markdown("**Релевантность документов:**")
                            for i, score in enumerate(search_result.scores):
                                st.progress(min(score, 1.0), text=f"Документ {i + 1}: {score:.3f}")

                except Exception as e:
                    st.error(f"Произошла ошибка при обработке вопроса: {e}")
                    st.error("Попробуйте переформулировать вопрос или обратитесь к администратору")

                    with st.expander("Отладочная информация"):
                        st.code(str(e))

        elif ask_button:
            st.warning("Пожалуйста, введите вопрос")

    else:
        st.error("Не удалось инициализировать систему. Проверьте:")
        st.error("- Наличие векторного хранилища по пути: " + VECTOR_STORE_PATH)
        st.error("- Правильность API ключа GigaChat")
        st.error("- Доступность модуля vectorization.v_a_c")


if 'user_question' not in st.session_state:
    st.session_state.user_question = ''

with st.sidebar:
    st.markdown("### О приложении")
    st.markdown("""
    Этот ассистент поможет вам найти ответы на вопросы о библиотеке LangChain.
    
    Просто введите ваш вопрос и получите подробный ответ!
    """)

    st.markdown("---")
    st.markdown("**Совет:** Формулируйте вопросы конкретно для получения более точных ответов.")

if __name__ == "__main__":
    main()
