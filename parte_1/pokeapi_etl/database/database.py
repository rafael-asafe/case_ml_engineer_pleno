"""Configuração do banco de dados e utilitários de acesso a dados.

Fornece o engine SQLAlchemy, a fábrica de sessões e funções auxiliares
para exportação de tabelas para o formato Parquet (camada SOT).
"""

from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from utils.settings import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


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
