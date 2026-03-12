"""Schemas Pydantic para validação e transformação dos dados da PokéAPI.

Cada schema corresponde a um recurso retornado pela API e realiza a limpeza
e normalização necessárias para persistência no banco de dados. Campos aninhados
da API são achatados via ``computed_field``, e campos intermediários são excluídos
da serialização com ``exclude=True``.
"""

from pydantic import BaseModel, Field, computed_field


class PokemonTypeSchema(BaseModel):
    """Schema de validação para o tipo elemental de um Pokémon.

    Recebe o formato aninhado da API (``{"slot": 1, "type": {"name": "grass", "url": "..."}}``),
    extrai o nome do tipo via ``computed_field`` e exclui o dicionário intermediário
    da serialização final.

    Attributes:
        slot: Posição do tipo na lista (1 = tipo primário, 2 = tipo secundário).
        type_description: Dicionário bruto com ``name`` e ``url`` do tipo. Recebido
            via alias ``'type'`` e excluído do ``model_dump()``.
        type_name: Nome do tipo elemental extraído de ``type_description['name']``
            (ex.: ``'grass'``, ``'fire'``). Campo computado, incluído na serialização.
    """

    slot: int
    type_description: dict[str, str] = Field(alias='type', exclude=True)

    @computed_field
    def type_name(self) -> str:
        """Extrai o nome do tipo a partir do dicionário aninhado retornado pela API."""
        return self.type_description.get('name')


class PokemonStatsSchema(BaseModel):
    """Schema de validação para uma estatística base de um Pokémon.

    Recebe o formato aninhado da API (``{"base_stat": 45, "stat": {"name": "hp", "url": "..."}}``),
    extrai o nome da estatística via ``computed_field`` e exclui o dicionário intermediário.

    Attributes:
        base_stat: Valor numérico base da estatística (ex.: 45 para HP do Bulbasaur).
        stat_description: Dicionário bruto com ``name`` e ``url`` da estatística. Recebido
            via alias ``'stat'`` e excluído do ``model_dump()``.
        stat_name: Nome da estatística extraído de ``stat_description['name']``
            (ex.: ``'hp'``, ``'attack'``, ``'speed'``). Campo computado.
    """

    base_stat: int
    stat_description: dict[str, str] = Field(alias='stat', exclude=True)

    @computed_field
    def stat_name(self) -> str:
        """Extrai o nome da estatística a partir do dicionário aninhado retornado pela API."""
        return self.stat_description.get('name')


class PokemonAbilitySchema(BaseModel):
    """Schema de validação para uma habilidade de um Pokémon.

    Recebe o formato aninhado da API (``{"ability": {"name": "overgrow", "url": "..."}, "is_hidden": false}``),
    extrai o nome da habilidade via ``computed_field`` e exclui o dicionário intermediário.

    Attributes:
        abilities_description: Dicionário bruto com ``name`` e ``url`` da habilidade.
            Recebido via alias ``'ability'`` e excluído do ``model_dump()``.
        is_hidden: Indica se a habilidade é oculta (``True``) ou normal (``False``).
        ability_name: Nome da habilidade extraído de ``abilities_description['name']``
            (ex.: ``'overgrow'``, ``'chlorophyll'``). Campo computado.
    """

    abilities_description: dict[str, str] = Field(alias='ability', exclude=True)
    is_hidden: bool

    @computed_field
    def ability_name(self) -> str:
        """Extrai o nome da habilidade a partir do dicionário aninhado retornado pela API."""
        return self.abilities_description.get('name')


class PokemonSchema(BaseModel):
    """Schema de validação principal para um Pokémon completo.

    Representa a resposta completa do endpoint ``/pokemon/{id}`` da PokéAPI,
    normalizando os dados e compondo os schemas aninhados de habilidades,
    estatísticas e tipos.

    Attributes:
        pokemon_id: Identificador único do Pokémon, mapeado do campo ``'id'`` da API.
        name: Nome do Pokémon em letras minúsculas (ex.: ``'bulbasaur'``).
        height: Altura em decímetros (ex.: 7 = 0,7 m).
        weight: Peso em hectogramas (ex.: 69 = 6,9 kg).
        base_experience: Experiência base concedida ao derrotar este Pokémon.
            Padrão ``0`` quando ausente na resposta da API.
        abilities: Lista de habilidades do Pokémon, cada uma validada por
            ``PokemonAbilitySchema``.
        stats: Lista de estatísticas base, cada uma validada por
            ``PokemonStatsSchema``.
        types: Lista de tipos elementais, cada um validado por
            ``PokemonTypeSchema``.
    """

    pokemon_id: int = Field(alias='id')
    name: str
    height: int
    weight: int
    base_experience: int | None = 0
    abilities: list[PokemonAbilitySchema]
    stats: list[PokemonStatsSchema]
    types: list[PokemonTypeSchema]
