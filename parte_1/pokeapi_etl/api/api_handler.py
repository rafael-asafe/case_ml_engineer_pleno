import json

import httpx

from api.client import client
from utils.logger import logger


def trata_erro_http(func):
    def wrapper(*args, **kwargs):
        try:
            logger.debug(f"=== Iniciando {func.__name__}")
            response = func(*args, **kwargs)
            logger.debug(f"Status HTTP: {response.status_code}")
            response.raise_for_status()
            return response
        except httpx.HTTPStatusError as e:
            logger.error(f"✗ Erro HTTP {e.response.status_code}: {e} ")
            return False
        except httpx.RequestError as e:
            logger.error(f"✗ Erro de conexão: {e} ")
            return False
        except json.JSONDecodeError as e:
            logger.error(f"✗ Erro no formato JSON: {e} ")
            return False
        except IOError as e:
            logger.error(f"✗ Erro de I/O: {e} ")
            return False
        except Exception as e:
            logger.exception(f"✗ Erro inesperado: {e} ")
            return False

    return wrapper


@trata_erro_http
def busca_pokemon(pokemon_url, client=client):
    return client.get(pokemon_url)


@trata_erro_http
def busca_lista_pokemons(client=client):
    return client.get("/pokemon")
