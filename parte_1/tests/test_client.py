"""Testes unitários para o módulo de cliente HTTP (``api.client``).

Cobre o decorador ``trata_erro_http_async`` e os event hooks
``before_request_async`` e ``after_request_async``.
"""

import asyncio
import time
from json import JSONDecodeError
from unittest.mock import MagicMock

import httpx
import pytest

from api.client import after_request_async, before_request_async, trata_erro_http_async

# --- trata_erro_http_async ---


def test_trata_erro_retorna_response_em_sucesso() -> None:
    """Verifica que a função decorada retorna a resposta quando não há erros."""

    async def _run():
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()

        @trata_erro_http_async
        async def funcao_mock():
            return mock_response

        resultado = await funcao_mock()
        assert resultado is mock_response

    asyncio.run(_run())


def test_trata_erro_relanca_http_status_error() -> None:
    """Verifica que HTTPStatusError é re-lançado após o log de erro."""

    async def _run():
        req = httpx.Request('GET', 'https://pokeapi.co/api/v2/pokemon')
        resp = httpx.Response(404, request=req)

        @trata_erro_http_async
        async def funcao_mock():
            raise httpx.HTTPStatusError('Not Found', request=req, response=resp)

        with pytest.raises(httpx.HTTPStatusError):
            await funcao_mock()

    asyncio.run(_run())


def test_trata_erro_relanca_request_error() -> None:
    """Verifica que RequestError é re-lançado após o log de erro."""

    async def _run():
        @trata_erro_http_async
        async def funcao_mock():
            raise httpx.ConnectError('Sem conexão')

        with pytest.raises(httpx.RequestError):
            await funcao_mock()

    asyncio.run(_run())


def test_trata_erro_relanca_json_decode_error() -> None:
    """Verifica que JSONDecodeError é re-lançado após o log de erro."""

    async def _run():
        @trata_erro_http_async
        async def funcao_mock():
            raise JSONDecodeError('Erro JSON', '', 0)

        with pytest.raises(JSONDecodeError):
            await funcao_mock()

    asyncio.run(_run())


def test_trata_erro_relanca_excecao_generica() -> None:
    """Verifica que exceções inesperadas são re-lançadas após o log."""

    async def _run():
        @trata_erro_http_async
        async def funcao_mock():
            raise ValueError('erro inesperado')

        with pytest.raises(ValueError):
            await funcao_mock()

    asyncio.run(_run())


# --- before_request_async ---


def test_before_request_adiciona_extensoes() -> None:
    """Verifica que before_request_async adiciona request_id, start_time e execution_id nas extensões."""

    async def _run():
        request = httpx.Request('GET', 'https://pokeapi.co/api/v2/pokemon')
        await before_request_async(request)

        assert 'request_id' in request.extensions
        assert 'start_time' in request.extensions
        assert 'execution_id' in request.extensions

    asyncio.run(_run())


def test_before_request_request_id_e_string() -> None:
    """Verifica que request_id adicionado é uma string não vazia."""

    async def _run():
        request = httpx.Request('GET', 'https://pokeapi.co/api/v2/pokemon')
        await before_request_async(request)

        assert isinstance(request.extensions['request_id'], str)
        assert len(request.extensions['request_id']) > 0

    asyncio.run(_run())


def test_before_request_start_time_e_float() -> None:
    """Verifica que start_time adicionado é um número de ponto flutuante."""

    async def _run():
        request = httpx.Request('GET', 'https://pokeapi.co/api/v2/pokemon')
        await before_request_async(request)

        assert isinstance(request.extensions['start_time'], float)

    asyncio.run(_run())


# --- after_request_async ---


def test_after_request_com_start_time_nao_levanta_excecao() -> None:
    """Verifica que after_request_async executa sem erros quando start_time está presente."""

    async def _run():
        request = httpx.Request('GET', 'https://pokeapi.co/api/v2/pokemon')
        request.extensions['start_time'] = time.monotonic()
        request.extensions['request_id'] = 'test-uuid'
        response = httpx.Response(200, request=request)

        await after_request_async(response)  # não deve levantar

    asyncio.run(_run())


def test_after_request_sem_start_time_nao_levanta_excecao() -> None:
    """Verifica que after_request_async executa sem erros quando start_time está ausente."""

    async def _run():
        request = httpx.Request('GET', 'https://pokeapi.co/api/v2/pokemon')
        response = httpx.Response(200, request=request)

        await after_request_async(response)  # não deve levantar

    asyncio.run(_run())
