# Case ML Engineer Pleno

Case técnico composto por dois projetos independentes de engenharia de dados e machine learning.

---

## Projetos

### [Parte 1 — ETL PokeAPI](projetos/analise_dado_pokeapi/analise_dados_pokeapi.md)

Pipeline ETL que extrai dados de todos os pokémons da [PokéAPI](https://pokeapi.co/), persiste em banco SQLite e exporta em formato Parquet.

**Tecnologias:** Python 3.14 · httpx · hishel · SQLAlchemy · Polars · Alembic · Docker

**Fluxo:**
1. Extrai lista paginada de pokémons via API
2. Busca detalhes de cada pokémon (abilities, stats, types)
3. Salva dados brutos em JSONL (`SOR/`)
4. Persiste no banco SQLite
5. Exporta 4 tabelas em Parquet (`SOT/`)

---

### [Parte 2 — Microserviço NER](projetos/micro_servico_model_serving.md)

Microserviço REST para registro, gerenciamento e inferência de modelos spaCy com Named Entity Recognition.

**Tecnologias:** Python 3.13 · FastAPI · spaCy · SQLAlchemy async · aiosqlite · Alembic · Docker

**Funcionalidades:**
- Registro e download automático de modelos spaCy
- Cache de modelos em memória com limite configurável
- Inferência NER com extração de entidades (pessoa, local, data, etc.)
- Histórico de predições persistido no banco de dados
- Rastreamento de requests por middleware (`X-Request-ID`, latência)

---

## Uso de IA no Desenvolvimento

Foi utilizado o assistente **Claude Code** para apoio em revisão de código e criação de testes unitários.

Contribuições:

- **Testes — Parte 1**: criação de `test_schemas.py` (10 testes) e `test_storage.py` (5 testes) cobrindo schemas Pydantic e operações de persistência
- **Refatorações**: abstração de criação de diretório em `storage/storage.py` e padronização de logs em `database/database.py`

Veja mais detalhes em [Planejamento e Desenvolvimento](projetos/analise_dado_pokeapi/desenvolvimento.md).
