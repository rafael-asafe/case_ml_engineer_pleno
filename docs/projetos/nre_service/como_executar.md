# Microserviço de Model Serving (NER)

API REST para registro, gerenciamento e inferência de modelos spaCy com Named Entity Recognition.

---

## Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/) instalado e em execução
- [Docker Compose](https://docs.docker.com/compose/) v2.20+ (suporte a `depends_on.condition`)

---

## Como iniciar a aplicação

Após as etapas descritas no README.md

### 1. Acesse o diretório

```bash
cd parte_2
```

### 2. Configurar variáveis de ambiente

Crie um arquivo `.env` na raiz de `parte_2/`:

```env
# Logging
LOG_LEVEL=INFO
CONSOLE_LOG=true
LOG_FILE=/data/logs/app.log

# Banco de dados (SQLite via volume Docker)
DATABASE_URL=sqlite+aiosqlite:////data/database.db

# spaCy
MAX_MODELS_IN_MEMORY=5
MODEL_PRELOAD=["en_core_web_sm"]
MAX_TEXT_LENGTH=10000

# Health / Métricas
HEALTH_CHECK_INTERVAL=60
METRICS_RETENTION_DAYS=30
```

> **Atenção:** `DATABASE_URL` deve usar quatro barras (`////`) quando dentro do container para apontar ao volume `/data/database.db`.

### 3. Subir a aplicação

```bash
docker compose up
# ou 
docker compose --verbose up
```

Na primeira execução a imagem será buildada automaticamente. Nas seguintes, use `--build` apenas se o código ou dependências mudarem:

```bash
docker compose up --build
```


O compose executa dois serviços em ordem:

| Serviço   | O que faz                                              | Quando termina          |
|-----------|--------------------------------------------------------|-------------------------|
| `migrate` | Roda `alembic upgrade head` — cria/atualiza as tabelas | Ao concluir com sucesso |
| `app`     | Sobe o servidor FastAPI na porta `8001`                | Aguarda `migrate`       |

---

## Verificar se a aplicação está saudável

```bash
curl http://localhost:8001/health
```

Resposta esperada:

```json
{
  "status": "healthy",
  "timestamp": "2026-03-11T22:08:58.860939",
  "uptime_seconds": 3.87,
  "requests_total": 0,
  "models_in_memory": 0
}
```

---

## Usar a API

### Registrar um modelo

```bash
curl -X POST http://localhost:8001/models/load \
  -H "Content-Type: application/json" \
  -d '{"model": "pt_core_news_sm"}'
```

> O modelo é baixado automaticamente via `python -m spacy download` se não estiver instalado.

### Listar modelos registrados

```bash
curl http://localhost:8001/models/
```

### Executar predição NER

```bash
curl -X POST http://localhost:8001/predict/ \
  -H "Content-Type: application/json" \
  -d '{"text": "Can you send $45 to Michael on June 3?", "model": "en_core_web_sm"}'
```

Resposta esperada:

```json
{ 
  "money":"45",
  "person":"Michael",
  "date":"June 3"
}
```

### Listar histórico de predições

```bash
curl http://localhost:8001/predict/list
```

### Remover um modelo

```bash
curl -X DELETE http://localhost:8001/models/{version}
```

---

## Parar a aplicação

```bash
docker compose down
```

Para remover também os volumes (banco de dados e logs):

```bash
docker compose down -v
```

---

## Referência dos endpoints

| Método   | Endpoint              | Descrição                        |
|----------|-----------------------|----------------------------------|
| `GET`    | `/health`             | Status e métricas da aplicação   |
| `POST`   | `/models/load`        | Registra e carrega um modelo     |
| `GET`    | `/models/`            | Lista modelos registrados        |
| `DELETE` | `/models/{version}`   | Remove um modelo pelo ID         |
| `POST`   | `/predict/`           | Executa inferência NER           |
| `GET`    | `/predict/list`       | Lista histórico de predições     |

Documentação interativa disponível em: `http://localhost:8001/docs`
