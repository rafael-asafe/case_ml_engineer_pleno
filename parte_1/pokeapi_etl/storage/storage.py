"""Operações de armazenamento e persistência dos dados extraídos da PokéAPI.

Contém a classe ``OperadorArmazenamento``, responsável pelas três etapas de carga:
1. Gravação dos dados brutos em JSONL (camada SOR — System of Record).
2. Persistência dos dados normalizados no banco de dados SQLite (camada ODS).
3. Exportação das tabelas do banco para Parquet particionado por data (camada SOT).

O particionamento por data segue o padrão ``YYYY/MM/DD``, substituindo a
string literal ``'today_date'`` nos caminhos configurados.
"""

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
    """Classe utilitária com métodos de classe para persistência dos dados de Pokémons.

    Não possui estado de instância; todos os métodos são ``@classmethod`` para
    facilitar o uso direto sem instanciação.
    """

    @classmethod
    def _build_folder_path(cls, base: str) -> Path:
        """Resolve e cria o diretório de destino substituindo ``'today_date'`` pela data atual.

        Substitui a string literal ``'today_date'`` no caminho base pela data de
        hoje formatada como ``'YYYY/MM/DD'``, criando toda a hierarquia de diretórios
        necessária com ``mkdir(parents=True, exist_ok=True)``.

        Args:
            base: Caminho base com a string ``'today_date'`` a ser substituída
                (ex.: ``'./data/SOR/pokemons/today_date/'``).

        Returns:
            Path: Objeto ``Path`` apontando para o diretório criado ou já existente
                (ex.: ``Path('./data/SOR/pokemons/2026/03/11/')``).
        """
        folder = Path(base.replace('today_date', date.today().strftime('%Y/%m/%d')))
        folder.mkdir(parents=True, exist_ok=True)
        return folder

    @classmethod
    def gerar_pokemons(cls, retornos: list[Response]) -> PokemonSchema:
        """Gera instâncias de ``PokemonSchema`` a partir de uma lista de respostas HTTP.

        Itera sobre as respostas, desserializa o JSON de cada uma e valida os dados
        via Pydantic. Funciona como gerador para evitar carregar todos os Pokémons
        em memória simultaneamente.

        Args:
            retornos: Lista de objetos ``httpx.Response`` retornados pelas chamadas
                a ``busca_pokemon``. Cada resposta deve conter o JSON completo de
                um Pokémon no formato da PokéAPI.

        Yields:
            PokemonSchema: Instância validada com os dados normalizados do Pokémon.

        Raises:
            pydantic.ValidationError: Se o JSON da resposta não corresponder ao
                schema esperado por ``PokemonSchema``.
        """
        for retorno in retornos:
            yield PokemonSchema(**retorno.json())

    @classmethod
    def registra_dados_brutos(
        cls, retornos: list[Response], nome_pasta: str, nome_arquivo: str
    ) -> None:
        """Persiste os dados brutos dos Pokémons em um arquivo JSONL (camada SOR).

        Cada linha do arquivo corresponde ao JSON serializado de um ``PokemonSchema``,
        utilizando o formato JSONL (JSON Lines) para facilitar processamento incremental.
        O arquivo é sobrescrito a cada execução.

        Args:
            retornos: Lista de respostas HTTP com os dados dos Pokémons.
            nome_pasta: Subdiretório relativo a ``Settings().CAMINHO_DADOS`` onde o
                arquivo será gravado. Deve conter ``'today_date'`` para particionamento
                (ex.: ``'SOR/pokemons/today_date/'``).
            nome_arquivo: Nome do arquivo de destino (ex.: ``'pokemons.jsonl'``).

        Raises:
            Exception: Propaga erros de I/O ou validação, registrando a mensagem
                no logger antes de re-lançar.
        """
        pokemons = cls.gerar_pokemons(retornos)
        folder = cls._build_folder_path(Settings().CAMINHO_DADOS + nome_pasta)
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
        """Persiste os dados normalizados dos Pokémons no banco de dados relacional.

        Para cada Pokémon, verifica se já existe no banco (idempotência) antes de
        inserir. Caso já esteja registrado, o Pokémon é ignorado com log de debug.
        Habilidades, estatísticas e tipos são inseridos junto ao Pokémon pai em
        uma única transação via cascade.

        Args:
            retornos: Lista de respostas HTTP com os dados dos Pokémons.

        Raises:
            Exception: Propaga erros de banco de dados (integridade, conexão, etc.),
                realizando rollback automático via ``get_session()`` e registrando
                a mensagem no logger antes de re-lançar.

        Note:
            A operação é idempotente: Pokémons já presentes no banco são ignorados,
            permitindo que o pipeline seja reexecutado sem duplicar registros.
        """
        try:
            pokemons = cls.gerar_pokemons(retornos)

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
        """Exporta todas as tabelas do banco de dados para arquivos Parquet (camada SOT).

        Itera sobre todas as tabelas registradas em ``table_registry.metadata`` e,
        para cada uma, cria o diretório particionado por data e invoca
        ``exporta_para_parquet``. O caminho de saída segue o padrão:
        ``{CAMINHO_DADOS}/{NOME_PASTA_SOT}/{nome_tabela}/YYYY/MM/DD/{nome_tabela}.parquet``.

        Raises:
            Exception: Se a exportação de qualquer tabela falhar, o erro é logado
                e re-lançado, interrompendo o processo para as tabelas restantes.
        """
        for nome_tabela in table_registry.metadata.tables.keys():
            caminho_base = Settings().CAMINHO_DADOS + Settings().NOME_PASTA_SOT
            try:
                base = f'{caminho_base}{nome_tabela}/today_date/'
                folder = cls._build_folder_path(base)
                destino_tabela = str(folder / f'{nome_tabela}.parquet')
                exporta_para_parquet(nome_tabela, destino_tabela)
                logger.info(f'Tabela {nome_tabela!r} exportada para {destino_tabela}')
            except Exception as e:
                logger.error(f'Erro ao exportar tabela {nome_tabela!r}: {e}')
                raise
