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
    tipo = PokemonTypeSchemaFactory.build(type={'name': 'grass', 'url': ''})
    assert tipo.type_name == 'grass'


def test_type_description_excluido_do_model_dump() -> None:
    tipo = PokemonTypeSchemaFactory.build()
    assert 'type_description' not in tipo.model_dump()


# --- PokemonStatsSchema ---


def test_stat_name_extraido_do_campo_stat() -> None:
    stat = PokemonStatsSchemaFactory.build(stat={'name': 'speed', 'url': ''})
    assert stat.stat_name == 'speed'


def test_base_stat_e_inteiro() -> None:
    stat = PokemonStatsSchemaFactory.build()
    assert isinstance(stat.base_stat, int)


# --- PokemonAbilitySchema ---


def test_ability_name_extraido_do_campo_ability() -> None:
    ability = PokemonAbilitySchemaFactory.build(ability={'name': 'overgrow', 'url': ''})
    assert ability.ability_name == 'overgrow'


def test_is_hidden_e_bool() -> None:
    ability = PokemonAbilitySchemaFactory.build()
    assert isinstance(ability.is_hidden, bool)


# --- PokemonSchema ---


def test_parse_pokemon_valido() -> None:
    pokemon = PokemonSchemaFactory.build()
    assert isinstance(pokemon, PokemonSchema)
    assert isinstance(pokemon.pokemon_id, int)
    assert isinstance(pokemon.name, str)


def test_abilities_lista_de_abilities() -> None:
    abilities = PokemonAbilitySchemaFactory.build_batch(3)
    pokemon = PokemonSchemaFactory.build(abilities=abilities)
    assert len(pokemon.abilities) == 3


def test_stats_lista_de_stats() -> None:
    stats = PokemonStatsSchemaFactory.build_batch(6)
    pokemon = PokemonSchemaFactory.build(stats=stats)
    assert len(pokemon.stats) == 6


def test_types_lista_de_types() -> None:
    types = PokemonTypeSchemaFactory.build_batch(2)
    pokemon = PokemonSchemaFactory.build(types=types)
    assert len(pokemon.types) == 2


def test_base_experience_ausente_usa_default_zero() -> None:
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
    p1, p2 = PokemonSchemaFactory.build_batch(2)
    assert p1.pokemon_id != p2.pokemon_id


def test_pokemon_invalido_levanta_erro() -> None:
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
