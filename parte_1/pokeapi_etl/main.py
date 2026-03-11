from asyncio import gather, run

from api.api_handler import busca_lista_pokemons, busca_pokemon
from storage.storage import OperadorArmazenamento
from utils.logger import logger
from utils.settings import Settings


async def main() -> None:
    try:
        index_pokemons = await busca_lista_pokemons()

        lista_retornos = await gather(*[
            busca_pokemon(item_index.get('url')) for item_index in index_pokemons
        ])

        OperadorArmazenamento.registra_dados_brutos(
            lista_retornos, Settings().NOME_PASTA_SOR, Settings().NOME_ARQUIVO_SOR
        )

        OperadorArmazenamento.registra_dados_bd(lista_retornos)

        OperadorArmazenamento.exporta_tabelas_bd()

    except Exception as e:
        logger.exception(f'Pipeline encerrado com erro: {e}')
        raise


run(main())
