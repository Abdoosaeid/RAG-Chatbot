import os
from langchain_community.document_loaders import PyPDFLoader,TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings

def load_documents(DATA_PATH = "Data"):
    documents = []

    for file_name in os.listdir(DATA_PATH):

        file_path = os.path.join(DATA_PATH, file_name)

        # PDF
        if file_name.endswith(".pdf"):
            loader = PyPDFLoader(file_path)
            documents.extend(loader.load())

        # TXT
        elif file_name.endswith(".txt"):
            loader = TextLoader(file_path, encoding="utf-8")
            documents.extend(loader.load())


def split_documents(documents):

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150
    )
    doc_splits = text_splitter.split_documents(documents)   

    return doc_splits

def create_vector_store(doc_splits):

    embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")

    vectorstore = InMemoryVectorStore.from_documents(
            documents=doc_splits, embedding=embeddings
        )

     
    return vectorstore 


def create_vector_store():
    documents = load_documents()
    doc_splits = split_documents(documents)
    vectorstore = create_vector_store(doc_splits)

    return vectorstore