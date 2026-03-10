from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, registry, relationship

table_registry = registry()


@table_registry.mapped_as_dataclass
class Pokemon:
    __tablename__ = "pokemon"

    pokemon_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    height: Mapped[int]
    weight: Mapped[int]
    base_experience: Mapped[int] = mapped_column(default=0)

    abilities: Mapped[list["PokemonAbility"]] = relationship(back_populates="pokemon", cascade="all, delete-orphan",default_factory=list)
    stats: Mapped[list["PokemonStats"]] = relationship(back_populates="pokemon", cascade="all, delete-orphan",default_factory=list)
    types: Mapped[list["PokemonType"]] = relationship(back_populates="pokemon", cascade="all, delete-orphan",default_factory=list)


@table_registry.mapped_as_dataclass
class PokemonType:
    __tablename__ = "pokemon_type"

    type_name: Mapped[str] = mapped_column(primary_key=True)
    pokemon_id: Mapped[int] = mapped_column(ForeignKey("pokemon.pokemon_id", ondelete="cascade", onupdate="cascade"), primary_key=True,init=False)

    pokemon: Mapped["Pokemon"] = relationship("Pokemon", back_populates="types", init=False)

@table_registry.mapped_as_dataclass
class PokemonStats:
    __tablename__ = "pokemon_stats"

    stat_name: Mapped[str] = mapped_column(primary_key=True)
    base_stat: Mapped[str] 
    pokemon_id: Mapped[int] = mapped_column(ForeignKey("pokemon.pokemon_id", ondelete="cascade", onupdate="cascade"), primary_key=True,init=False)

    pokemon: Mapped["Pokemon"] = relationship("Pokemon", back_populates="stats", init=False)

@table_registry.mapped_as_dataclass
class PokemonAbility:
    __tablename__ = "pokemon_ability"

    ability_name: Mapped[str] = mapped_column(primary_key=True)
    is_hidden: Mapped[bool]

    pokemon_id: Mapped[int] = mapped_column(ForeignKey("pokemon.pokemon_id", ondelete="cascade", onupdate="cascade"), primary_key=True,init=False)

    pokemon: Mapped["Pokemon"] = relationship("Pokemon", back_populates="abilities", init=False)
