"""Testes unitários para os schemas Pydantic de validação da PokéAPI.

Cobre o comportamento de validação, extração de campos computados e
serialização dos schemas: ``PokemonTypeSchema``, ``PokemonStatsSchema``,
``PokemonAbilitySchema`` e ``PokemonSchema``.
"""

import pytest

from database.schemas import PokemonSchema
from factories import (
    PokemonAbilitySchemaFactory,
    PokemonSchemaFactory,
    PokemonStatsSchemaFactory,
    PokemonTypeSchemaFactory,
)

# --- PokemonTypeSchema ---


def test_type_name_extraido_do_campo_type() -> None:
    """Verifica que ``type_name`` é extraído corretamente do dicionário ``type``."""
    tipo = PokemonTypeSchemaFactory.build(type={'name': 'grass', 'url': ''})
    assert tipo.type_name == 'grass'


def test_type_description_excluido_do_model_dump() -> None:
    """Verifica que o campo intermediário ``type_description`` não aparece na serialização."""
    tipo = PokemonTypeSchemaFactory.build()
    assert 'type_description' not in tipo.model_dump()


# --- PokemonStatsSchema ---


def test_stat_name_extraido_do_campo_stat() -> None:
    """Verifica que ``stat_name`` é extraído corretamente do dicionário ``stat``."""
    stat = PokemonStatsSchemaFactory.build(stat={'name': 'speed', 'url': ''})
    assert stat.stat_name == 'speed'


def test_base_stat_e_inteiro() -> None:
    """Verifica que ``base_stat`` é sempre um inteiro após validação pelo Pydantic."""
    stat = PokemonStatsSchemaFactory.build()
    assert isinstance(stat.base_stat, int)


# --- PokemonAbilitySchema ---


def test_ability_name_extraido_do_campo_ability() -> None:
    """Verifica que ``ability_name`` é extraído corretamente do dicionário ``ability``."""
    ability = PokemonAbilitySchemaFactory.build(ability={'name': 'overgrow', 'url': ''})
    assert ability.ability_name == 'overgrow'


def test_is_hidden_e_bool() -> None:
    """Verifica que ``is_hidden`` é sempre um booleano após validação pelo Pydantic."""
    ability = PokemonAbilitySchemaFactory.build()
    assert isinstance(ability.is_hidden, bool)


# --- PokemonSchema ---


def test_parse_pokemon_valido() -> None:
    """Verifica que um Pokémon gerado pela factory produz uma instância válida de ``PokemonSchema``."""
    pokemon = PokemonSchemaFactory.build()
    assert isinstance(pokemon, PokemonSchema)
    assert isinstance(pokemon.pokemon_id, int)
    assert isinstance(pokemon.name, str)


def test_abilities_lista_de_abilities() -> None:
    """Verifica que a lista de habilidades preserva a quantidade de itens fornecida."""
    abilities = PokemonAbilitySchemaFactory.build_batch(3)
    pokemon = PokemonSchemaFactory.build(abilities=abilities)
    assert len(pokemon.abilities) == 3


def test_stats_lista_de_stats() -> None:
    """Verifica que a lista de estatísticas preserva a quantidade de itens fornecida."""
    stats = PokemonStatsSchemaFactory.build_batch(6)
    pokemon = PokemonSchemaFactory.build(stats=stats)
    assert len(pokemon.stats) == 6


def test_types_lista_de_types() -> None:
    """Verifica que a lista de tipos preserva a quantidade de itens fornecida."""
    types = PokemonTypeSchemaFactory.build_batch(2)
    pokemon = PokemonSchemaFactory.build(types=types)
    assert len(pokemon.types) == 2


def test_base_experience_ausente_usa_default_zero() -> None:
    """Verifica que ``base_experience`` assume valor 0 quando omitido no payload."""
    payload = {
        'id': 1,
        'name': 'missingno',
        'height': 1,
        'weight': 1,
        'abilities': [],
        'stats': [],
        'types': [],
    }
    pokemon = PokemonSchema(**payload)
    assert pokemon.base_experience == 0


def test_pokemon_id_unico_por_instancia() -> None:
    """Verifica que IDs gerados pela factory são únicos entre instâncias distintas."""
    p1, p2 = PokemonSchemaFactory.build_batch(2)
    assert p1.pokemon_id != p2.pokemon_id


def test_pokemon_invalido_levanta_erro() -> None:
    """Verifica que o Pydantic levanta exceção ao receber ``id`` com tipo inválido."""
    with pytest.raises(Exception):
        PokemonSchema(
            id='nao_e_int',
            name='erro',
            height=0,
            weight=0,
            abilities=[],
            stats=[],
            types=[],
        )


def test_stat_description_excluido_do_model_dump() -> None:
    """Verifica que o campo intermediário ``stat_description`` não aparece na serialização."""
    stat = PokemonStatsSchemaFactory.build()
    assert 'stat_description' not in stat.model_dump()


def test_abilities_description_excluido_do_model_dump() -> None:
    """Verifica que o campo intermediário ``abilities_description`` não aparece na serialização."""
    ability = PokemonAbilitySchemaFactory.build()
    assert 'abilities_description' not in ability.model_dump()
