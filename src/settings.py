from pydantic_settings import BaseSettings, SettingsConfigDict, SecretStr
from functools import lru_cache
from langchain_groq import Chat_Groq

class Settings(BaseSettings):
    DB_URL: str = "sqlite:///jobs.db"
    
    telegram_bot_token: str
    telegram_chat_id: str
    openai_api_key: str
    LLM: str = "llama-3.3-70b-versatile"
    min_ai_score: int = 7

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

@lru_cache()
def get_settings() -> Settings:
    return Settings()

class LLMFactory:
    @staticmethod
    @lru_cache(maxsize=1)
    def get_llm(temperature: float = 0.0):
        settings = get_settings()
        
        base_llm = ChatGroq(
            model=settings.LLM,
            api_key=SecretStr(settings.GROQ_API_KEY),
            temperature=temperature,
            max_retries=3,
        )
        return base_llm