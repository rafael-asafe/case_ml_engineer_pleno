# Análise de Dados com PokeAPI

## instalar python e poetry 

```bash
sudo dnf install python3.14

pip install pipx

pipx install poetry 
```

## instalar projeto  

```bash
cd parte_1

source $(poetry env info -p)/bin/activate

poetry install 
``` 

## iniciar a aplicação 
poetry run alembic revision --autogenerate -m "create pokemon tables"

poetry run alembic upgrade head

poetry run python pokeapi_etl/main.py

## iniciar notebook analise 

- adicione as tabelas ao seu ambiente

- criei a tabela usando o UI do databricks

- importe as tabelas no notebook


## Modelagem de dados

Sugestão: padronizar o nome dos campos 

pokemon_id:
pokemon_name:

etc