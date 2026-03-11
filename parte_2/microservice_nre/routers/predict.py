from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from microservice_nre.database.database import get_session
from microservice_nre.database.models import PredictLogs
from microservice_nre.database.schemas import (
    PredictLogsPublic,
    PredictRequest,
    PredictResponse,
)
from microservice_nre.services.model_registry import ModelRegistry
from microservice_nre.services.spacy_service import SpacyService
from microservice_nre.utils.error_handler import handle_http_errors

router = APIRouter(prefix='/predict', tags=['predict'])
registry = ModelRegistry()


def get_service(request: Request) -> SpacyService:
    service = request.app.state.service
    if not service:
        raise HTTPException(503, 'Service not ready')
    return service


@router.post('/', response_model=PredictResponse)
@handle_http_errors
async def predict(
    body: PredictRequest,
    service: SpacyService = Depends(get_service),  # noqa: B008
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> PredictResponse:
    """Realiza inferência utilizando o modelo ativo ou uma versão específica."""
    entities = await service.process_text(body.text, body.model)
    result = PredictResponse(entities=entities)
    modelo_db = await registry.get_by_name(body.model, session)
    if modelo_db:
        session.add(PredictLogs(
            input=body.model_dump(),
            output=result.model_dump(),
            model_version=modelo_db.model_version,
        ))
        await session.commit()
    return result


@router.get('/list', response_model=list[PredictLogsPublic])
async def list_predicts(session: AsyncSession = Depends(get_session)):
    """Lista as predições realizadas."""
    result = await session.execute(select(PredictLogs))
    return result.scalars().all()
