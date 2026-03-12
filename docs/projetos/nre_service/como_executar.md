# Configuração — Microserviço NER

Referência completa de todas as variáveis de ambiente suportadas pelo microserviço.

As variáveis são carregadas automaticamente de um arquivo `.env` na raiz de `parte_2/` via **Pydantic Settings**.

---

## Variáveis de ambiente

### Logging

| Variável      | Tipo    | Padrão  | Descrição                                      |
|---------------|---------|---------|------------------------------------------------|
| `LOG_LEVEL`   | string  | `INFO`  | Nível de log: `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `CONSOLE_LOG` | boolean | `true`  | Habilita saída de log no console               |
| `LOG_FILE`    | string  | —       | Caminho do arquivo de log (ex: `/data/logs/app.log`) |

> Se `LOG_FILE` não for definido, os logs são escritos apenas no console (quando `CONSOLE_LOG=true`).

---

### Banco de dados

| Variável       | Tipo   | Padrão | Descrição                             |
|----------------|--------|--------|---------------------------------------|
| `DATABASE_URL` | string | —      | URL de conexão SQLAlchemy (obrigatório) |

**Exemplos de URL:**

```env
# SQLite local (desenvolvimento)
DATABASE_URL=sqlite+aiosqlite:///database.db

# SQLite via volume Docker (produção no container)
DATABASE_URL=sqlite+aiosqlite:////data/database.db
```

> As quatro barras (`////`) são necessárias dentro do container para usar o caminho absoluto `/data/database.db`.

---

### Modelos spaCy

| Variável              | Tipo    | Padrão | Descrição                                                     |
|-----------------------|---------|--------|---------------------------------------------------------------|
| `MAX_MODELS_IN_MEMORY`| integer | `5`    | Limite de modelos carregados simultaneamente em memória       |
| `MODEL_PRELOAD`       | JSON    | `[]`   | Lista de modelos a serem carregados automaticamente no startup |
| `MAX_TEXT_LENGTH`     | integer | `10000`| Tamanho máximo do texto aceito em `/predict/` (em caracteres) |

**Exemplo de `MODEL_PRELOAD`:**

```env
# Um modelo
MODEL_PRELOAD=["pt_core_news_sm"]

# Múltiplos modelos
MODEL_PRELOAD=["pt_core_news_sm","en_core_web_sm"]

# Sem pré-carregamento
MODEL_PRELOAD=[]
```

> Modelos em `MODEL_PRELOAD` são baixados e carregados na inicialização. Falhas individuais são logadas sem interromper o startup.

---

### Health e métricas

| Variável                  | Tipo    | Padrão | Descrição                                           |
|---------------------------|---------|--------|-----------------------------------------------------|
| `HEALTH_CHECK_INTERVAL`   | integer | `60`   | Intervalo em segundos entre verificações de saúde   |
| `METRICS_RETENTION_DAYS`  | integer | `30`   | Dias de retenção dos logs de predição               |

---

## Arquivo `.env` completo

Exemplo de configuração para ambiente de produção com Docker:

```env
# Logging
LOG_LEVEL=INFO
CONSOLE_LOG=true
LOG_FILE=/data/logs/app.log

# Banco de dados
DATABASE_URL=sqlite+aiosqlite:////data/database.db

# Modelos spaCy
MAX_MODELS_IN_MEMORY=5
MODEL_PRELOAD=["pt_core_news_sm"]
MAX_TEXT_LENGTH=10000

# Health / Métricas
HEALTH_CHECK_INTERVAL=60
METRICS_RETENTION_DAYS=30
```

Exemplo de configuração para desenvolvimento local:

```env
# Logging
LOG_LEVEL=DEBUG
CONSOLE_LOG=true

# Banco de dados
DATABASE_URL=sqlite+aiosqlite:///database.db

# Modelos spaCy
MAX_MODELS_IN_MEMORY=3
MODEL_PRELOAD=[]
MAX_TEXT_LENGTH=10000

# Health / Métricas
HEALTH_CHECK_INTERVAL=60
METRICS_RETENTION_DAYS=30
```

---

## Configuração do Docker Compose

O `compose.yml` monta um volume compartilhado entre os serviços `migrate` e `app`:

```yaml
volumes:
  - ./data:/data
```

Isso garante que o banco de dados (`/data/database.db`) e os logs (`/data/logs/`) persistam entre reinicializações do container.

Para resetar o banco de dados e os logs:

```bash
docker compose down -v
rm -rf data/
```
