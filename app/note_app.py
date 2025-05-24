from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chat_models.gigachat import GigaChat
from langchain.chains import create_retrieval_chain
from langchain_gigachat.chat_models import GigaChat
from langchain_gigachat.embeddings.gigachat import GigaChatEmbeddings
from pathlib import Path
from vectorization.v_a_c import *


API_KEY = "YjllY2FhYjgtNGRlMC00MDA4LWIwZmYtNjdlNjY0ZmI5OTc4OmRkMjZhOWFjLThhNTctNGM3ZC1iZjFkLWQ3NGY1NmRjNTQzMQ=="
CODE_DIR = Path("..\\data\\code")
DOC_DIR = Path("..\\data\\documentation")
VECTOR_STORE_PATH = "langchain_vector_store"

embedding=GigaChatEmbeddings(
        credentials=API_KEY,
        scope="GIGACHAT_API_PERS",
        verify_ssl_certs=False,
)

embeddings = GigaChatEmbeddings(
    credentials=API_KEY,
    verify_ssl_certs=False
)

system = SmartCodeDocSystem(embeddings, chunk_size=600, chunk_overlap=100)

system.load_vector_store(VECTOR_STORE_PATH)

llm = GigaChat(
    credentials=API_KEY,
    verify_ssl_certs=False,
)

smart_retriever = SmartRetriever(smart_system=system, k=3)

prompt = create_smart_prompt()
document_chain = create_stuff_documents_chain(llm=llm, prompt=prompt)
retrieval_chain = create_retrieval_chain(smart_retriever, document_chain)

query = "How to use FAISS vectorstore in LangChain?"

# пример запроса модели
try:
    response = retrieval_chain.invoke({"input": query})
    
    print("ОТВЕТ:")
    print(response["answer"])
    
    search_result = system.smart_search(query, k=3)
    print(f"\nИНФО О ПОИСКЕ:")
    print(f"Тип поиска: {search_result.search_type}")
    print(f"Найдено документов: {len(search_result.documents)}")
    
    code_count = len([d for d in search_result.documents if d.metadata.get('type') == 'code'])
    doc_count = len([d for d in search_result.documents if d.metadata.get('type') == 'doc'])
    print(f"Код: {code_count}, Документация: {doc_count}")
    
except Exception as e:
    print(f"Ошибка: {e}")

