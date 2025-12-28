import os
import shutil
import uuid
import streamlit as st
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# Базовая папка
BASE_DB_DIR = "chroma_data"
TEMP_DIR = "temp_docs"

# Отключаем предупреждение симлинков
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

@st.cache_resource
def get_embedding_model():
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def save_uploaded_file(uploaded_file):
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)
    
    file_path = os.path.join(TEMP_DIR, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path

def create_vector_db(file_path: str):
    """
    Создает НОВУЮ уникальную базу данных для файла.
    Возвращает: (объект_базы, путь_к_папке)
    """
    # 1. Загрузка и сплит
    if file_path.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
    elif file_path.endswith(".txt"):
        loader = TextLoader(file_path, encoding="utf-8")
    else:
        raise ValueError("Только PDF или TXT")
        
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)
    
    # 2. Генерируем уникальную папку, чтобы Windows не ругалась на занятый файл
    unique_id = str(uuid.uuid4())
    db_path = os.path.join(BASE_DB_DIR, unique_id)
    
    # 3. Создаем базу
    embedding_model = get_embedding_model()
    
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory=db_path
    )
    return vector_store, db_path

def load_existing_db(db_path: str):
    """
    Просто загружает базу с диска, если она уже была создана.
    """
    if not os.path.exists(db_path):
        return None
        
    embedding_model = get_embedding_model()
    vector_store = Chroma(
        persist_directory=db_path, 
        embedding_function=embedding_model
    )
    return vector_store