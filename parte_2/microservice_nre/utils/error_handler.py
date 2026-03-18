"""Decorator centralizado de tratamento de erros HTTP.

Evita repetição de blocos ``try/except`` nos handlers de rota, mapeando
exceções internas para respostas HTTP semanticamente corretas.
"""

import functools
from collections.abc import Callable
from http import HTTPStatus

from fastapi import HTTPException


def handle_http_errors(func: Callable) -> Callable:
    """Decorator que converte exceções internas em respostas HTTP adequadas.

    Deve ser aplicado em handlers de rota FastAPI assíncronos. ``HTTPException``
    já levantadas são repassadas sem alteração, preservando o código de status
    original (ex: 409 do ``ModelRegistry.register``).

    Mapeamento de exceções:
        - ``HTTPException``: repassada sem alteração.
        - ``KeyError``: ``404 Not Found`` — modelo não encontrado no cache em memória.
        - ``OSError | RuntimeError``: ``422 Unprocessable Entity`` — falha no download
          ou carregamento do modelo spaCy.

    Args:
        func: Handler de rota assíncrono a ser decorado.

    Returns:
        Wrapper assíncrono com tratamento de erros centralizado.

    Example:
        ::

            @router.post('/load')
            @handle_http_errors
            async def load(...):
                ...
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except HTTPException:
            raise
        except KeyError as e:
            raise HTTPException(HTTPStatus.NOT_FOUND, f'Modelo {e} não está carregado') from e
        except (OSError, RuntimeError) as e:
            raise HTTPException(HTTPStatus.UNPROCESSABLE_ENTITY, str(e)) from e

    return wrapper
