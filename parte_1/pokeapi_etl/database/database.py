from contextlib import contextmanager

import polars as pl
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from utils.logger import logger
from utils.settings import Settings

engine = create_engine(Settings().DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def exporta_para_parquet(nome_tabela: str,destino_tabela: str,engine:Engine = engine) -> None:
    try:
        query = f"SELECT * FROM {nome_tabela}"
        df = pl.read_database(query=query, connection=engine)

        # TODO resolve usando um postgres - sqlite não tem suporte a bool
        if nome_tabela == 'pokemon_ability':
            df_ajustado = df.with_columns(pl.col("is_hidden").cast(pl.Boolean))
            df_ajustado.write_parquet(destino_tabela,compression="snappy")
            return 
        
        df.write_parquet(destino_tabela,compression="snappy")
    
    except Exception as e:
        logger.error(f"erro ao salvar tabela: {nome_tabela} em parquet,\n erro: {e}")
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


