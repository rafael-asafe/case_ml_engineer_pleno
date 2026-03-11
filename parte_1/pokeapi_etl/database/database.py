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
    """Exporta uma tabela do banco de dados para o formato Parquet."""
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
    """Context manager that yields a database session."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


