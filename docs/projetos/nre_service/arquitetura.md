# Arquitetura — Microserviço NER

Visão técnica da estrutura, componentes e decisões de design do microserviço de Named Entity Recognition.

---

## Estrutura do projeto

```
parte_2/
├── microservice_nre/
│   ├── main.py              # Aplicação FastAPI — routers e middleware
│   ├── lifespan.py          # Ciclo de vida: startup e shutdown
│   ├── middleware.py        # Rastreamento de requests (ID e latência)
│   ├── routers/
│   │   ├── health.py        # GET /health
│   │   ├── model.py         # POST /models/load, GET /models/, DELETE /models/{version}
│   │   └── predict.py       # POST /predict/, GET /predict/list
│   ├── services/
│   │   ├── spacy_service.py     # Cache em memória de modelos spaCy
│   │   ├── model_registry.py    # Persistência de modelos no banco de dados
│   │   └── model_downloader.py  # Download assíncrono via subprocess
│   ├── database/
│   │   ├── database.py      # Engine e sessão SQLAlchemy async
│   │   ├── models.py        # ORM: MLModel, PredictLogs
│   │   └── schemas.py       # Schemas Pydantic de request/response
│   └── utils/
│       ├── logger.py        # Logger com execution_id único por processo
│       ├── settings.py      # Variáveis de ambiente via Pydantic Settings
│       └── error_handler.py # Decorator de mapeamento de exceções para HTTP
├── migrations/              # Migrações Alembic
├── tests/                   # Suite de testes (9 arquivos)
├── dockerfile
└── compose.yml
```

---

## Banco de dados

SQLite com SQLAlchemy assíncrono (`aiosqlite`). A sessão é injetada via dependency injection do FastAPI.

### Modelos ORM

**`MLModel`** — tabela `models`

| Coluna          | Tipo    | Descrição                        |
|-----------------|---------|----------------------------------|
| `model_version` | Integer | PK auto-increment                |
| `model`         | String  | Nome do pacote spaCy (único)     |

**`PredictLogs`** — tabela `predict_logs`

| Coluna          | Tipo     | Descrição                              |
|-----------------|----------|----------------------------------------|
| `log_id`        | Integer  | PK auto-increment                      |
| `input`         | JSON     | Texto e modelo da requisição           |
| `output`        | JSON     | Entidades extraídas                    |
| `timestamp`     | DateTime | Data/hora da predição (auto)           |
| `model_version` | Integer  | FK → `MLModel.model_version` (nullable)|

---

## Tratamento de erros

O decorator `@handle_http_errors` é aplicado nos handlers de rota e mapeia exceções Python para respostas HTTP:

| Exceção Python    | Status HTTP                  |
|-------------------|------------------------------|
| `KeyError`        | `404 Not Found`              |
| `OSError`         | `422 Unprocessable Entity`   |
| `RuntimeError`    | `422 Unprocessable Entity`   |
| `HTTPException`   | Repassa sem alteração        |

---

## Fluxo de uma predição

```
POST /predict/
  │
  ├── Valida PredictRequest (text, model) via Pydantic
  ├── SpacyService.process_text(text, model)
  │     └── nlp(text) em thread pool → extrai entidades
  ├── ModelRegistry.get_by_name(model) → busca model_version
  ├── Persiste PredictLogs no banco (input, output, model_version)
  └── Retorna PredictResponse {money, person, date}
```

---

## Stack tecnológica

| Camada       | Tecnologia                              |
|--------------|-----------------------------------------|
| Framework    | FastAPI                                 |
| NLP          | spaCy                                   |
| ORM          | SQLAlchemy (async)                      |
| Driver DB    | aiosqlite                               |
| Migrations   | Alembic                                 |
| Validação    | Pydantic v2                             |
| Config       | Pydantic Settings                       |
| Testes       | pytest + pytest-asyncio                 |
| Lint         | Ruff + isort                            |
| Container    | Docker (multi-stage) + Docker Compose   |
