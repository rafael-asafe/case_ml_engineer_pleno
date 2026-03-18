

import functools
from collections.abc import Callable
from http import HTTPStatus

from fastapi import HTTPException


def handle_http_errors(func: Callable) -> Callable:
    

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
