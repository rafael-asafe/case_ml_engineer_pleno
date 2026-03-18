

import json
from datetime import date
from unittest.mock import patch

import pytest
from sqlalchemy import func, select

from database.database import get_session
from database.models import Pokemon, table_registry
from database.schemas import PokemonSchema
from factories import PokemonSchemaFactory
from storage.storage import OperadorArmazenamento


def test_gerar_pokemons_retorna_schema_valido(make_response) -> None:
    
    pokemon = PokemonSchemaFactory.build()
    resultado = list(OperadorArmazenamento._gerar_pokemons([make_response(pokemon)]))
    assert len(resultado) == 1
    assert isinstance(resultado[0], PokemonSchema)


def test_gerar_pokemons_preserva_nome(make_response) -> None:
    
    pokemon = PokemonSchemaFactory.build(name='pikachu')
    resultado = next(OperadorArmazenamento._gerar_pokemons([make_response(pokemon)]))
    assert resultado.name == 'pikachu'


def test_gerar_pokemons_multiplos_retornos(make_response) -> None:
    
    pokemons = PokemonSchemaFactory.build_batch(3)
    responses = [make_response(p) for p in pokemons]
    resultado = list(OperadorArmazenamento._gerar_pokemons(responses))
    assert len(resultado) == 3


def test_gerar_pokemons_lista_vazia() -> None:
    
    resultado = list(OperadorArmazenamento._gerar_pokemons([]))
    assert resultado == []


def test_gerar_pokemons_ids_preservados(make_response) -> None:
    
    pokemons = PokemonSchemaFactory.build_batch(2)
    responses = [make_response(p) for p in pokemons]
    resultado = list(OperadorArmazenamento._gerar_pokemons(responses))
    assert resultado[0].pokemon_id == pokemons[0].pokemon_id
    assert resultado[1].pokemon_id == pokemons[1].pokemon_id


# --- _build_folder_path ---


def test_build_folder_path_substitui_today_date(tmp_path) -> None:
    
    base = str(tmp_path / 'data' / 'today_date')
    resultado = OperadorArmazenamento._build_folder_path(base)
    data_esperada = date.today().strftime('%Y/%m/%d')
    assert str(resultado).endswith(data_esperada)


def test_build_folder_path_cria_diretorio(tmp_path) -> None:
    
    base = str(tmp_path / 'today_date')
    resultado = OperadorArmazenamento._build_folder_path(base)
    assert resultado.exists()
    assert resultado.is_dir()


# --- registra_dados_brutos ---


def test_registra_dados_brutos_cria_arquivo_jsonl(tmp_path, make_response) -> None:
    
    pokemons = PokemonSchemaFactory.build_batch(3)
    responses = [make_response(p) for p in pokemons]
    OperadorArmazenamento.registra_dados_brutos(
        responses, str(tmp_path), 'pokemons.jsonl'
    )
    arquivos = list(tmp_path.rglob('*.jsonl'))
    assert len(arquivos) == 1
    linhas = arquivos[0].read_text(encoding='utf-8').strip().split('\n')
    assert len(linhas) == 3


def test_registra_dados_brutos_conteudo_valido_json(tmp_path, make_response) -> None:
    
    pokemon = PokemonSchemaFactory.build()
    responses = [make_response(pokemon)]
    OperadorArmazenamento.registra_dados_brutos(
        responses, str(tmp_path), 'pokemons.jsonl'
    )
    arquivo = list(tmp_path.rglob('*.jsonl'))[0]
    dados = json.loads(arquivo.read_text(encoding='utf-8').strip())
    assert dados['pokemon_id'] == pokemon.pokemon_id
    assert dados['name'] == pokemon.name


def test_registra_dados_brutos_relanca_excecao(tmp_path, make_response) -> None:
    
    pokemon = PokemonSchemaFactory.build()
    responses = [make_response(pokemon)]
    with patch('builtins.open', side_effect=IOError('disco cheio')):
        with pytest.raises(IOError):
            OperadorArmazenamento.registra_dados_brutos(
                responses, 'SOR/today_date/', 'err.jsonl'
            )


def test_registra_dados_bd_insere_pokemon(make_response, cria_tabelas) -> None:
    

    pokemon = PokemonSchemaFactory.build()
    OperadorArmazenamento.registra_dados_bd([make_response(pokemon)])
    with get_session() as session:
        db_pokemon = session.scalar(
            select(Pokemon).where(Pokemon.pokemon_id == pokemon.pokemon_id)
        )
        assert db_pokemon is not None
        assert db_pokemon.name == pokemon.name


def test_registra_dados_bd_idempotente(make_response, cria_tabelas) -> None:
    

    pokemon = PokemonSchemaFactory.build()
    OperadorArmazenamento.registra_dados_bd([make_response(pokemon)])
    OperadorArmazenamento.registra_dados_bd([make_response(pokemon)])
    with get_session() as session:
        count = session.scalar(
            select(func.count())
            .select_from(Pokemon)
            .where(Pokemon.pokemon_id == pokemon.pokemon_id)
        )
    assert count == 1


# --- exporta_tabelas_bd ---


def test_exporta_tabelas_bd_chama_exporta_para_cada_tabela(
    tmp_path, cria_tabelas
) -> None:
    
    with patch('storage.storage.settings.CAMINHO_DADOS', f'{str(tmp_path)}/'):
        OperadorArmazenamento.exporta_tabelas_bd()
    tabelas = list(table_registry.metadata.tables.keys())
    assert len(list(tmp_path.rglob('*.parquet'))) == len(tabelas)


def test_exporta_tabelas_bd_relanca_excecao(tmp_path) -> None:
    
    with patch.object(
        OperadorArmazenamento,
        '_exporta_para_parquet',
        side_effect=RuntimeError('falha parquet'),
    ):
        with patch.object(
            OperadorArmazenamento, '_build_folder_path', return_value=tmp_path
        ):
            with pytest.raises(RuntimeError):
                OperadorArmazenamento.exporta_tabelas_bd()
