from pydantic import BaseModel, Field, computed_field


class PokemonTypeSchema(BaseModel):
    slot: int
    type_description: dict[str, str] = Field(alias="type")

    @computed_field
    def type_name(self) -> str:
        return self.type_description.name


class PokemonStatsSchema(BaseModel):
    base_stat: int
    stat_description: dict[str, str] = Field(alias="stat")

    @computed_field
    def stat_name(self) -> str:
        return self.stat_description.get('name')


class PokemonAbilitySchema(BaseModel):
    abilities_description: dict[str, str] = Field(alias="ability")
    is_hidden: bool

    @computed_field
    def ability_name(self) -> str:
        return self.abilities_description.get('name')


class PokemonSchema(BaseModel):
    pokemon_id: int = Field(alias="id")
    name: str
    height: int
    weight: int
    base_experience: int
    abilities: list[PokemonAbilitySchema]
    stats: list[PokemonStatsSchema]
    types: list[PokemonTypeSchema]
