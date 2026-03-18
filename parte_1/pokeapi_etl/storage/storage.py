

from datetime import date
from pathlib import Path

import polars as pl
from httpx import Response
from sqlalchemy import select
from sqlalchemy.engine import Engine

from database.database import engine, get_session
from database.models import (
    Pokemon,
    PokemonAbility,
    PokemonStats,
    PokemonType,
    table_registry,
)
from database.schemas import PokemonSchema
from utils.logger import logger
from utils.settings import settings


class OperadorArmazenamento:
    

    @staticmethod
    def _build_folder_path(base: str) -> Path:
        
        folder = Path(base.replace('today_date', date.today().strftime('%Y/%m/%d')))
        folder.mkdir(parents=True, exist_ok=True)
        return folder

    @staticmethod
    def _gerar_pokemons(retornos: list[Response]) -> PokemonSchema:
        
        for retorno in retornos:
            yield PokemonSchema(**retorno.json())

    @staticmethod
    def _exporta_para_parquet(
        nome_tabela: str, destino_tabela: str, engine: Engine = engine
    ) -> None:
        
        try:
            query = f'SELECT * FROM {nome_tabela}'
            df = pl.read_database(query=query, connection=engine)

            # SQLite não tem suporte nativo a bool; cast explícito necessário
            if nome_tabela == 'pokemon_ability':
                df = df.with_columns(pl.col('is_hidden').cast(pl.Boolean))

            df.write_parquet(destino_tabela, compression='snappy')

        except Exception as e:
            logger.error(f'Erro ao salvar tabela {nome_tabela!r} em parquet: {e}')
            raise

    @classmethod
    def registra_dados_brutos(
        cls, retornos: list[Response], nome_pasta: str, nome_arquivo: str
    ) -> None:
        
        pokemons = cls._gerar_pokemons(retornos)
        folder = cls._build_folder_path(settings.CAMINHO_DADOS + nome_pasta)
        filepath = folder / nome_arquivo

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                for pokemon in pokemons:
                    f.write(pokemon.model_dump_json() + '\n')

        except Exception as e:
            logger.error(f'Erro ao salvar dados brutos: {e}')
            raise

    @classmethod
    def registra_dados_bd(cls, retornos: list[Response]) -> None:
        
        try:
            pokemons = cls._gerar_pokemons(retornos)

            with get_session() as session:
                for pokemon in pokemons:
                    db_pokemon = session.scalar(
                        select(Pokemon).where(Pokemon.pokemon_id == pokemon.pokemon_id)
                    )

                    if db_pokemon:
                        logger.debug(
                            f'Pokemon {pokemon.name} já registrado, ignorando.'
                        )
                        continue

                    db_pokemon = Pokemon(
                        pokemon_id=pokemon.pokemon_id,
                        name=pokemon.name,
                        height=pokemon.height,
                        weight=pokemon.weight,
                        base_experience=pokemon.base_experience,
                        abilities=[
                            PokemonAbility(
                                ability_name=a.ability_name, is_hidden=a.is_hidden
                            )
                            for a in pokemon.abilities
                        ],
                        stats=[
                            PokemonStats(stat_name=s.stat_name, base_stat=s.base_stat)
                            for s in pokemon.stats
                        ],
                        types=[
                            PokemonType(type_name=t.type_name) for t in pokemon.types
                        ],
                    )

                    session.add(db_pokemon)
                    logger.debug(
                        f'Pokemon {db_pokemon.name} adicionado para persistência.'
                    )

        except Exception as e:
            logger.error(f'Erro ao salvar informações no banco de dados: {e}')
            raise

    @classmethod
    def exporta_tabelas_bd(cls) -> None:
        
        for nome_tabela in table_registry.metadata.tables.keys():
            caminho_base = settings.CAMINHO_DADOS + settings.NOME_PASTA_SOT
            try:
                base = f'{caminho_base}{nome_tabela}/today_date/'
                folder = cls._build_folder_path(base)
                destino_tabela = str(folder / f'{nome_tabela}.parquet')
                cls._exporta_para_parquet(nome_tabela, destino_tabela)
                logger.info(f'Tabela {nome_tabela!r} exportada para {destino_tabela}')
            except Exception as e:
                logger.error(f'Erro ao exportar tabela {nome_tabela!r}: {e}')
                raise
