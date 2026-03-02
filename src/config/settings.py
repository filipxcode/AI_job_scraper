from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
from functools import lru_cache
from langchain_groq import ChatGroq

class Settings(BaseSettings):
    DB_URL: str = "sqlite:///jobs.db"
    
    TELEGRAM_BOT_API_KEY: str = ""
    TELEGRAM_CHAT_ID: str = ""
    LLM: str = "llama-3.3-70b-versatile"
    min_ai_score: int = 7
    GROQ_API_KEY: str = ""
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

@lru_cache()
def get_settings() -> Settings:
    return Settings()

class LLMFactory:
    @staticmethod
    @lru_cache(maxsize=1)
    def get_llm(temperature: float = 0.0):
        settings = get_settings()

        if not settings.GROQ_API_KEY:
            raise RuntimeError("GROQ_API_KEY is not set (required for --mode llm/all)")
        
        base_llm = ChatGroq(
            model=settings.LLM,
            api_key=SecretStr(settings.GROQ_API_KEY),
            temperature=temperature,
            max_retries=3,
        )
        return base_llm