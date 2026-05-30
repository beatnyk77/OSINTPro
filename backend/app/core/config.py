import os
from pydantic import BaseSettings, PostgresDsn, AnyHttpUrl
from typing import List, Union, Optional
from pydantic.networks import validator

class Settings(BaseSettings):
    PROJECT_NAME: str = "OSINT-Pro"
    API_V1_STR: str = "/api/v1"
    # Backend CORS origins
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    # Database
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "db")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "osint_pro")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql",
            user=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=f"{self.POSTGRES_DB or ''}",
        )

    # Mission profile
    MISSION_PROFILE: str = os.getenv("MISSION_PROFILE", "lac_logistics")

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
