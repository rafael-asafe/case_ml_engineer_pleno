from datetime import datetime

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter(tags=['health'])


@router.get('/health', response_model=None)
async def health_status(request: Request) -> JSONResponse | dict:
    """Confere saúde da aplicação."""
    service = getattr(request.app.state, 'service', None)

    if not service:
        return JSONResponse(status_code=503, content={'status': 'starting'})

    return {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'uptime_seconds': (datetime.now() - service.startup_time).total_seconds(),
        'requests_total': service.request_count,
        'models_in_memory': service.loaded_models,
    }
