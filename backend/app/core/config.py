from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    elasticsearch_url: str = "http://elasticsearch:9200"
    elasticsearch_index: str = "documents"

    redis_url: str = "redis://redis:6379"

    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "api_db"
    postgres_host: str = "db"
    postgres_port: int = 5432

    secret_key: str = "change-me-in-production-please"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 часа

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()
