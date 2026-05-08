from langchain.tools import tool
from rag_pipeline import create_vector_store 

@tool
def retrieve_documents(query: str) -> str:
    """
    Retrieve relevant information from uploaded documents.

    Use this tool ONLY when the question requires document context.
    """
    vectorstore = create_vector_store()
    
    results = vectorstore.similarity_search_with_score(
        query,
        k=10
    )

    filtered_docs = []

    for doc, score in results:

        # InMemoryVectorStore:
        # larger score = better

        if score > 0.5:
            filtered_docs.append((doc, score))

    if not filtered_docs:
        return "No relevant information found in the uploaded documents."

    top_docs = filtered_docs[:3]

    output = []

    for i, (doc, score) in enumerate(top_docs):

        source = doc.metadata.get("source", "Unknown")
        page = doc.metadata.get("page", "N/A")

        output.append(
            f"""
                Document {i + 1}
                                
                Source: {source}
                Page: {page}
                
                Content:
                {doc.page_content}
                """
        )

    return "\n\n".join(output)