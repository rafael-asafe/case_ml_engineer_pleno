# Case ML Engineer Pleno

Case técnico composto por dois projetos independentes de engenharia de dados e machine learning.

---

## Projetos

### [Parte 1 — ETL PokeAPI](projetos/analise_dados_pokeapi/como_executar.md)

Pipeline ETL que extrai dados de todos os pokémons da [PokeAPI](https://pokeapi.co/), persiste em banco SQLite e exporta em formato Parquet.

**Tecnologias:** Python 3.14 · httpx · hishel · SQLAlchemy · Polars · Alembic · Docker

**Fluxo:**

1.  Extrai lista paginada de pokémons via API
2.  Busca detalhes de cada pokémon (abilities, stats, types)
3.  Salva dados brutos em JSONL (`SOR/`)
4.  Persiste no banco SQLite
5.  Exporta 4 tabelas em Parquet (`SOT/`)
6.  Notebook Spark faz a analise das tabelas.

---

### [Parte 2 — Microserviço NER](projetos/nre_service/como_executar.md)

Microserviço REST para registro, gerenciamento e inferência de modelos spaCy com Named Entity Recognition.

**Tecnologias:** Python 3.13 · FastAPI · spaCy · SQLAlchemy async · aiosqlite · Alembic · Docker

**Funcionalidades:**

-   Registro e download automático de modelos spaCy
-   Cache de modelos em memória com limite configurável
-   Inferência NER com extração de entidades (pessoa, local, data, etc.)
-   Histórico de predições persistido no banco de dados
-   Rastreamento de requests por middleware (`X-Request-ID`, latência)

