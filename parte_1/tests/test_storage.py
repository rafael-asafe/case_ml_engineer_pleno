from unittest.mock import MagicMock

import pytest

from database.schemas import PokemonSchema
from factories import PokemonSchemaFactory
from storage.storage import OperadorArmazenamento


@pytest.fixture()
def make_response():
    """Fixture que retorna uma factory de mock de httpx.Response a partir de um PokemonSchema."""

    def _factory(pokemon: PokemonSchema) -> MagicMock:
        """Reconstrói o payload no formato original da API (com aliases) para que
        PokemonSchema(**retorno.json()) consiga re-parsear corretamente."""
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
    pokemon = PokemonSchemaFactory.build()
    resultado = list(OperadorArmazenamento.gerar_pokemons([make_response(pokemon)]))
    assert len(resultado) == 1
    assert isinstance(resultado[0], PokemonSchema)


def test_gerar_pokemons_preserva_nome(make_response) -> None:
    pokemon = PokemonSchemaFactory.build(name='pikachu')
    resultado = next(OperadorArmazenamento.gerar_pokemons([make_response(pokemon)]))
    assert resultado.name == 'pikachu'


def test_gerar_pokemons_multiplos_retornos(make_response) -> None:
    pokemons = PokemonSchemaFactory.build_batch(3)
    responses = [make_response(p) for p in pokemons]
    resultado = list(OperadorArmazenamento.gerar_pokemons(responses))
    assert len(resultado) == 3


def test_gerar_pokemons_lista_vazia() -> None:
    resultado = list(OperadorArmazenamento.gerar_pokemons([]))
    assert resultado == []


def test_gerar_pokemons_ids_preservados(make_response) -> None:
    pokemons = PokemonSchemaFactory.build_batch(2)
    responses = [make_response(p) for p in pokemons]
    resultado = list(OperadorArmazenamento.gerar_pokemons(responses))
    assert resultado[0].pokemon_id == pokemons[0].pokemon_id
    assert resultado[1].pokemon_id == pokemons[1].pokemon_id
