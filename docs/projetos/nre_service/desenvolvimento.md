# Desenvolvimento — Microserviço NER

Guia para configurar o ambiente local, executar testes e contribuir com o projeto.

---

## Configurar o ambiente local

### Pré-requisitos

- Python 3.13+
- [Poetry](https://python-poetry.org/docs/)

### Instalar dependências

```bash
cd parte_2
poetry install
source $(poetry env info -p)/bin/activate
```

### Configurar `.env` local

```env
LOG_LEVEL=DEBUG
CONSOLE_LOG=true
DATABASE_URL=sqlite+aiosqlite:///database.db
MAX_MODELS_IN_MEMORY=3
MODEL_PRELOAD=[]
MAX_TEXT_LENGTH=10000
HEALTH_CHECK_INTERVAL=60
METRICS_RETENTION_DAYS=30
```

### Criar e migrar o banco

```bash
alembic upgrade head
```

### Iniciar o servidor

```bash
poetry run task run
# ou diretamente:
fastapi dev microservice_nre/main.py
```

Acesse `http://localhost:8000/docs` para a interface interativa.

---

## Testes

### Executar todos os testes

```bash
poetry run task test
```

### Executar com cobertura

```bash
pytest --cov=microservice_nre --cov-report=term-missing
```

### Executar um arquivo específico

```bash
pytest tests/test_predict_router.py -v
```

---

## Suite de testes

| Arquivo                      | Cobertura                                              |
|------------------------------|--------------------------------------------------------|
| `test_health_router.py`      | Endpoint `/health`, status 200 e 503                  |
| `test_model_router.py`       | Endpoints `/models/` — load, list, delete             |
| `test_predict_router.py`     | Endpoints `/predict/` — inferência e histórico        |
| `test_spacy_service.py`      | SpacyService — cache, inferência, contadores          |
| `test_model_registry.py`     | ModelRegistry — CRUD, conflitos, not found            |
| `test_model_downloader.py`   | ModelDownloader — subprocess async                    |
| `test_middleware.py`         | Headers `X-Request-ID` e `X-Process-Time-MS`          |
| `test_db.py`                 | Sessão e engine do banco de dados                     |
| `test_main.py`               | Inicialização da aplicação                            |

### Fixtures de teste (`conftest.py`)

Os testes usam um banco **SQLite em memória** para isolamento total:

```python
# Banco em memória — sem efeito colateral entre testes
engine = create_async_engine("sqlite+aiosqlite:///:memory:")

# Override da sessão do FastAPI
app.dependency_overrides[get_session] = override_get_session
```

O `SpacyService` é mockado nos testes de rota para evitar o carregamento real de modelos spaCy.

---

## Linting e formatação

```bash
# Verificar estilo
poetry run task lint

# Ordenar imports
isort microservice_nre/ tests/

# Aplicar correções automáticas
ruff check --fix microservice_nre/
```

---

## Migrações de banco de dados

### Criar nova migração

```bash
alembic revision --autogenerate -m "descrição da mudança"
```

### Aplicar migrações

```bash
alembic upgrade head
```

### Reverter última migração

```bash
alembic downgrade -1
```

### Ver histórico de migrações

```bash
alembic history
```

---

## Adicionar um novo endpoint

1. Crie ou edite o router em `microservice_nre/routers/`
2. Adicione os schemas em `microservice_nre/database/schemas.py`
3. Registre o router em `microservice_nre/main.py` (se for novo arquivo)
4. Aplique `@handle_http_errors` nos handlers para mapeamento automático de exceções
5. Adicione testes em `tests/`

**Exemplo mínimo de router:**

```python
from fastapi import APIRouter
from microservice_nre.utils.error_handler import handle_http_errors

router = APIRouter(prefix="/exemplo", tags=["exemplo"])

@router.get("/")
@handle_http_errors
async def listar():
    return []
```

---

## Adicionar suporte a um novo modelo spaCy

Qualquer modelo publicado no hub do spaCy pode ser registrado via API:

```bash
# Registrar via endpoint
curl -X POST http://localhost:8000/models/load \
  -H "Content-Type: application/json" \
  -d '{"model": "en_core_web_sm"}'
```

O download é realizado automaticamente. Modelos disponíveis em [spacy.io/models](https://spacy.io/models).

Para novos tipos de entidade, adicione o mapeamento em `SpacyService.process_text()`:

```python
label_map = {
    "MONEY": "money",
    "PER": "person",
    "DATE": "date",
    # Adicione novos labels aqui
    "ORG": "organization",
}
```
