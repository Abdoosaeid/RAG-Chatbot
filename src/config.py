from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    
    GOOGLE_API_KEY: str
    LLM_MODEL: str = "gemini-2.5-flash"
    LLM_TIMEOUT: int = 60
    LLM_MAX_RETRIES: int = 2
    LLM_MAX_TOKENS: int = 2048
    LLM_TEMPERATURE: float = 0.2
    
    LANGCHAIN_API_KEY: str | None = None
    LANGCHAIN_TRACING: bool = False
    LANGCHAIN_ENDPOINT: str = "https://api.smith.langchain.com"
    LANGCHAIN_PROJECT: str = "Chatbot"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"


def get_settings() -> Settings:
    return Settings()