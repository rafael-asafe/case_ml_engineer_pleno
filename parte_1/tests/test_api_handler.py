"""Testes unitários para os handlers de requisição HTTP da PokéAPI.

Cobre ``busca_pagina``, ``paginacao``, ``busca_lista_pokemons`` e ``busca_pokemon``,
verificando comportamento de sucesso, parâmetros enviados e propagação de erros HTTP.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from api.api_handler import busca_lista_pokemons, busca_pagina, busca_pokemon, paginacao

# --- busca_pagina ---


def test_busca_pagina_retorna_response() -> None:
    """Verifica que busca_pagina retorna a resposta do cliente HTTP."""

    async def _run():
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response

        resultado = await busca_pagina('/pokemon', 20, 0, async_client=mock_client)

        assert resultado is mock_response

    asyncio.run(_run())


def test_busca_pagina_passa_params_corretos() -> None:
    """Verifica que limit e offset são enviados como parâmetros da requisição."""

    async def _run():
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response

        await busca_pagina('/pokemon', 20, 40, async_client=mock_client)

        mock_client.get.assert_called_once_with(
            '/pokemon', params={'offset': 40, 'limit': 20}
        )

    asyncio.run(_run())


def test_busca_pagina_relanca_http_status_error() -> None:
    """Verifica que HTTPStatusError é re-lançado após o log."""

    async def _run():
        req = httpx.Request('GET', 'https://pokeapi.co/api/v2/pokemon')
        resp = httpx.Response(404, request=req)
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            'Not Found', request=req, response=resp
        )
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response

        with pytest.raises(httpx.HTTPStatusError):
            await busca_pagina('/pokemon', 20, 0, async_client=mock_client)

    asyncio.run(_run())


def test_busca_pagina_relanca_request_error() -> None:
    """Verifica que RequestError é re-lançado após o log."""

    async def _run():
        mock_client = AsyncMock()
        mock_client.get.side_effect = httpx.ConnectError('Sem conexão')

        with pytest.raises(httpx.RequestError):
            await busca_pagina('/pokemon', 20, 0, async_client=mock_client)

    asyncio.run(_run())


# --- paginacao ---


def test_paginacao_pagina_unica() -> None:
    """Verifica que paginacao retorna os resultados quando total cabe em uma página."""

    async def _run():
        mock_client = AsyncMock()
        mock_retorno = MagicMock()
        mock_retorno.json.return_value = {
            'results': [
                {'name': 'bulbasaur', 'url': 'https://pokeapi.co/api/v2/pokemon/1/'}
            ],
            'count': 1,
        }
        mock_client.get.return_value = mock_retorno

        resultado = await paginacao('/pokemon', async_client=mock_client)

        assert len(resultado) == 1
        assert resultado[0]['name'] == 'bulbasaur'

    asyncio.run(_run())


def test_paginacao_multiplas_paginas() -> None:
    """Verifica que paginacao agrega resultados de múltiplas páginas."""

    async def _run():
        mock_client = AsyncMock()
        mock_retorno = MagicMock()
        # count=25 com LIMIT_OFFSET=20 dispara 1 página extra (offset 20)
        mock_retorno.json.return_value = {
            'results': [{'name': 'bulbasaur', 'url': ''}],
            'count': 25,
        }
        mock_client.get.return_value = mock_retorno

        mock_pagina_extra = MagicMock()
        mock_pagina_extra.json.return_value = {
            'results': [{'name': 'charmander', 'url': ''}]
        }

        with patch(
            'api.api_handler.busca_pagina',
            new_callable=AsyncMock,
            return_value=mock_pagina_extra,
        ):
            resultado = await paginacao('/pokemon', async_client=mock_client)

        assert len(resultado) == 2
        nomes = [r['name'] for r in resultado]
        assert 'bulbasaur' in nomes
        assert 'charmander' in nomes

    asyncio.run(_run())


# --- busca_lista_pokemons ---


def test_busca_lista_pokemons_chama_paginacao_com_endpoint_correto() -> None:
    """Verifica que busca_lista_pokemons delega para paginacao com '/pokemon'."""

    async def _run():
        with patch(
            'api.api_handler.paginacao', new_callable=AsyncMock
        ) as mock_paginacao:
            mock_paginacao.return_value = [{'name': 'pikachu', 'url': ''}]
            resultado = await busca_lista_pokemons()

        mock_paginacao.assert_called_once_with('/pokemon')
        assert resultado == [{'name': 'pikachu', 'url': ''}]

    asyncio.run(_run())


# --- busca_pokemon ---


def test_busca_pokemon_retorna_response() -> None:
    """Verifica que busca_pokemon retorna a resposta do cliente HTTP."""

    async def _run():
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response

        resultado = await busca_pokemon(
            'https://pokeapi.co/api/v2/pokemon/1/', async_client=mock_client
        )

        assert resultado is mock_response
        mock_client.get.assert_called_once_with('https://pokeapi.co/api/v2/pokemon/1/')

    asyncio.run(_run())


def test_busca_pokemon_relanca_http_status_error() -> None:
    """Verifica que HTTPStatusError é re-lançado após o log."""

    async def _run():
        req = httpx.Request('GET', 'https://pokeapi.co/api/v2/pokemon/1/')
        resp = httpx.Response(500, request=req)
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            'Server Error', request=req, response=resp
        )
        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response

        with pytest.raises(httpx.HTTPStatusError):
            await busca_pokemon(
                'https://pokeapi.co/api/v2/pokemon/1/', async_client=mock_client
            )

    asyncio.run(_run())
