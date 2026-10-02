import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Qnexus Backend"
    ENV: str = "development"
    PORT: int = 8000
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "qnexus_db"
    PINECONE_API_KEY: str = ""
    PINECONE_INDEX_NAME: str = "qnexus-questions"
    PINECONE_CLOUD: str = "aws"
    PINECONE_REGION: str = "us-east-1"
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    FRONTEND_URL: str = "http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
