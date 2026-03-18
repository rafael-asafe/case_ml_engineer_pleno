"""Gerenciamento de configurações via variáveis de ambiente.

Utiliza ``pydantic-settings`` para carregar e validar automaticamente as
variáveis de ambiente definidas no arquivo ``.env`` ou no ambiente do sistema.
Todas as configurações são tipadas e validadas na inicialização da aplicação.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações centralizadas do pipeline ETL, carregadas do arquivo ``.env``.

    Todas as variáveis são obrigatórias (sem valor padrão), exceto onde indicado.
    A ausência de qualquer variável obrigatória levantará ``ValidationError`` na
    inicialização.

    Attributes:
        LOG_LEVEL: Nível de logging do Python (ex.: ``'DEBUG'``, ``'INFO'``, ``'WARNING'``).
        CONSOLE_LOG: Se ``True``, os logs são exibidos no stdout. Defina ``False``
            em testes automatizados.
        DATABASE_URL: URL de conexão SQLAlchemy (ex.: ``'sqlite:///database.db'``
            para SQLite local ou ``'sqlite:///:memory:'`` para testes em memória).
        NOME_PASTA_SOR: Subdiretório relativo ao ``CAMINHO_DADOS`` para a camada SOR.
            Deve conter ``'today_date'`` para particionamento automático por data
            (ex.: ``'SOR/pokemons/today_date/'``).
        NOME_ARQUIVO_SOR: Nome do arquivo JSONL de dados brutos
            (ex.: ``'pokemons.jsonl'``).
        NOME_PASTA_SOT: Subdiretório relativo ao ``CAMINHO_DADOS`` para a camada SOT.
            As tabelas são organizadas em subpastas por nome de tabela e data
            (ex.: ``'SOT/'``).
        CAMINHO_DADOS: Caminho base para armazenamento de todos os arquivos de dados
            (ex.: ``'./data/'``).
        LIMIT_OFFSET: Número de itens por página nas requisições paginadas à PokéAPI.
            Controla o tamanho do batch de busca concorrente.
        RETRY: Número máximo de tentativas em caso de falha HTTP antes de desistir.
        BACKOFF_FACTOR: Fator multiplicador para o backoff exponencial entre retries
            (ex.: ``0.5`` resulta em esperas de 0s, 0.5s, 1s, 2s...).
        CLIENT_MAX_CONNECTIONS: Número máximo de conexões TCP simultâneas no pool
            do cliente HTTP.
        MAX_KEEPALIVE_CONNECTIONS: Número máximo de conexões keep-alive mantidas
            abertas no pool.
        KEEPALIVE_EXPIRY: Tempo em segundos para expirar conexões keep-alive ociosas.
        POKEAPI_BASE_URL: URL base da PokéAPI usada pelo cliente HTTP
            (ex.: ``'https://pokeapi.co/api/v2/'``).
    """

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
