from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    elasticsearch_url: str = "http://elasticsearch:9200"
    elasticsearch_index: str = "documents"

    redis_url: str = "redis://redis:6379"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()
