from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """importa as variaveis de ambiente do arquivo .env"""

    model_config = SettingsConfigDict(env_file=".env", env_file_encondig="utf-8")

    LOG_LEVEL: str
    CONSOLE_LOG: bool
    TIMEOUT_SEC: float
