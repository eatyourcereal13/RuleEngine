from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, ConfigDict
from typing import Optional


class Settings(BaseSettings):
    PROJECT_NAME: str = "Движок правил"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_URL: Optional[PostgresDsn] = None
    
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )
    
    def model_post_init(self, __context):
        if not self.DATABASE_URL:
            self.DATABASE_URL = PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.POSTGRES_SERVER,
                port=5432,
                path=self.POSTGRES_DB or "",
            )


settings = Settings()