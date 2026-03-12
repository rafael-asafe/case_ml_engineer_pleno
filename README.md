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

### Executar com Docker

```bash
cd parte_1

# 1. Criar arquivo .env
cat > .env << 'EOF'
LOG_LEVEL=DEBUG
CONSOLE_LOG=TRUE
DATABASE_URL=sqlite:///database.db
NOME_PASTA_SOR=SOR/pokemons/today_date/
NOME_ARQUIVO_SOR=pokemons.jsonl
NOME_PASTA_SOT=SOT/
CAMINHO_DADOS=./data/
LIMIT_OFFSET=20
RETRY=5
BACKOFF_FACTOR=0.5
CLIENT_MAX_CONNECTIONS=50
MAX_KEEPALIVE_CONNECTIONS=20
KEEPALIVE_EXPIRY=10
POKEAPI_BASE_URL=https://pokeapi.co/api/v2/
EOF

# 2. Criar estrutura de dados
mkdir -p data
touch database.db

# 3. Executar
docker compose up
```

**Saída esperada:**

```
data/
├── SOR/pokemons/<ano>/<mes>/<dia>/pokemons.jsonl   # dados brutos
└── SOT/
    ├── pokemon/<ano>/<mes>/<dia>/pokemon.parquet
    ├── pokemon_ability/<ano>/<mes>/<dia>/pokemon_ability.parquet
    ├── pokemon_stats/<ano>/<mes>/<dia>/pokemon_stats.parquet
    └── pokemon_type/<ano>/<mes>/<dia>/pokemon_type.parquet
database.db                                          # banco SQLite
```

### Executar localmente

```bash
cd parte_1
poetry install
source $(poetry env info -p)/bin/activate
poetry run task run
```

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

**Componentes principais:**
- **SpacyService**: gerencia modelos spaCy em memória (cache com limite configurável)
- **ModelRegistry**: persiste registro de modelos no banco de dados
- **Middleware**: injeta `X-Request-ID` e `X-Process-Time-MS` em cada request

### Endpoints

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/health` | Status e métricas da aplicação |
| `POST` | `/models/load` | Registra e carrega um modelo spaCy |
| `GET` | `/models/` | Lista modelos registrados |
| `DELETE` | `/models/{version}` | Remove modelo pelo ID |
| `POST` | `/predict/` | Executa inferência NER |
| `GET` | `/predict/list` | Histórico de predições |

### Executar com Docker

```bash
cd parte_2

# 1. Criar arquivo .env
cat > .env << 'EOF'
LOG_LEVEL=INFO
CONSOLE_LOG=true
LOG_FILE=/data/logs/app.log
DATABASE_URL=sqlite+aiosqlite:////data/database.db
MAX_MODELS_IN_MEMORY=5
MODEL_PRELOAD=["pt_core_news_sm"]
MAX_TEXT_LENGTH=10000
HEALTH_CHECK_INTERVAL=60
METRICS_RETENTION_DAYS=30
EOF

# 2. Subir (migrate roda antes do app automaticamente)
docker compose up --build
```

O compose executa dois serviços em sequência:

| Serviço | O que faz |
|---------|-----------|
| `migrate` | Roda `alembic upgrade head` — cria/atualiza as tabelas |
| `app` | Sobe o FastAPI na porta `8000` (aguarda `migrate` concluir) |

### Uso da API

```bash
# Health check
curl http://localhost:8000/health

# Registrar modelo
curl -X POST http://localhost:8000/models/load \
  -H "Content-Type: application/json" \
  -d '{"model": "pt_core_news_sm"}'

# Inferência NER
curl -X POST http://localhost:8000/predict/ \
  -H "Content-Type: application/json" \
  -d '{"text": "John Smith transferred $5,000 to Goldman Sachs in New York last Monday.", "model": "en_core_web_sm"}'
```

**Resposta da predição:**
```json
{
  "entities": {
    "PER": "Lula",
    "LOC": "São Paulo"
  }
}
```

Documentação interativa: `http://localhost:8000/docs`

### Executar localmente

```bash
cd parte_2
poetry install
source $(poetry env info -p)/bin/activate
poetry run task run
```

### Testes

```bash
cd parte_2
poetry run task test
```

---

## Documentação

Para visualizar a documentação completa com MkDocs:

```bash
# Instalar MkDocs (a partir do ambiente virtual de qualquer projeto)
cd parte_1
source $(poetry env info -p)/bin/activate

# Voltar à raiz e iniciar
cd ..
mkdocs serve
```

Acesse em `http://localhost:8000`.

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
