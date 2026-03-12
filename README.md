# Case ML Engineer Pleno

Case técnico composto por dois projetos independentes de engenharia de dados e machine learning.

## Projetos

| Projeto | Descrição | Tecnologias |
|---------|-----------|-------------|
| [Parte 1 — ETL PokeAPI](parte_1/) | Pipeline ETL que extrai dados de todos os pokémons da PokéAPI, persiste em SQLite e exporta em Parquet | httpx, SQLAlchemy, Polars, Alembic |
| [Parte 2 — Microserviço NER](parte_2/) | Microserviço REST para serving de modelos spaCy com inferência de Named Entity Recognition | FastAPI, spaCy, SQLAlchemy async, Alembic |

---

## Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/) e [Docker Compose](https://docs.docker.com/compose/) v2.20+
- [Python 3.13+](https://www.python.org/downloads/) (para desenvolvimento local)
- [Poetry](https://python-poetry.org/docs/) (gerenciador de dependências)

### Instalar Python e Poetry

```bash
# Fedora/RHEL
sudo dnf install python3.14 python3.13

# Poetry via pipx
pip install pipx
pipx install poetry
```

---

## Parte 1 — ETL PokeAPI

Pipeline que extrai, transforma e carrega dados de pokémons em banco de dados e arquivos Parquet.

### Arquitetura

```
pokeapi_etl/
├── api/          # Client HTTP com cache, retry e paginação
├── database/     # ORM SQLAlchemy, modelos e schemas Pydantic
├── storage/      # Persistência em disco (SOR/SOT)
└── utils/        # Logger e configurações
```

**Fluxo de dados:**
1. Busca lista paginada de pokémons na PokéAPI
2. Extrai detalhes de cada pokémon (abilities, stats, types)
3. Salva dados brutos em JSONL → `data/SOR/`
4. Persiste no banco SQLite
5. Exporta 4 tabelas em Parquet → `data/SOT/`

### Como executar

O passo a passo de como executar a aplicação pode ser acessado pelo servidor mkdocs ou no caminho direto:

`docs/projetos/analise_dado_pokeapi/como_executar.md`

> Obs: o teste orienta a criação de um repo, tive a decisão de criar o pyproject.toml apenas nas páginas de cada projeto.

```bash
cd parte_1
poetry --directory=./parte_1 install
source $(poetry --directory=./parte_1 env info -p)/bin/activate
mkdocs run
```

Endereço de acesso a doc: `http://localhost:8000/docs`

### Testes

```bash
cd parte_1
poetry run task test
```

---

## Parte 2 — Microserviço NER

API REST para registro, gerenciamento e inferência de modelos spaCy de Named Entity Recognition.

### Arquitetura

```
microservice_nre/
├── routers/      # Endpoints: /health, /models, /predict
├── services/     # SpacyService (cache em memória), ModelRegistry, ModelDownloader
├── database/     # ORM async SQLAlchemy, modelos e schemas
└── utils/        # Logger, settings e error handler
```

### Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/health` | Status e métricas da aplicação |
| `POST` | `/models/load` | Registra e carrega um modelo spaCy |
| `GET` | `/models/` | Lista modelos registrados |
| `DELETE` | `/models/{version}` | Remove modelo pelo ID |
| `POST` | `/predict/` | Executa inferência NER |
| `GET` | `/predict/list` | Histórico de predições |

### Como executar

O passo a passo de como executar a aplicação pode ser acessado pelo servidor mkdocs ou no caminho direto:

`docs/projetos/nre_service/como_executar.md`

```bash
cd parte_1
poetry --directory=./parte_2 install
source $(poetry --directory=./parte_2 env info -p)/bin/activate
mkdocs run
```
> Obs: os dois projetos compartilham a mesma doc.

Endereço de acesso a doc: `http://localhost:8000`

Endereço de acesso a doc da api: `http://localhost:8001/docs`

### Testes

```bash
cd parte_2
poetry run task test
```
---

## Estrutura do Repositório

```
case_ml_engineer_pleno/
├── parte_1/                 # ETL PokeAPI
│   ├── pokeapi_etl/         # Código principal
│   ├── tests/               # Testes unitários
│   ├── migrations/          # Migrações Alembic
│   ├── Dockerfile
│   ├── compose.yml
│   └── pyproject.toml
├── parte_2/                 # Microserviço NER
│   ├── microservice_nre/    # Código principal
│   ├── tests/               # Testes unitários (9 arquivos)
│   ├── migrations/          # Migrações Alembic
│   ├── dockerfile
│   ├── compose.yml
│   └── pyproject.toml
└── docs/                    # Documentação MkDocs
```
