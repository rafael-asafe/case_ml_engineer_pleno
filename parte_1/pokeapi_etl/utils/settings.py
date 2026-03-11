from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """importa as variaveis de ambiente do arquivo .env"""

    model_config = SettingsConfigDict(env_file=".env", env_file_encondig="utf-8")

    LOG_LEVEL: str
    CONSOLE_LOG: bool
    DATABASE_URL: str
    NOME_PASTA_SOR: str
    NOME_ARQUIVO_SOR: str
    NOME_PASTA_SOT: str
    CAMINHO_DADOS: str
    LIMIT_OFFSET:int
    RETRY:int
    BACKOFF_FACTOR: float
    CLIENT_MAX_CONNECTIONS: int
    MAX_KEEPALIVE_CONNECTIONS: int
    KEEPALIVE_EXPIRY: float
    POKEAPI_BASE_URL: str
