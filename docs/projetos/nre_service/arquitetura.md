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

## Componentes principais

### SpacyService

Gerencia o ciclo de vida dos modelos spaCy em memória. Funciona como um cache com limite configurável (`MAX_MODELS_IN_MEMORY`).

| Método | Descrição |
|--------|-----------|
| `add_model(name)` | Carrega um modelo spaCy no dicionário interno |
| `remove_model(name)` | Remove um modelo da memória |
| `process_text(text, model)` | Executa NER em thread pool (não bloqueia o event loop) |
| `clear()` | Remove todos os modelos (chamado no shutdown) |

A inferência é executada via `asyncio.get_event_loop().run_in_executor()` para não bloquear o event loop com a computação síncrona do spaCy.

**Entidades extraídas:**

| Label spaCy | Campo na resposta |
|-------------|-------------------|
| `MONEY`     | `money`           |
| `PER`       | `person`          |
| `DATE`      | `date`            |

### ModelRegistry

Repositório para persistência dos modelos registrados no banco de dados. Desencadeia o download do modelo ao registrar.

| Método | Descrição |
|--------|-----------|
| `register(model_name)` | Cria entrada no banco + dispara download |
| `list()` | Retorna todos os modelos cadastrados |
| `get_by_version(version)` | Busca pelo ID (PK auto-increment) |
| `get_by_name(name)` | Busca pelo nome do pacote spaCy |
| `delete(version)` | Remove pelo ID, lança `KeyError` se não existir |

Lança `HTTPException 409` se o modelo já estiver registrado.

### ModelDownloader

Wrapper assíncrono em torno de `python -m spacy download <model>`. Usa `asyncio.create_subprocess_exec` para não bloquear durante o download.

```python
# Comportamento interno
process = await asyncio.create_subprocess_exec(
    "python", "-m", "spacy", "download", model_name
)
await process.communicate()
# Lança RuntimeError se returncode != 0
```

---

## Ciclo de vida da aplicação (lifespan)

```
Startup
  └── Lê MODEL_PRELOAD (settings) + modelos registrados no banco
      └── Para cada modelo:
          ├── Executa download se necessário
          ├── Carrega via SpacyService.add_model()
          └── Falhas individuais são logadas sem interromper o startup

Shutdown
  └── SpacyService.clear() — libera memória de todos os modelos
```

---

## Middleware

Cada requisição passa por `request_middleware` antes de chegar aos routers:

```
Request →  gera X-Request-ID (UUID4)
        →  inicia timer
        →  processa request
        →  calcula X-Process-Time-MS
        →  adiciona headers à response
Response →  X-Request-ID: <uuid>
         →  X-Process-Time-MS: <ms>
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
