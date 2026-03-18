

import time
from json import JSONDecodeError

import httpx
import pytest
import respx

from api.client import after_request_async, before_request_async, trata_erro_http_async

_URL = 'https://pokeapi.co/api/v2/pokemon'

# --- trata_erro_http_async ---


async def test_trata_erro_retorna_response_em_sucesso() -> None:
    
    with respx.mock:
        respx.get(_URL).mock(return_value=httpx.Response(200))

        @trata_erro_http_async
        async def funcao_mock():
            async with httpx.AsyncClient() as client:
                return await client.get(_URL)

        resultado = await funcao_mock()
        assert resultado.status_code == 200


async def test_trata_erro_relanca_http_status_error() -> None:
    
    with respx.mock:
        respx.get(_URL).mock(return_value=httpx.Response(404))

        @trata_erro_http_async
        async def funcao_mock():
            async with httpx.AsyncClient() as client:
                return await client.get(_URL)

        with pytest.raises(httpx.HTTPStatusError):
            await funcao_mock()


async def test_trata_erro_relanca_request_error() -> None:
    
    with respx.mock:
        respx.get(_URL).mock(side_effect=httpx.ConnectError('Sem conexão'))

        @trata_erro_http_async
        async def funcao_mock():
            async with httpx.AsyncClient() as client:
                return await client.get(_URL)

        with pytest.raises(httpx.RequestError):
            await funcao_mock()


async def test_trata_erro_relanca_json_decode_error() -> None:
    
    with respx.mock:
        respx.get(_URL).mock(side_effect=JSONDecodeError('Erro JSON', '', 0))

        @trata_erro_http_async
        async def funcao_mock():
            async with httpx.AsyncClient() as client:
                return await client.get(_URL)

        with pytest.raises(JSONDecodeError):
            await funcao_mock()


async def test_trata_erro_relanca_excecao_generica() -> None:
    
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
    
    request = httpx.Request('GET', _URL)
    await before_request_async(request)

    assert 'request_id' in request.extensions
    assert 'start_time' in request.extensions
    assert 'execution_id' in request.extensions


async def test_before_request_request_id_e_string() -> None:
    
    request = httpx.Request('GET', _URL)
    await before_request_async(request)

    assert isinstance(request.extensions['request_id'], str)
    assert len(request.extensions['request_id']) > 0


async def test_before_request_start_time_e_float() -> None:
    
    request = httpx.Request('GET', _URL)
    await before_request_async(request)

    assert isinstance(request.extensions['start_time'], float)


# --- after_request_async ---


async def test_after_request_com_start_time_nao_levanta_excecao() -> None:
    
    request = httpx.Request('GET', _URL)
    request.extensions['start_time'] = time.monotonic()
    request.extensions['request_id'] = 'test-uuid'
    response = httpx.Response(200, request=request)

    await after_request_async(response)


async def test_after_request_sem_start_time_nao_levanta_excecao() -> None:
    
    request = httpx.Request('GET', _URL)
    response = httpx.Response(200, request=request)

    await after_request_async(response)
