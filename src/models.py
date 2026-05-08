from langchain_google_genai import ChatGoogleGenerativeAI
from config import get_settings

settings = get_settings()

def get_llm():
    llm = ChatGoogleGenerativeAI(
        model=settings.LLM_MODEL,
        temperature=settings.LLM_TEMPERATURE,
        max_tokens=settings.LLM_MAX_TOKENS,
        timeout=settings.LLM_TIMEOUT,
        max_retries=settings.LLM_MAX_RETRIES,
        google_api_key=settings.GOOGLE_API_KEY
    )
    return llm

