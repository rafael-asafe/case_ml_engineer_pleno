from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, registry

table_registry = registry()


@table_registry.mapped_as_dataclass
class Pokemon:
    __tablename__ = "pokemon"

    pokemon_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    height: Mapped[int]
    weight: Mapped[int]
    base_experience: Mapped[int]


@table_registry.mapped_as_dataclass
class PokemonType:
    __tablename__ = "pokemon_type"

    pokemon_id: Mapped[int] = ForeignKey(
        "pokemon.id_regiao", ondelete="cascade", onupdate="cascade", primary_key=True
    )
    type_name: Mapped[str] = mapped_column(primary_key=True)


@table_registry.mapped_as_dataclass
class PokemonStats:
    __tablename__ = "pokemon_stats"

    pokemon_id: Mapped[int] = ForeignKey(
        "pokemon.id_regiao", ondelete="cascade", onupdate="cascade"
    )
    stat_name: Mapped[str]
    base_stat: Mapped[str]


@table_registry.mapped_as_dataclass
class PokemonAbility:
    __tablename__ = "pokemon_ability"

    pokemon_id: Mapped[int] = ForeignKey(
        "pokemon.id_regiao", ondelete="cascade", onupdate="cascade"
    )
    ability_name: Mapped[str]
    is_hidden: Mapped[bool]
