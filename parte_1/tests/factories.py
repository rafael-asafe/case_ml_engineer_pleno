

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
    

    class Meta:
        model = PokemonTypeSchema

    slot = factory.Sequence(lambda n: n + 1)
    type = factory.Sequence(lambda n: {'name': f'type_{n}', 'url': ''})


class PokemonStatsSchemaFactory(factory.Factory):
    

    class Meta:
        model = PokemonStatsSchema

    base_stat = factory.LazyFunction(lambda: fake.random_int(min=1, max=255))
    stat = factory.Sequence(lambda n: {'name': f'stat_{n}', 'url': ''})


class PokemonAbilitySchemaFactory(factory.Factory):
    

    class Meta:
        model = PokemonAbilitySchema

    ability = factory.Sequence(lambda n: {'name': f'ability_{n}', 'url': ''})
    is_hidden = factory.LazyFunction(lambda: fake.boolean())


class PokemonSchemaFactory(factory.Factory):
    

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
