from asyncio import gather
from itertools import chain

from httpx import AsyncClient, Response

from api.client import async_client, trata_erro_http_async
from utils.settings import Settings


@trata_erro_http_async
async def busca_pagina(
    url: str, limit: int, offset: int, async_client: AsyncClient = async_client
) -> Response:
    params = {'offset': offset, 'limit': limit}
    response = await async_client.get(url, params=params)
    return response


async def paginacao(url: int, async_client: AsyncClient = async_client) -> list:
    paginas = []
    retorno = await async_client.get(url)
    paginas += retorno.json()['results']
    total = retorno.json().get('count')

    retornos = await gather(*[
        busca_pagina(url, Settings().LIMIT_OFFSET, offset)
        for offset in range(Settings().LIMIT_OFFSET, total, Settings().LIMIT_OFFSET)
    ])

    paginas.extend(chain.from_iterable(r.json()['results'] for r in retornos))

    return paginas


async def busca_lista_pokemons() -> list[Response]:
    retornos = await paginacao('/pokemon')
    return retornos


@trata_erro_http_async
async def busca_pokemon(
    pokemon_url: str, async_client: AsyncClient = async_client
) -> Response:
    response = await async_client.get(pokemon_url)
    return response
