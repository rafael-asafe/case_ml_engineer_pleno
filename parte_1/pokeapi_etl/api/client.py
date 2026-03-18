"""Configuração do cliente HTTP assíncrono para a PokéAPI.

Monta o ``httpx.AsyncClient`` global com:
- Cache HTTP via Hishel (SQLite) para evitar requisições duplicadas.
- Retry automático com backoff exponencial via httpx-retries.
- Limites de conexão simultânea configuráveis via Settings.
- Event hooks para rastreamento de requisições (ID único, tempo de resposta).

O cliente exposto (``async_client``) deve ser importado e reutilizado por todos
os handlers de requisição para aproveitar o pool de conexões compartilhado.
"""

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
    """Decorador que adiciona tratamento padronizado de erros HTTP a corrotinas assíncronas.

    Envolve a função decorada em um bloco try/except que captura os principais
    tipos de falha de uma requisição HTTP, registra a mensagem de erro no logger
    e re-lança a exceção para que o chamador possa tratá-la.

    Args:
        func: Corrotina assíncrona que realiza uma requisição HTTP e retorna um
            ``httpx.Response``.

    Returns:
        Callable: Versão decorada da função com tratamento de erros e logging.

    Raises:
        httpx.HTTPStatusError: Quando o servidor retorna um código de status de erro
            (4xx ou 5xx). O status code é incluído na mensagem de log.
        httpx.RequestError: Em caso de falha de rede, timeout ou problema de conexão.
        JSONDecodeError: Se a resposta não puder ser decodificada como JSON.
        IOError: Para erros de entrada/saída durante a requisição.
        Exception: Para qualquer outra exceção inesperada, logada com traceback completo.

    Example:
        >>> @trata_erro_http_async
        ... async def busca_recurso(url: str) -> httpx.Response:
        ...     return await client.get(url)
    """
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
    """Hook executado antes de cada requisição HTTP para adicionar metadados de rastreamento.

    Gera um UUID único por requisição (``X-Requests-ID``), registra o instante de
    início (via ``time.monotonic()``) e o ID de execução do pipeline nas extensões
    do objeto ``request``, permitindo correlacionar logs de requisição e resposta.

    Args:
        request: Objeto de requisição httpx que será enriquecido com os metadados.

    Note:
        Este hook é registrado automaticamente no ``async_client`` e não deve
        ser chamado diretamente.
    """
    request_id = str(uuid.uuid4())
    request.headers['X-Requests-ID'] = request_id
    request.extensions['request_id'] = request_id
    request.extensions['start_time'] = time.monotonic()
    request.extensions['execution_id'] = execution_id


async def after_request_async(response: httpx.Response) -> None:
    """Hook executado após cada resposta HTTP para registrar métricas da requisição.

    Calcula o tempo decorrido desde o início da requisição (registrado em
    ``before_request_async``) e emite uma linha de log estruturada com método,
    URL, status code, tempo de resposta e ID único da requisição.

    Args:
        response: Objeto de resposta httpx contendo a requisição original e
            as extensões preenchidas pelo hook de pré-requisição.

    Note:
        Caso ``start_time`` não esteja disponível nas extensões (ex.: em testes),
        o campo de tempo de resposta é registrado como ``None``.
    """
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
