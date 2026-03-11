import time
import uuid
from functools import wraps
from json import JSONDecodeError
from typing import Callable, ParamSpec, TypeVar

import hishel
import hishel.httpx
import httpx
from httpx_retries import Retry, RetryTransport

from utils.logger import execution_id, logger
from utils.settings import Settings

P = ParamSpec('P')
T = TypeVar('T')

retry = Retry(total=Settings().RETRY, backoff_factor=Settings().BACKOFF_FACTOR)

retry_transport = RetryTransport(retry=retry)

transport_async = hishel.httpx.AsyncCacheTransport(
    next_transport=retry_transport,
    storage=hishel.AsyncSqliteStorage(),
)

limits = httpx.Limits(
    max_connections=Settings().CLIENT_MAX_CONNECTIONS,
    max_keepalive_connections=Settings().MAX_KEEPALIVE_CONNECTIONS,
    keepalive_expiry=Settings().KEEPALIVE_EXPIRY,
)


def trata_erro_http_async(func: Callable[P, T]) -> Callable[P, T]:
    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        try:
            logger.debug(f'=== Iniciando {func.__name__}')

            response = await func(*args, **kwargs)

            logger.debug(f'Status HTTP: {response.status_code}')

            response.raise_for_status()

            return response

        except httpx.HTTPStatusError as e:
            logger.error(f'✗ Erro HTTP {e.response.status_code}: {e} ')
            raise
        except httpx.RequestError as e:
            logger.error(f'✗ Erro de conexão: {e} ')
            raise
        except JSONDecodeError as e:
            logger.error(f'✗ Erro no formato JSON: {e} ')
            raise
        except IOError as e:
            logger.error(f'✗ Erro de I/O: {e} ')
            raise
        except Exception as e:
            logger.exception(f'✗ Erro inesperado: {e} ')
            raise

    return wrapper


async def before_request_async(request: httpx.Request) -> None:
    request_id = str(uuid.uuid4())
    request.headers['X-Requests-ID'] = request_id
    request.extensions['request_id'] = request_id
    request.extensions['start_time'] = time.monotonic()
    request.extensions['execution_id'] = execution_id


async def after_request_async(response: httpx.Response) -> None:
    request = response.request
    start = response.request.extensions.get('start_time', None)
    if start:
        elapsed = time.monotonic() - start
    else:
        elapsed = None

    logger.info(
        f'<pokeapi - extract> {request.method} {request.url} {response.status_code} '
        f'{elapsed} {request.extensions.get("request_id")}'
    )


async_client = httpx.AsyncClient(
    event_hooks={'request': [before_request_async], 'response': [after_request_async]},
    transport=transport_async,
    limits=limits,
    base_url=Settings().POKEAPI_BASE_URL,
)
