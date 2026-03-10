from datetime import date
from pathlib import Path

from httpx import Response
from sqlalchemy import select

from database.database import exporta_para_parquet, get_session
from database.models import (
    Pokemon,
    PokemonAbility,
    PokemonStats,
    PokemonType,
    table_registry,
)
from database.schemas import PokemonSchema
from utils.logger import logger
from utils.settings import Settings


class OperadorArmazenamento:
    @classmethod
    def gerar_pokemons(cls, retornos: list[Response]) -> PokemonSchema:
        for retorno in retornos:
            yield PokemonSchema(**retorno.json())

    @classmethod
    def registra_dados_brutos(cls, retornos: list[Response], nome_pasta: str, nome_arquivo: str) -> None:
        pokemons = cls.gerar_pokemons(retornos)

        folderpath = Settings().CAMINHO_DADOS + nome_pasta.replace(
            'today_date', date.today().strftime('%Y/%m/%d')
        )
        filepath = folderpath + nome_arquivo

        folder_path = Path(folderpath)
        folder_path.mkdir(parents=True, exist_ok=True)

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                for pokemon in pokemons:
                    f.write(pokemon.model_dump_json() + '\n')

        except Exception as e:
            logger.error(f'erro ao salvar requisição: {e}')
            raise
     
    # TODO terminar de criar a classe
    @classmethod
    def registra_dados_bd(cls, retornos: list[Response]) -> None:       
        try: 
            pokemons = cls.gerar_pokemons(retornos)
            
            with get_session() as session:
                for pokemon in pokemons:
                    db_pokemon =  session.scalar(
                    select(Pokemon).where(Pokemon.pokemon_id == pokemon.pokemon_id)
                )

                    if db_pokemon:
                        logger.debug(f"Informações do pokemon {pokemon.name} registradas anteriormente!")
                        continue
                
                    db_pokemon = Pokemon(
                        pokemon_id = pokemon.pokemon_id,
                        name = pokemon.name,
                        height = pokemon.height,
                        weight  = pokemon.weight,
                        base_experience = pokemon.base_experience,
                        abilities=[
                            PokemonAbility(ability_name=a.ability_name, is_hidden=a.is_hidden) 
                            for a in pokemon.abilities
                        ],
                        stats=[
                            PokemonStats(stat_name=s.stat_name, base_stat=s.base_stat) 
                            for s in pokemon.stats
                        ],
                        types=[
                            PokemonType(type_name=t.type_name) 
                            for t in pokemon.types
                        ])

                    session.add(db_pokemon)

                    session.commit()
                    session.refresh(db_pokemon)

                    logger.debug(f"pokemon {db_pokemon.name} registrado com sucesso!")               
            

        except Exception as e:
            logger.error(
                f"erro ao salvar informacoes no banco de dados: {e}"
            )
            raise
        
    #TODO - não é elegante mas resolve 
    @classmethod
    def exporta_tabelas_bd(cls) -> None:
        try:
            lista_tabelas_bd =  table_registry.metadata.tables.keys()
            
            for nome_tabela in lista_tabelas_bd:
                
                #TODO - repetindo código
                folderpath = f"{Settings().CAMINHO_DADOS + Settings().NOME_PASTA_SOT}{nome_tabela}/{date.today().strftime('%Y/%m/%d')}/"
                folder_path = Path(folderpath)
                folder_path.mkdir(parents=True, exist_ok=True)
                
                destino_tabela = f"{folderpath}{nome_tabela}.parquet"
                
                exporta_para_parquet(nome_tabela,destino_tabela)
    
        except Exception as e:      
            logger.error(
                f"erro ao exportar tabela do banco de dados: {e}"
            )
            raise
