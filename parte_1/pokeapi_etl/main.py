from api.api_handler import busca_lista_pokemons, busca_pokemon
from storage.storage import OperadorArmazenamento


def pokedex():

    lista_pokemons = busca_lista_pokemons().json().get("results")

    for poke in lista_pokemons:
        pokemon_info = busca_pokemon(poke.get("url"))
        OperadorArmazenamento.registra_dados_brutos(pokemon_info)
        OperadorArmazenamento.registra_dados_bd(pokemon_info)


if __name__ == "__main__":
    pokedex()
