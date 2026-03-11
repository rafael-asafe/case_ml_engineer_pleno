# Desenvolvimento do Micro Serviço de Model Serving

docker build . -t microservice_ner
docker run -d --name ner_instance -p 80:80 microservice_ner

acesse http://localhost/docs para documentação do serviço


# Como iniciar a aplicação

## Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/) instalado e em execução
- [Docker Compose](https://docs.docker.com/compose/) v2.20+ (suporte a `depends_on.condition`)

---

## 1. Clonar o repositório

```bash
git clone <url-do-repositorio>
cd parte_2
```

---

## 2. Configurar variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto. Exemplo mínimo:

```env
# Logging
LOG_LEVEL=INFO
CONSOLE_LOG=true

# Banco de dados (SQLite via volume Docker)
DATABASE_URL=sqlite+aiosqlite:////data/database.db

# spaCy
MAX_MODELS_IN_MEMORY=5
MODEL_PRELOAD=["pt_core_news_sm"]
MAX_TEXT_LENGTH=10000

# Health / Métricas
HEALTH_CHECK_INTERVAL=60
METRICS_RETENTION_DAYS=30
```

> **Atenção:** `DATABASE_URL` deve usar quatro barras (`////`) quando dentro do container para apontar ao volume `/data/database.db`.

---

## 3. Subir a aplicação

```bash
docker compose up --build
```

O compose executa dois serviços em ordem:

| Serviço   | O que faz                                              | Quando termina          |
|-----------|--------------------------------------------------------|-------------------------|
| `migrate` | Roda `alembic upgrade head` — cria/atualiza as tabelas | Ao concluir com sucesso |
| `app`     | Sobe o servidor FastAPI na porta `8000`                | Aguarda `migrate`       |

---

## 4. Verificar se a aplicação está saudável

```bash
curl http://localhost:8000/health
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

## 5. Registrar e usar um modelo spaCy

### 5.1 Registrar um modelo

```bash
curl -X POST http://localhost:8000/models/load \
  -H "Content-Type: application/json" \
  -d '{"model": "pt_core_news_sm"}'
```

> O modelo é baixado automaticamente se não estiver instalado.

### 5.2 Listar modelos registrados

```bash
curl http://localhost:8000/models/
```

### 5.3 Executar predição NER

```bash
curl -X POST http://localhost:8000/predict/ \
  -H "Content-Type: application/json" \
  -d '{"text": "Lula visitou São Paulo ontem.", "model": "pt_core_news_sm"}'
```

Resposta esperada:

```json
{
  "entities": {
    "PER": "Lula",
    "LOC": "São Paulo"
  }
}
```

---

## 6. Parar a aplicação

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
| `GET`    | `/health`             | Status da aplicação              |
| `POST`   | `/models/load`        | Registra e carrega um modelo     |
| `GET`    | `/models/`            | Lista modelos registrados        |
| `DELETE` | `/models/{version}`   | Remove um modelo pelo ID         |
| `POST`   | `/predict/`           | Executa inferência NER           |
| `GET`    | `/predict/list`       | Lista histórico de predições     |

Documentação interativa disponível em: `http://localhost:8000/docs`
