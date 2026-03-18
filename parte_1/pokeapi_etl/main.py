"""Ponto de entrada do pipeline ETL da PokéAPI.

Orquestra as três etapas do pipeline:
1. Extração assíncrona dos dados da PokéAPI.
2. Carga dos dados brutos no formato JSONL (camada SOR).
3. Persistência no banco de dados relacional e exportação para Parquet (camada SOT).
"""

from asyncio import gather, run

from api.api_handler import busca_lista_pokemons, busca_pokemon
from storage.storage import OperadorArmazenamento
from utils.logger import logger
from utils.settings import Settings


async def main() -> None:
    """Executa o pipeline ETL completo de forma assíncrona.

    Fluxo de execução:
        1. Busca o índice paginado de todos os Pokémons disponíveis na PokéAPI.
        2. Dispara requisições concorrentes para obter os detalhes de cada Pokémon.
        3. Salva os dados brutos em um arquivo JSONL na camada SOR (System of Record).
        4. Persiste os dados normalizados no banco de dados relacional (SQLite).
        5. Exporta cada tabela do banco para arquivos Parquet na camada SOT (System of Truth).

    Raises:
        Exception: Qualquer exceção não tratada durante o pipeline é logada e re-lançada,
            encerrando a execução com código de erro.
    """
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
