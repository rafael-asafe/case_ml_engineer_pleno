"""Configurações da aplicação via variáveis de ambiente.

Utiliza ``pydantic-settings`` para carregar e validar variáveis de ambiente,
com suporte a arquivo ``.env``. Todos os campos sem valor padrão são obrigatórios.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações carregadas do ambiente ou arquivo ``.env``.

    Attributes:
        LOG_LEVEL: Nível de log do Python (ex: ``"INFO"``, ``"DEBUG"``).
        CONSOLE_LOG: Se ``True``, habilita handler de log para ``stdout``.
        LOG_FILE: Caminho para arquivo de log. ``None`` desabilita o handler de arquivo.
        DATABASE_URL: URL de conexão assíncrona com o banco
            (ex: ``"postgresql+asyncpg://user:pass@host/db"``).
        MAX_MODELS_IN_MEMORY: Número máximo de modelos spaCy mantidos em memória
            simultaneamente. Reservado para uso futuro em política de eviction.
        MODEL_PRELOAD: Lista de nomes de modelos spaCy a carregar no startup,
            independentemente do que está no banco
            (ex: ``["pt_core_news_sm", "en_core_web_sm"]``).
        MAX_TEXT_LENGTH: Tamanho máximo em caracteres aceito pelo endpoint de predição.
        HEALTH_CHECK_INTERVAL: Intervalo em segundos entre verificações de saúde.
            Reservado para uso futuro em checks periódicos.
        METRICS_RETENTION_DAYS: Dias de retenção dos logs de predição no banco.
            Reservado para uso futuro em rotina de limpeza.
    """

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
