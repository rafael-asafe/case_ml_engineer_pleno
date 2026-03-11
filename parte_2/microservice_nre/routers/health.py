from fastapi import APIRouter

router = APIRouter(tags=['health'])


@router.get('/health')
async def health_status():
    """confere saude da aplicação"""
    return {'message': ' not implemented'}
