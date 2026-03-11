import asyncio
from http import HTTPStatus

import spacy
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from microservice_nre.database.database import get_session
from microservice_nre.database.schemas import MLModelPublic, MLModelSchema
from microservice_nre.services.model_registry import ModelRegistry
from microservice_nre.utils.error_handler import handle_http_errors

router = APIRouter(prefix='/models', tags=['models'])
registry = ModelRegistry()


@router.post('/load', status_code=HTTPStatus.CREATED, response_model=MLModelPublic)
@handle_http_errors
async def load(request: Request, ml_model: MLModelSchema, session: AsyncSession = Depends(get_session)):  # noqa: B008
    """Registra uma nova versão do modelo; caso não exista, baixa o modelo."""
    model_obj = await registry.register(ml_model.model, session)
    nlp = await asyncio.to_thread(spacy.load, ml_model.model)
    request.app.state.service.add_model(ml_model.model, nlp)
    return model_obj


@router.get('/', response_model=list[MLModelPublic])
async def list_models(session: AsyncSession = Depends(get_session)):
    """Lista os modelos registrados."""
    return await registry.list(session)


@router.delete('/{model_version}', status_code=HTTPStatus.NO_CONTENT)
@handle_http_errors
async def delete_model(request: Request, model_version: int, session: AsyncSession = Depends(get_session)):  # noqa: B008
    """Deleta uma versão específica do modelo e remove do cache em memória."""
    model_obj = await registry.get_by_version(model_version, session)
    await registry.delete(model_version, session)
    request.app.state.service.remove_model(model_obj.model)
