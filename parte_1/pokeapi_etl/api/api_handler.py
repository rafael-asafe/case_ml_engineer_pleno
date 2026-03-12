"""Handlers de requisição HTTP para a PokéAPI.

Contém as funções responsáveis pela extração dos dados:
- Paginação automática do endpoint de listagem de Pokémons.
- Busca concorrente dos detalhes de cada Pokémon individual.

Todas as funções que fazem requisições HTTP utilizam o decorador
``trata_erro_http_async`` para tratamento padronizado de erros.
"""

from asyncio import gather
from itertools import chain

from httpx import AsyncClient, Response

from api.client import async_client, trata_erro_http_async
from utils.settings import Settings


@trata_erro_http_async
async def busca_pagina(
    url: str, limit: int, offset: int, async_client: AsyncClient = async_client
) -> Response:
    """Busca uma página específica de resultados da API com paginação por offset.

    Realiza uma requisição GET com os parâmetros ``limit`` e ``offset`` para
    navegar entre páginas do endpoint de listagem.

    Args:
        url: Caminho relativo do endpoint (ex.: ``'/pokemon'``).
        limit: Número máximo de itens por página (definido em ``Settings().LIMIT_OFFSET``).
        offset: Índice do primeiro item da página atual.
        async_client: Cliente HTTP assíncrono a ser utilizado. Por padrão usa o
            cliente global configurado em ``api.client``.

    Returns:
        Response: Resposta HTTP com status 2xx contendo a página de resultados.

    Raises:
        httpx.HTTPStatusError: Se o servidor retornar um código de erro HTTP (4xx, 5xx).
        httpx.RequestError: Em caso de falha de conexão ou timeout.
    """
    params = {'offset': offset, 'limit': limit}
    response = await async_client.get(url, params=params)
    return response


async def paginacao(url: str, async_client: AsyncClient = async_client) -> list[dict[str, str]]:
    """Coleta todos os itens de um endpoint paginado da PokéAPI de forma concorrente.

    Executa uma primeira requisição para obter o total de registros e os itens
    da primeira página, depois dispara todas as páginas restantes em paralelo
    usando ``asyncio.gather``.

    Args:
        url: Caminho relativo do endpoint paginado (ex.: ``'/pokemon'``).
        async_client: Cliente HTTP assíncrono a ser utilizado.

    Returns:
        list[dict[str, str]]: Lista completa de itens de todas as páginas,
            onde cada item é um dicionário com pelo menos ``'name'`` e ``'url'``.

    Note:
        O tamanho de cada página é controlado por ``Settings().LIMIT_OFFSET``.
        A primeira página é obtida com offset 0 (requisição inicial) e as
        demais são buscadas em paralelo a partir do offset ``LIMIT_OFFSET``.
    """
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


async def busca_lista_pokemons() -> list[dict[str, str]]:
    """Retorna a lista completa de Pokémons disponíveis na PokéAPI.

    Atalho sobre ``paginacao`` que aponta para o endpoint ``/pokemon``.
    Cada item da lista contém o ``name`` e a ``url`` de detalhe do Pokémon.

    Returns:
        list[dict[str, str]]: Lista com todos os Pokémons do índice, cada um
            representado por ``{'name': str, 'url': str}``.
    """
    retornos = await paginacao('/pokemon')
    return retornos


@trata_erro_http_async
async def busca_pokemon(
    pokemon_url: str, async_client: AsyncClient = async_client
) -> Response:
    """Busca os detalhes completos de um Pokémon específico.

    Realiza uma requisição GET para a URL absoluta do Pokémon retornada
    pelo endpoint de listagem. A resposta contém todos os atributos do
    Pokémon (stats, tipos, habilidades, etc.).

    Args:
        pokemon_url: URL absoluta do Pokémon
            (ex.: ``'https://pokeapi.co/api/v2/pokemon/1/'``).
        async_client: Cliente HTTP assíncrono a ser utilizado.

    Returns:
        Response: Resposta HTTP com os dados completos do Pokémon em JSON.

    Raises:
        httpx.HTTPStatusError: Se o servidor retornar um código de erro HTTP (4xx, 5xx).
        httpx.RequestError: Em caso de falha de conexão ou timeout.
    """
    response = await async_client.get(pokemon_url)
    return response
