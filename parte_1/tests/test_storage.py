"""Testes unitários para ``OperadorArmazenamento``.

Cobre todos os métodos da classe: ``gerar_pokemons``, ``_build_folder_path``,
``registra_dados_brutos``, ``registra_dados_bd`` e ``exporta_tabelas_bd``.
"""

import json
from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from database.models import table_registry
from database.schemas import PokemonSchema
from factories import PokemonSchemaFactory
from storage.storage import OperadorArmazenamento


@pytest.fixture()
def make_response():
    """Fixture que retorna uma factory de mock de httpx.Response a partir de um PokemonSchema.

    Reconstrói o payload no formato original da PokéAPI (com aliases como ``'id'`` e
    dicionários aninhados para ``ability``, ``stat`` e ``type``) para que
    ``PokemonSchema(**retorno.json())`` consiga re-parsear corretamente.

    Returns:
        Callable[[PokemonSchema], MagicMock]: Função interna que recebe um ``PokemonSchema``
            e retorna um ``MagicMock`` com o método ``json()`` configurado para retornar
            o payload no formato da API.
    """

    def _factory(pokemon: PokemonSchema) -> MagicMock:
        """Cria um mock de ``httpx.Response`` a partir de um ``PokemonSchema`` validado.

        Args:
            pokemon: Instância de ``PokemonSchema`` cujos dados serão usados para
                montar o payload no formato original da API.

        Returns:
            MagicMock: Mock com ``json()`` retornando o payload reconstruído com aliases.
        """
        mock = MagicMock()
        mock.json.return_value = {
            'id': pokemon.pokemon_id,
            'name': pokemon.name,
            'height': pokemon.height,
            'weight': pokemon.weight,
            'base_experience': pokemon.base_experience,
            'abilities': [
                {
                    'ability': {'name': a.ability_name, 'url': ''},
                    'is_hidden': a.is_hidden,
                }
                for a in pokemon.abilities
            ],
            'stats': [
                {'base_stat': s.base_stat, 'stat': {'name': s.stat_name, 'url': ''}}
                for s in pokemon.stats
            ],
            'types': [
                {'slot': t.slot, 'type': {'name': t.type_name, 'url': ''}}
                for t in pokemon.types
            ],
        }
        return mock

    return _factory


def test_gerar_pokemons_retorna_schema_valido(make_response) -> None:
    """Verifica que uma única resposta mockada é convertida em um ``PokemonSchema`` válido."""
    pokemon = PokemonSchemaFactory.build()
    resultado = list(OperadorArmazenamento.gerar_pokemons([make_response(pokemon)]))
    assert len(resultado) == 1
    assert isinstance(resultado[0], PokemonSchema)


def test_gerar_pokemons_preserva_nome(make_response) -> None:
    """Verifica que o nome do Pokémon é preservado corretamente após a conversão."""
    pokemon = PokemonSchemaFactory.build(name='pikachu')
    resultado = next(OperadorArmazenamento.gerar_pokemons([make_response(pokemon)]))
    assert resultado.name == 'pikachu'


def test_gerar_pokemons_multiplos_retornos(make_response) -> None:
    """Verifica que múltiplas respostas geram o número correto de schemas."""
    pokemons = PokemonSchemaFactory.build_batch(3)
    responses = [make_response(p) for p in pokemons]
    resultado = list(OperadorArmazenamento.gerar_pokemons(responses))
    assert len(resultado) == 3


def test_gerar_pokemons_lista_vazia() -> None:
    """Verifica que uma lista vazia de respostas resulta em um gerador sem itens."""
    resultado = list(OperadorArmazenamento.gerar_pokemons([]))
    assert resultado == []


def test_gerar_pokemons_ids_preservados(make_response) -> None:
    """Verifica que os IDs dos Pokémons são preservados na ordem original após a conversão."""
    pokemons = PokemonSchemaFactory.build_batch(2)
    responses = [make_response(p) for p in pokemons]
    resultado = list(OperadorArmazenamento.gerar_pokemons(responses))
    assert resultado[0].pokemon_id == pokemons[0].pokemon_id
    assert resultado[1].pokemon_id == pokemons[1].pokemon_id


# --- _build_folder_path ---


def test_build_folder_path_substitui_today_date(tmp_path) -> None:
    """Verifica que 'today_date' é substituído pela data de hoje no formato YYYY/MM/DD."""
    base = str(tmp_path / 'data' / 'today_date')
    resultado = OperadorArmazenamento._build_folder_path(base)
    data_esperada = date.today().strftime('%Y/%m/%d')
    assert str(resultado).endswith(data_esperada)


def test_build_folder_path_cria_diretorio(tmp_path) -> None:
    """Verifica que o diretório de destino é criado fisicamente."""
    base = str(tmp_path / 'today_date')
    resultado = OperadorArmazenamento._build_folder_path(base)
    assert resultado.exists()
    assert resultado.is_dir()


# --- registra_dados_brutos ---


def test_registra_dados_brutos_cria_arquivo_jsonl(tmp_path, make_response) -> None:
    """Verifica que o arquivo JSONL é criado com uma linha por Pokémon."""
    pokemons = PokemonSchemaFactory.build_batch(3)
    responses = [make_response(p) for p in pokemons]
    with patch('storage.storage.Settings') as mock_settings:
        mock_settings.return_value.CAMINHO_DADOS = str(tmp_path) + '/'
        OperadorArmazenamento.registra_dados_brutos(responses, 'SOR/today_date/', 'pokemons.jsonl')
    arquivos = list(tmp_path.rglob('*.jsonl'))
    assert len(arquivos) == 1
    linhas = arquivos[0].read_text(encoding='utf-8').strip().split('\n')
    assert len(linhas) == 3


def test_registra_dados_brutos_conteudo_valido_json(tmp_path, make_response) -> None:
    """Verifica que cada linha do JSONL é um JSON válido com os dados do Pokémon."""
    pokemon = PokemonSchemaFactory.build()
    responses = [make_response(pokemon)]
    with patch('storage.storage.Settings') as mock_settings:
        mock_settings.return_value.CAMINHO_DADOS = str(tmp_path) + '/'
        OperadorArmazenamento.registra_dados_brutos(responses, 'SOR/today_date/', 'pokemons.jsonl')
    arquivo = list(tmp_path.rglob('*.jsonl'))[0]
    dados = json.loads(arquivo.read_text(encoding='utf-8').strip())
    assert dados['pokemon_id'] == pokemon.pokemon_id
    assert dados['name'] == pokemon.name


def test_registra_dados_brutos_relanca_excecao(tmp_path, make_response) -> None:
    """Verifica que exceções de I/O são re-lançadas após o log."""
    pokemon = PokemonSchemaFactory.build()
    responses = [make_response(pokemon)]
    with patch('storage.storage.Settings') as mock_settings:
        mock_settings.return_value.CAMINHO_DADOS = str(tmp_path) + '/'
        with patch('builtins.open', side_effect=IOError('disco cheio')):
            with pytest.raises(IOError):
                OperadorArmazenamento.registra_dados_brutos(responses, 'SOR/today_date/', 'err.jsonl')


# --- registra_dados_bd ---


@pytest.fixture()
def cria_tabelas():
    """Cria e derruba todas as tabelas no banco em memória para cada teste."""
    from database.database import engine
    table_registry.metadata.create_all(engine)
    yield
    table_registry.metadata.drop_all(engine)


def test_registra_dados_bd_insere_pokemon(make_response, cria_tabelas) -> None:
    """Verifica que um novo Pokémon é inserido corretamente no banco de dados."""
    from database.database import get_session
    from database.models import Pokemon
    from sqlalchemy import select

    pokemon = PokemonSchemaFactory.build()
    OperadorArmazenamento.registra_dados_bd([make_response(pokemon)])
    with get_session() as session:
        db_pokemon = session.scalar(select(Pokemon).where(Pokemon.pokemon_id == pokemon.pokemon_id))
        assert db_pokemon is not None
        assert db_pokemon.name == pokemon.name


def test_registra_dados_bd_idempotente(make_response, cria_tabelas) -> None:
    """Verifica que chamadas repetidas com o mesmo Pokémon não duplicam o registro."""
    from database.database import get_session
    from database.models import Pokemon
    from sqlalchemy import func, select

    pokemon = PokemonSchemaFactory.build()
    OperadorArmazenamento.registra_dados_bd([make_response(pokemon)])
    OperadorArmazenamento.registra_dados_bd([make_response(pokemon)])
    with get_session() as session:
        count = session.scalar(
            select(func.count()).select_from(Pokemon).where(Pokemon.pokemon_id == pokemon.pokemon_id)
        )
    assert count == 1


# --- exporta_tabelas_bd ---


def test_exporta_tabelas_bd_chama_exporta_para_cada_tabela(tmp_path) -> None:
    """Verifica que exporta_para_parquet é chamada uma vez por tabela registrada."""
    with patch('storage.storage.exporta_para_parquet') as mock_export:
        with patch.object(OperadorArmazenamento, '_build_folder_path', return_value=tmp_path):
            OperadorArmazenamento.exporta_tabelas_bd()
    tabelas = list(table_registry.metadata.tables.keys())
    assert mock_export.call_count == len(tabelas)


def test_exporta_tabelas_bd_relanca_excecao(tmp_path) -> None:
    """Verifica que exceções de exportação são re-lançadas após o log."""
    with patch('storage.storage.exporta_para_parquet', side_effect=RuntimeError('falha parquet')):
        with patch.object(OperadorArmazenamento, '_build_folder_path', return_value=tmp_path):
            with pytest.raises(RuntimeError):
                OperadorArmazenamento.exporta_tabelas_bd()
