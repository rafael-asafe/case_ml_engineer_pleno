"""Factories para geração de dados de teste usando factory-boy e Faker.

Fornece factories baseadas em ``factory.Factory`` para criar instâncias dos
schemas Pydantic sem precisar construir manualmente os payloads da PokéAPI.
Úteis em testes unitários para isolar a lógica de negócio da estrutura da API.

Uso típico::

    from factories import PokemonSchemaFactory, PokemonAbilitySchemaFactory

    # Cria uma instância com dados aleatórios
    pokemon = PokemonSchemaFactory.build()

    # Sobrescreve campos específicos
    pokemon = PokemonSchemaFactory.build(name='pikachu')

    # Cria um lote de instâncias
    pokemons = PokemonSchemaFactory.build_batch(10)
"""

import factory
from faker import Faker

from database.schemas import (
    PokemonAbilitySchema,
    PokemonSchema,
    PokemonStatsSchema,
    PokemonTypeSchema,
)

fake = Faker()


class PokemonTypeSchemaFactory(factory.Factory):
    """Factory para ``PokemonTypeSchema``.

    Gera instâncias com slot sequencial e dicionário ``type`` aleatório no
    formato esperado pela PokéAPI (``{'name': str, 'url': str}``).

    Atributos gerados:
        slot: Inteiro sequencial iniciando em 1 (1 = tipo primário).
        type: Dicionário com ``name`` (palavra aleatória) e ``url`` (URL falsa).
    """

    class Meta:
        model = PokemonTypeSchema

    slot = factory.Sequence(lambda n: n + 1)
    type = factory.LazyFunction(lambda: {'name': fake.word(), 'url': fake.url()})


class PokemonStatsSchemaFactory(factory.Factory):
    """Factory para ``PokemonStatsSchema``.

    Gera instâncias com estatística base aleatória e dicionário ``stat``
    no formato da PokéAPI.

    Atributos gerados:
        base_stat: Inteiro aleatório entre 1 e 255.
        stat: Dicionário com ``name`` (palavra aleatória) e ``url`` (URL falsa).
    """

    class Meta:
        model = PokemonStatsSchema

    base_stat = factory.LazyFunction(lambda: fake.random_int(min=1, max=255))
    stat = factory.LazyFunction(lambda: {'name': fake.word(), 'url': fake.url()})


class PokemonAbilitySchemaFactory(factory.Factory):
    """Factory para ``PokemonAbilitySchema``.

    Gera instâncias com habilidade aleatória e flag ``is_hidden`` randômica,
    simulando tanto habilidades normais quanto habilidades ocultas.

    Atributos gerados:
        ability: Dicionário com ``name`` (palavra aleatória) e ``url`` (URL falsa).
        is_hidden: Booleano aleatório (``True`` ou ``False``).
    """

    class Meta:
        model = PokemonAbilitySchema

    ability = factory.LazyFunction(lambda: {'name': fake.word(), 'url': fake.url()})
    is_hidden = factory.LazyFunction(lambda: fake.boolean())


class PokemonSchemaFactory(factory.Factory):
    """Factory para ``PokemonSchema`` (schema completo do Pokémon).

    Gera instâncias completas com ID sequencial único, nome aleatório e
    listas de habilidades, estatísticas e tipos pré-construídas com valores
    aleatórios. O campo ``pokemon_id`` é renomeado para ``id`` via ``Meta.rename``
    para respeitar o alias do schema Pydantic.

    Atributos gerados:
        pokemon_id: Inteiro sequencial único por instância (mapeado para ``id``).
        name: Primeiro nome aleatório em letras minúsculas.
        height: Inteiro aleatório entre 1 e 100 (decímetros).
        weight: Inteiro aleatório entre 1 e 1000 (hectogramas).
        base_experience: Inteiro aleatório entre 0 e 500.
        abilities: Lista com 2 instâncias de ``PokemonAbilitySchema``.
        stats: Lista com 6 instâncias de ``PokemonStatsSchema``.
        types: Lista com 1 instância de ``PokemonTypeSchema``.
    """

    class Meta:
        model = PokemonSchema
        rename = {'pokemon_id': 'id'}

    pokemon_id = factory.Sequence(lambda n: n + 1)
    name = factory.LazyFunction(lambda: fake.first_name().lower())
    height = factory.LazyFunction(lambda: fake.random_int(min=1, max=100))
    weight = factory.LazyFunction(lambda: fake.random_int(min=1, max=1000))
    base_experience = factory.LazyFunction(lambda: fake.random_int(min=0, max=500))
    abilities = factory.LazyFunction(lambda: PokemonAbilitySchemaFactory.build_batch(2))
    stats = factory.LazyFunction(lambda: PokemonStatsSchemaFactory.build_batch(6))
    types = factory.LazyFunction(lambda: PokemonTypeSchemaFactory.build_batch(1))
