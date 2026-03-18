

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    LOG_LEVEL: str
    CONSOLE_LOG: bool | None = None
    LOG_FILE: str | None = None
    DATABASE_URL: str

    # spaCy
    MAX_MODELS_IN_MEMORY: int
    MODEL_PRELOAD: list[str]
    MAX_TEXT_LENGTH: int

    # Health / Metrics
    HEALTH_CHECK_INTERVAL: int
    METRICS_RETENTION_DAYS: int


settings = Settings()
