# config.py
from pydantic_settings import BaseSettings  
# Для pydantic v1: from pydantic import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./altconcept.db"
    SECRET_KEY: str = "change-me-in-prod-please"  
    class Config:
        env_file = ".env"  

settings = Settings()