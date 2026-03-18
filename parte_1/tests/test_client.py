"""Testes unitários para o módulo de cliente HTTP (``api.client``).

Cobre o decorador ``trata_erro_http_async`` e os event hooks
``before_request_async`` e ``after_request_async``.
"""

import time
from json import JSONDecodeError

import httpx
import pytest
import respx

from api.client import after_request_async, before_request_async, trata_erro_http_async

_URL = 'https://pokeapi.co/api/v2/pokemon'

# --- trata_erro_http_async ---


async def test_trata_erro_retorna_response_em_sucesso() -> None:
    """Verifica que a função decorada retorna a resposta quando não há erros."""
    with respx.mock:
        respx.get(_URL).mock(return_value=httpx.Response(200))

        @trata_erro_http_async
        async def funcao_mock():
            async with httpx.AsyncClient() as client:
                return await client.get(_URL)

        resultado = await funcao_mock()
        assert resultado.status_code == 200


async def test_trata_erro_relanca_http_status_error() -> None:
    """Verifica que HTTPStatusError é re-lançado após o log de erro."""
    with respx.mock:
        respx.get(_URL).mock(return_value=httpx.Response(404))

        @trata_erro_http_async
        async def funcao_mock():
            async with httpx.AsyncClient() as client:
                return await client.get(_URL)

        with pytest.raises(httpx.HTTPStatusError):
            await funcao_mock()


async def test_trata_erro_relanca_request_error() -> None:
    """Verifica que RequestError é re-lançado após o log de erro."""
    with respx.mock:
        respx.get(_URL).mock(side_effect=httpx.ConnectError('Sem conexão'))

        @trata_erro_http_async
        async def funcao_mock():
            async with httpx.AsyncClient() as client:
                return await client.get(_URL)

        with pytest.raises(httpx.RequestError):
            await funcao_mock()


async def test_trata_erro_relanca_json_decode_error() -> None:
    """Verifica que JSONDecodeError é re-lançado após o log de erro."""
    with respx.mock:
        respx.get(_URL).mock(side_effect=JSONDecodeError('Erro JSON', '', 0))

        @trata_erro_http_async
        async def funcao_mock():
            async with httpx.AsyncClient() as client:
                return await client.get(_URL)

        with pytest.raises(JSONDecodeError):
            await funcao_mock()


async def test_trata_erro_relanca_excecao_generica() -> None:
    """Verifica que exceções inesperadas são re-lançadas após o log."""
    with respx.mock:
        respx.get(_URL).mock(side_effect=ValueError('erro inesperado'))

        @trata_erro_http_async
        async def funcao_mock():
            async with httpx.AsyncClient() as client:
                return await client.get(_URL)

        with pytest.raises(ValueError):
            await funcao_mock()


# --- before_request_async ---


async def test_before_request_adiciona_extensoes() -> None:
    """Verifica que before_request_async adiciona request_id, start_time e execution_id nas extensões."""
    request = httpx.Request('GET', _URL)
    await before_request_async(request)

    assert 'request_id' in request.extensions
    assert 'start_time' in request.extensions
    assert 'execution_id' in request.extensions


async def test_before_request_request_id_e_string() -> None:
    """Verifica que request_id adicionado é uma string não vazia."""
    request = httpx.Request('GET', _URL)
    await before_request_async(request)

    assert isinstance(request.extensions['request_id'], str)
    assert len(request.extensions['request_id']) > 0


async def test_before_request_start_time_e_float() -> None:
    """Verifica que start_time adicionado é um número de ponto flutuante."""
    request = httpx.Request('GET', _URL)
    await before_request_async(request)

    assert isinstance(request.extensions['start_time'], float)


# --- after_request_async ---


async def test_after_request_com_start_time_nao_levanta_excecao() -> None:
    """Verifica que after_request_async executa sem erros quando start_time está presente."""
    request = httpx.Request('GET', _URL)
    request.extensions['start_time'] = time.monotonic()
    request.extensions['request_id'] = 'test-uuid'
    response = httpx.Response(200, request=request)

    await after_request_async(response)


async def test_after_request_sem_start_time_nao_levanta_excecao() -> None:
    """Verifica que after_request_async executa sem erros quando start_time está ausente."""
    request = httpx.Request('GET', _URL)
    response = httpx.Response(200, request=request)

    await after_request_async(response)
