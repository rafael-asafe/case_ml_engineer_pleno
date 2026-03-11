from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from microservice_nre.database.database import get_session
from microservice_nre.database.models import MLModel
from microservice_nre.database.schemas import MLModelPublic, MLModelSchema
from microservice_nre.utils.ml_utils import get_model

router = APIRouter(prefix='/models', tags=['models'])


@router.post('/load', status_code=HTTPStatus.CREATED, response_model=MLModelPublic)
async def load(ml_model: MLModelSchema, session: Session = Depends(get_session)):  # noqa: B008
    """Registra uma nova versão do modelo caso não exista baixa uma o modelo"""
    db_ml_model = session.scalar(select(MLModel).where(MLModel.model == ml_model.model))

    if db_ml_model:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Modelo já registrado',
        )

    get_model(ml_model.model)

    db_ml_model = MLModel(model=ml_model.model)

    session.add(db_ml_model)
    session.commit()
    session.refresh(db_ml_model)

    return db_ml_model


@router.get('/')
async def list_models():
    """Lista as predições realizadas"""
    return {'message': ' not implemented'}


@router.delete('/{model_version}')
async def delete_model(model_version: int):
    """deleta versão específica do modelo"""
    return {'message': ' not implemented'}
