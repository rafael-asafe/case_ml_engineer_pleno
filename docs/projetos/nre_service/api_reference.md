# Referência da API — Microserviço NER

Documentação completa de todos os endpoints, schemas de entrada e saída, e códigos de resposta.

> Documentação interativa (Swagger UI) disponível em `http://localhost:8001/docs` com a aplicação em execução.

---

## Health

### `GET /health`

Retorna o status atual da aplicação e métricas operacionais.

**Resposta — `200 OK`**

```json
{
  "status": "healthy",
  "timestamp": "2026-03-12T10:00:00.000000",
  "uptime_seconds": 42.5,
  "requests_total": 15,
  "models_in_memory": 2
}
```

**Resposta — `503 Service Unavailable`**

Retornado quando o `SpacyService` ainda não foi inicializado.

```json
{
  "detail": "Service not available"
}
```

| Campo            | Tipo    | Descrição                              |
|------------------|---------|----------------------------------------|
| `status`         | string  | `"healthy"` quando operacional         |
| `timestamp`      | string  | ISO 8601 com data e hora atual         |
| `uptime_seconds` | float   | Segundos desde a inicialização         |
| `requests_total` | integer | Total de predições realizadas          |
| `models_in_memory` | integer | Modelos carregados no cache atual    |

---

## Modelos

### `POST /models/load`

Registra um modelo spaCy no banco de dados, realiza o download caso não esteja instalado e carrega em memória.

**Request body**

```json
{
  "model": "pt_core_news_sm"
}
```

| Campo   | Tipo   | Obrigatório | Descrição              |
|---------|--------|-------------|------------------------|
| `model` | string | sim         | Nome do pacote spaCy   |

**Resposta — `201 Created`**

```json
{
  "model_version": 1,
  "model": "pt_core_news_sm"
}
```

**Resposta — `409 Conflict`**

Retornado quando o modelo já está registrado.

```json
{
  "detail": "Model already registered"
}
```

**Resposta — `422 Unprocessable Entity`**

Retornado quando o download do modelo falha.

```json
{
  "detail": "Failed to download model: pt_core_news_sm"
}
```

---

### `GET /models/`

Lista todos os modelos registrados no banco de dados.

**Resposta — `200 OK`**

```json
[
  {
    "model_version": 1,
    "model": "pt_core_news_sm"
  },
  {
    "model_version": 2,
    "model": "en_core_web_sm"
  }
]
```

Retorna lista vazia `[]` se nenhum modelo estiver registrado.

---

### `DELETE /models/{model_version}`

Remove um modelo pelo seu ID de versão. Remove do banco de dados e da memória.

**Parâmetro de path**

| Parâmetro       | Tipo    | Descrição                     |
|-----------------|---------|-------------------------------|
| `model_version` | integer | ID da versão do modelo (PK)   |

**Resposta — `204 No Content`**

Sem corpo na resposta. Remoção bem-sucedida.

**Resposta — `404 Not Found`**

```json
{
  "detail": "Model version not found"
}
```

---

## Predição

### `POST /predict/`

Executa inferência de Named Entity Recognition (NER) em um texto usando o modelo especificado.

**Request body**

```json
{
  "text": "Lula visitou São Paulo e gastou R$ 500 ontem.",
  "model": "pt_core_news_sm"
}
```

| Campo   | Tipo   | Obrigatório | Restrição              | Descrição                      |
|---------|--------|-------------|------------------------|--------------------------------|
| `text`  | string | sim         | max `MAX_TEXT_LENGTH`  | Texto a ser analisado          |
| `model` | string | sim         | —                      | Nome do modelo spaCy a usar    |

**Resposta — `200 OK`**

```json
{
  "money": "R$ 500",
  "person": "Lula",
  "date": "ontem"
}
```

| Campo    | Tipo          | Label spaCy | Descrição                    |
|----------|---------------|-------------|------------------------------|
| `money`  | string \| null | `MONEY`    | Valores monetários           |
| `person` | string \| null | `PER`      | Nomes de pessoas             |
| `date`   | string \| null | `DATE`     | Expressões de data/hora      |

> Campos não encontrados no texto retornam `null`.

**Resposta — `422 Unprocessable Entity`**

Retornado quando o modelo não está carregado em memória ou o texto excede o limite.

```json
{
  "detail": "Model not loaded: pt_core_news_sm"
}
```

---

### `GET /predict/list`

Lista o histórico completo de predições realizadas.

**Resposta — `200 OK`**

```json
[
  {
    "log_id": 1,
    "input": {
      "text": "Lula visitou São Paulo ontem.",
      "model": "pt_core_news_sm"
    },
    "output": {
      "person": "Lula",
      "money": null,
      "date": "ontem"
    },
    "timestamp": "2026-03-12T10:05:30.123456",
    "model_version": 1
  }
]
```

| Campo           | Tipo          | Descrição                              |
|-----------------|---------------|----------------------------------------|
| `log_id`        | integer       | ID único do log                        |
| `input`         | object        | Dados da requisição original           |
| `output`        | object        | Entidades extraídas                    |
| `timestamp`     | string        | ISO 8601 da data/hora da predição      |
| `model_version` | integer \| null | ID do modelo usado (se registrado)   |

---

## Headers de rastreabilidade

Toda resposta inclui os seguintes headers injetados pelo middleware:

| Header               | Exemplo                                | Descrição                      |
|----------------------|----------------------------------------|--------------------------------|
| `X-Request-ID`       | `a3f2c1d4-...`                         | UUID único por requisição      |
| `X-Process-Time-MS`  | `12.47`                                | Tempo de processamento em ms   |

---

## Modelos spaCy disponíveis

Qualquer modelo da biblioteca spaCy pode ser registrado. Exemplos comuns:

| Modelo             | Idioma     | Tamanho |
|--------------------|------------|---------|
| `pt_core_news_sm`  | Português  | small   |
| `pt_core_news_md`  | Português  | medium  |
| `pt_core_news_lg`  | Português  | large   |
| `en_core_web_sm`   | Inglês     | small   |
| `en_core_web_md`   | Inglês     | medium  |

> Lista completa em [spacy.io/models](https://spacy.io/models).
