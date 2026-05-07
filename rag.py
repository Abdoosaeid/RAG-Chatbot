"""
RAG Module — Document processing, Google embeddings, vector store, and retriever tool.

Handles the full ingestion pipeline:
  PDF bytes → text extraction → chunking → Google embeddings → vector store → retriever tool

Uses ONLY Google AI services. No OpenAI dependencies.
"""

from __future__ import annotations

import io
import logging
import os
from typing import Optional

from dotenv import load_dotenv
load_dotenv()

from langchain_core.documents import Document
from langchain_core.tools import tool
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
from langchain_community.vectorstores import FAISS

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 0. API Key Validation
# ---------------------------------------------------------------------------

def _ensure_google_api_key() -> None:
    """Validate that GOOGLE_API_KEY is set in the environment.

    Raises:
        ValueError: If the key is missing.
    """
    if not os.environ.get("GOOGLE_API_KEY"):
        raise ValueError(
            "GOOGLE_API_KEY is not set. "
            "Please add it to your .env file or set it as an environment variable."
        )


# ---------------------------------------------------------------------------
# 1. PDF Ingestion
# ---------------------------------------------------------------------------

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract all text from a PDF file given its raw bytes.

    Args:
        pdf_bytes: Raw content of the PDF file.

    Returns:
        Concatenated text from every page.

    Raises:
        ValueError: If the PDF contains no extractable text.
    """
    reader = PdfReader(io.BytesIO(pdf_bytes))
    texts: list[str] = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text and page_text.strip():
            texts.append(page_text.strip())

    full_text = "\n\n".join(texts)
    if not full_text.strip():
        raise ValueError(
            "The uploaded PDF contains no extractable text. "
            "It may be a scanned image or an empty document."
        )
    logger.info("Extracted %d characters from PDF (%d pages)", len(full_text), len(reader.pages))
    return full_text


# ---------------------------------------------------------------------------
# 2. Text Splitting
# ---------------------------------------------------------------------------

def split_text(text: str) -> list[Document]:
    """Split raw text into overlapping chunks suitable for embedding.

    Uses RecursiveCharacterTextSplitter with:
      - chunk_size  = 1000 characters
      - overlap     = 200 characters
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.create_documents([text])
    logger.info("Split text into %d chunks", len(chunks))
    return chunks


# ---------------------------------------------------------------------------
# 3. Embeddings (Google AI)
# ---------------------------------------------------------------------------

def get_embeddings() -> GoogleGenerativeAIEmbeddings:
    """Return a Google Generative AI embeddings instance.

    Uses the 'models/embedding-001' model.
    Requires GOOGLE_API_KEY in the environment.
    """
    _ensure_google_api_key()
    return GoogleGenerativeAIEmbeddings(model="models/embedding-001")


# ---------------------------------------------------------------------------
# 4. Vector Store
# ---------------------------------------------------------------------------

def build_vector_store(documents: list[Document]) -> FAISS:
    """Create a FAISS vector store from a list of Document chunks.

    Args:
        documents: Chunked documents to index.

    Returns:
        A FAISS vector store instance ready for retrieval.
    """
    embeddings = get_embeddings()
    vector_store = FAISS.from_documents(documents, embeddings)
    logger.info("Built FAISS vector store with %d documents", len(documents))
    return vector_store


# ---------------------------------------------------------------------------
# 5. Full Ingestion Pipeline
# ---------------------------------------------------------------------------

def ingest_pdf(pdf_bytes: bytes) -> FAISS:
    """Run the full ingestion pipeline: PDF → text → chunks → vector store.

    Args:
        pdf_bytes: Raw bytes of the uploaded PDF.

    Returns:
        A FAISS vector store containing the indexed chunks.
    """
    _ensure_google_api_key()
    text = extract_text_from_pdf(pdf_bytes)
    chunks = split_text(text)
    vector_store = build_vector_store(chunks)
    return vector_store


# ---------------------------------------------------------------------------
# 6. Retriever Tool
# ---------------------------------------------------------------------------

# Module-level reference so the @tool function can access the vector store
# after it is initialized via `set_retriever_store`.
_vector_store: Optional[FAISS] = None


def set_retriever_store(vector_store: FAISS) -> None:
    """Set the global vector store used by the retrieve_docs tool.

    Must be called once after PDF ingestion, before the agent runs.
    """
    global _vector_store
    _vector_store = vector_store
    logger.info("Retriever tool bound to vector store")


@tool
def retrieve_docs(query: str) -> str:
    """Retrieve relevant document chunks from the indexed PDF based on a query.

    Use this tool when you need factual information from the uploaded document
    to answer the user's question.

    Args:
        query: The search query to find relevant passages.

    Returns:
        Concatenated text of the most relevant document chunks.
    """
    if _vector_store is None:
        return "No document has been indexed. Please upload a PDF first."

    retriever = _vector_store.as_retriever(search_kwargs={"k": 4})
    docs = retriever.invoke(query)

    if not docs:
        return "No relevant documents found for the given query."

    context = "\n\n---\n\n".join(doc.page_content for doc in docs)
    logger.info("Retrieved %d chunks for query: %s", len(docs), query[:80])
    return context
