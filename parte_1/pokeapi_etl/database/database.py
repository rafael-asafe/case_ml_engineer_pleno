"""Configuração do banco de dados e utilitários de acesso a dados.

Fornece o engine SQLAlchemy, a fábrica de sessões e funções auxiliares
para exportação de tabelas para o formato Parquet (camada SOT).
"""

from contextlib import contextmanager

import polars as pl
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from utils.logger import logger
from utils.settings import Settings

engine = create_engine(Settings().DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def exporta_para_parquet(nome_tabela: str, destino_tabela: str, engine: Engine = engine) -> None:
    """Exporta uma tabela do banco de dados para o formato Parquet com compressão Snappy.

    Lê todos os registros da tabela informada via Polars, aplica correções de tipo
    quando necessário (ex.: cast de inteiro para booleano no SQLite) e grava o
    resultado em disco no formato Parquet.

    Args:
        nome_tabela: Nome da tabela no banco de dados a ser exportada.
        destino_tabela: Caminho completo do arquivo Parquet de destino (incluindo extensão).
        engine: Engine SQLAlchemy a ser utilizado na leitura. Por padrão usa o engine
            global configurado via ``Settings().DATABASE_URL``.

    Raises:
        Exception: Propaga qualquer erro de leitura do banco ou escrita em disco,
            registrando a mensagem no logger antes de re-lançar.

    Note:
        O SQLite não possui tipo booleano nativo. Por isso, a coluna ``is_hidden``
        da tabela ``pokemon_ability`` é convertida explicitamente para ``pl.Boolean``
        após a leitura.
    """
    try:
        query = f'SELECT * FROM {nome_tabela}'
        df = pl.read_database(query=query, connection=engine)

        # SQLite não tem suporte nativo a bool; cast explícito necessário
        if nome_tabela == 'pokemon_ability':
            df = df.with_columns(pl.col('is_hidden').cast(pl.Boolean))

        df.write_parquet(destino_tabela, compression='snappy')

    except Exception as e:
        logger.error(f'Erro ao salvar tabela {nome_tabela!r} em parquet: {e}')
        raise


@contextmanager
def get_session() -> Session:
    """Gerenciador de contexto para obter e gerenciar uma sessão do banco de dados.

    Garante que a sessão seja commitada ao final do bloco ``with`` em caso de
    sucesso, ou revertida (rollback) em caso de exceção, e sempre fechada ao término.

    Yields:
        Session: Sessão SQLAlchemy ativa pronta para uso.

    Raises:
        Exception: Propaga qualquer exceção ocorrida dentro do bloco ``with``,
            garantindo o rollback antes de re-lançar.

    Example:
        >>> with get_session() as session:
        ...     session.add(novo_pokemon)
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
