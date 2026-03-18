import pytest
from httpx import Response
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from database.models import table_registry
from database.schemas import PokemonSchema
from factories import PokemonSchemaFactory


@pytest.fixture()
def make_response():
    """Fixture que retorna uma factory de ``httpx.Response`` a partir de um PokemonSchema.

    Reconstrói o payload no formato original da PokéAPI (com aliases como ``'id'`` e
    dicionários aninhados para ``ability``, ``stat`` e ``type``) para que
    ``PokemonSchema(**retorno.json())`` consiga re-parsear corretamente.
    """

    def _factory(pokemon: PokemonSchema = None) -> Response:
        """Cria um ``httpx.Response`` a partir de um ``PokemonSchema`` validado.

        Args:
            pokemon: Instância de ``PokemonSchema`` cujos dados serão usados para
                montar o payload no formato original da API. Se não fornecido,
                uma instância é gerada automaticamente via ``PokemonSchemaFactory``.
        """
        if pokemon is None:
            pokemon = PokemonSchemaFactory.build()

        payload = {
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
        return Response(200, json=payload)

    return _factory


# --- registra_dados_bd ---


@pytest.fixture()
def cria_tabelas():
    """Cria e derruba todas as tabelas no banco em memória para cada teste."""
    from database.database import engine

    table_registry.metadata.create_all(engine)
    yield
    table_registry.metadata.drop_all(engine)
