"""Gerenciamento do ciclo de vida da aplicação FastAPI.

Separa a lógica de startup e shutdown do módulo principal,
mantendo ``main.py`` responsável apenas pela composição da aplicação.
"""

import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import spacy
from fastapi import FastAPI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from microservice_nre.database.database import engine
from microservice_nre.database.models import MLModel
from microservice_nre.services.spacy_service import SpacyService
from microservice_nre.utils.logger import logger
from microservice_nre.utils.settings import Settings

_s = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Gerencia o ciclo de vida da aplicação (startup e shutdown).

    **Startup** (antes do ``yield``):

    1. Instancia o ``SpacyService`` e o expõe em ``app.state.service`` para os handlers.
       As tabelas já existem pois o serviço ``migrate`` (Alembic) roda antes no compose.
    2. Consolida a lista de modelos a carregar: union entre os registrados no banco e
       os definidos em ``MODEL_PRELOAD`` (settings), evitando duplicatas.
    3. Carrega cada modelo via ``spacy.load`` em thread separada e o registra no serviço.
       Falhas individuais são logadas como warning sem interromper o startup.

    **Shutdown** (após o ``yield``):

    - Limpa o cache em memória do ``SpacyService`` via ``service.clear()``.

    Args:
        app: Instância da aplicação FastAPI.

    Yields:
        Controle para o servidor após o startup concluído.
    """
    service = SpacyService()
    app.state.service = service

    async with AsyncSession(engine, expire_on_commit=False) as session:
        registered = (await session.execute(select(MLModel))).scalars().all()

    names_to_load = {m.model for m in registered} | set(_s.MODEL_PRELOAD)

    for name in names_to_load:
        try:
            nlp = await asyncio.to_thread(spacy.load, name)
            service.add_model(name, nlp)
            logger.info(f'Preloaded: {name}')
        except Exception as e:
            logger.warning(f'Preload falhou para {name}: {e}')

    logger.info('Aplicação pronta')
    yield

    service.clear()
    logger.info('Aplicação encerrada')
