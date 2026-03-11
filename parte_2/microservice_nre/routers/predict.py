from fastapi import APIRouter


router = APIRouter(prefix='/predict', tags=['predict'])


@router.post('/')
async def predict():
    """Realiza inferência utilizando o modelo ativo ou uma versão específica."""
    return {'message': ' not implemented'}


@router.get('/list')
async def list_predicts():
    """Lista as predições realizadas"""
    return {'message': ' not implemented'}
