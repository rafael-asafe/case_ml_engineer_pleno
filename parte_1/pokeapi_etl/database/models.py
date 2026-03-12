"""Modelos ORM do banco de dados usando SQLAlchemy com mapeamento dataclass.

Define as tabelas relacionais que armazenam os dados normalizados dos Pokémons
extraídos da PokéAPI. Todos os modelos são registrados em ``table_registry`` e
utilizam o padrão ``mapped_as_dataclass`` do SQLAlchemy 2.x.

Estrutura das tabelas:
    - ``pokemon``: Entidade principal com dados gerais do Pokémon.
    - ``pokemon_ability``: Habilidades associadas a cada Pokémon.
    - ``pokemon_stats``: Estatísticas base (HP, ataque, defesa, etc.).
    - ``pokemon_type``: Tipo(s) elemental(is) do Pokémon (fogo, água, etc.).
"""

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, registry, relationship

table_registry = registry()


@table_registry.mapped_as_dataclass
class Pokemon:
    """Modelo principal que representa um Pokémon no banco de dados.

    Tabela: ``pokemon``

    Attributes:
        pokemon_id: Identificador único do Pokémon (chave primária), equivalente
            ao campo ``id`` retornado pela PokéAPI.
        name: Nome do Pokémon em letras minúsculas (ex.: ``'bulbasaur'``).
        height: Altura do Pokémon em decímetros.
        weight: Peso do Pokémon em hectogramas.
        base_experience: Experiência base concedida ao derrotar este Pokémon.
            Padrão 0 para Pokémons sem esse dado na API.
        abilities: Lista de habilidades associadas. Relacionamento 1:N com
            ``PokemonAbility``; deletados em cascata junto ao Pokémon pai.
        stats: Lista de estatísticas base. Relacionamento 1:N com
            ``PokemonStats``; deletados em cascata junto ao Pokémon pai.
        types: Lista de tipos elementais. Relacionamento 1:N com
            ``PokemonType``; deletados em cascata junto ao Pokémon pai.
    """

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
    """Modelo que representa o tipo elemental de um Pokémon.

    Tabela: ``pokemon_type``

    Chave primária composta por ``(type_name, pokemon_id)``, permitindo que um
    Pokémon possua múltiplos tipos (ex.: Bulbasaur é Planta e Veneno).

    Attributes:
        type_name: Nome do tipo elemental (ex.: ``'grass'``, ``'poison'``).
        pokemon_id: Chave estrangeira referenciando ``pokemon.pokemon_id``.
            Preenchido automaticamente pelo ORM via relacionamento.
        pokemon: Referência ao ``Pokemon`` pai. Usado internamente pelo ORM.
    """

    __tablename__ = "pokemon_type"

    type_name: Mapped[str] = mapped_column(primary_key=True)
    pokemon_id: Mapped[int] = mapped_column(ForeignKey("pokemon.pokemon_id", ondelete="cascade", onupdate="cascade"), primary_key=True,init=False)

    pokemon: Mapped["Pokemon"] = relationship("Pokemon", back_populates="types", init=False)

@table_registry.mapped_as_dataclass
class PokemonStats:
    """Modelo que representa uma estatística base de um Pokémon.

    Tabela: ``pokemon_stats``

    Chave primária composta por ``(stat_name, pokemon_id)``. Cada Pokémon
    possui tipicamente 6 estatísticas: hp, attack, defense, special-attack,
    special-defense e speed.

    Attributes:
        stat_name: Nome da estatística (ex.: ``'hp'``, ``'attack'``).
        base_stat: Valor numérico base da estatística (intervalo típico: 1–255).
        pokemon_id: Chave estrangeira referenciando ``pokemon.pokemon_id``.
            Preenchido automaticamente pelo ORM via relacionamento.
        pokemon: Referência ao ``Pokemon`` pai. Usado internamente pelo ORM.
    """

    __tablename__ = "pokemon_stats"

    stat_name: Mapped[str] = mapped_column(primary_key=True)
    base_stat: Mapped[int]
    pokemon_id: Mapped[int] = mapped_column(ForeignKey("pokemon.pokemon_id", ondelete="cascade", onupdate="cascade"), primary_key=True,init=False)

    pokemon: Mapped["Pokemon"] = relationship("Pokemon", back_populates="stats", init=False)

@table_registry.mapped_as_dataclass
class PokemonAbility:
    """Modelo que representa uma habilidade de um Pokémon.

    Tabela: ``pokemon_ability``

    Chave primária composta por ``(ability_name, pokemon_id)``. Um Pokémon pode
    ter habilidades normais e habilidades ocultas (hidden abilities).

    Attributes:
        ability_name: Nome da habilidade (ex.: ``'overgrow'``, ``'chlorophyll'``).
        is_hidden: Indica se a habilidade é oculta (``True``) ou normal (``False``).
            Armazenada como inteiro no SQLite e convertida para booleano na exportação.
        pokemon_id: Chave estrangeira referenciando ``pokemon.pokemon_id``.
            Preenchido automaticamente pelo ORM via relacionamento.
        pokemon: Referência ao ``Pokemon`` pai. Usado internamente pelo ORM.
    """

    __tablename__ = "pokemon_ability"

    ability_name: Mapped[str] = mapped_column(primary_key=True)
    is_hidden: Mapped[bool]

    pokemon_id: Mapped[int] = mapped_column(ForeignKey("pokemon.pokemon_id", ondelete="cascade", onupdate="cascade"), primary_key=True,init=False)

    pokemon: Mapped["Pokemon"] = relationship("Pokemon", back_populates="abilities", init=False)
