

import time
import uuid
from collections.abc import Awaitable, Callable

from fastapi import Request
from starlette.responses import Response


async def request_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    
    request.state.request_id = str(uuid.uuid4())
    start = time.time()
    response = await call_next(request)
    response.headers['X-Request-ID'] = request.state.request_id
    response.headers['X-Process-Time-MS'] = str(round((time.time() - start) * 1000, 2))
    return response
