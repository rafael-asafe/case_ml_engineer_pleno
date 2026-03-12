# Documentação Técnica — ETL PokeAPI

Detalhamento da arquitetura e das decisões de implementação do pipeline ETL da Parte 1.

---

## Arquitetura

```
pokeapi_etl/
├── api/
│   ├── client.py        # AsyncClient com cache (hishel), retry e connection pool
│   └── api_handler.py   # Funções de busca: lista paginada e detalhes por pokémon
├── database/
│   ├── models.py        # Modelos ORM (SQLAlchemy)
│   ├── schemas.py       # Schemas de validação (Pydantic)
│   └── database.py      # Engine, sessão e exportação para Parquet
├── storage/
│   └── storage.py       # Persistência em disco (SOR e SOT)
└── utils/
    ├── logger.py        # Logger com execution ID
    └── settings.py      # Variáveis de ambiente via Pydantic Settings
```

---

## Modelos de dados

### `Pokemon`

| Coluna           | Tipo    | Descrição                     |
|------------------|---------|-------------------------------|
| `pokemon_id`     | Integer | Chave primária                |
| `name`           | String  | Nome do pokémon               |
| `height`         | Integer | Altura (em decímetros)        |
| `weight`         | Integer | Peso (em hectogramas)         |
| `base_experience`| Integer | Experiência base (default: 0) |

### `PokemonAbility`

| Coluna         | Tipo    | Descrição                        |
|----------------|---------|----------------------------------|
| `ability_name` | String  | Chave primária                   |
| `is_hidden`    | Boolean | Indica se é habilidade oculta    |
| `pokemon_id`   | Integer | FK → `Pokemon.pokemon_id`        |

### `PokemonStats`

| Coluna      | Tipo    | Descrição                 |
|-------------|---------|---------------------------|
| `stat_name` | String  | Chave primária            |
| `base_stat` | Integer | Valor base da estatística |
| `pokemon_id`| Integer | FK → `Pokemon.pokemon_id` |

### `PokemonType`

| Coluna      | Tipo    | Descrição                 |
|-------------|---------|---------------------------|
| `type_name` | String  | Chave primária            |
| `pokemon_id`| Integer | FK → `Pokemon.pokemon_id` |

---

## Decisões de implementação

### Cache HTTP com hishel

O cliente HTTP utiliza [hishel](https://hishel.com/) para cache de respostas, evitando requisições repetidas à PokéAPI em execuções sucessivas. O cache respeita os headers HTTP padrão (`Cache-Control`, `ETag`).

### Retry automático com httpx-retries

Configurado com `RETRY=5` e `BACKOFF_FACTOR=0.5` para tolerar instabilidades temporárias da API sem falhar o pipeline.

### Camadas de dados: SOR e SOT

- **SOR (Source of Record):** dados brutos em JSONL, sem transformação — rastreabilidade total
- **SOT (Source of Truth):** dados transformados e validados em Parquet — prontos para análise

### Particionamento por data

Ambas as camadas organizam os arquivos por `<ano>/<mes>/<dia>/`, permitindo reprocessamento incremental e consultas particionadas.
