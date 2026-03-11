"""Middleware HTTP da aplicação.

Intercepta todas as requisições para adicionar cabeçalhos de rastreabilidade,
facilitando correlação de logs e monitoramento de latência.
"""

import time
import uuid
from collections.abc import Awaitable, Callable

from fastapi import Request
from starlette.responses import Response


async def request_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """Adiciona rastreabilidade e métricas de latência a cada requisição HTTP.

    Gera um UUID único por requisição e o armazena em ``request.state.request_id``,
    disponível para uso em logs durante o ciclo de vida da requisição.

    Cabeçalhos adicionados à resposta:
        - ``X-Request-ID``: UUID único da requisição para correlação de logs.
        - ``X-Process-Time-MS``: Tempo total de processamento em milissegundos.

    Args:
        request: Objeto da requisição FastAPI/Starlette.
        call_next: Função que passa a requisição para o próximo handler da cadeia.

    Returns:
        Response com os cabeçalhos de rastreabilidade adicionados.
    """
    request.state.request_id = str(uuid.uuid4())
    start = time.time()
    response = await call_next(request)
    response.headers['X-Request-ID'] = request.state.request_id
    response.headers['X-Process-Time-MS'] = str(round((time.time() - start) * 1000, 2))
    return response
