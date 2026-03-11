# Análise de Dados com PokeAPI

## Como executar

Pipeline ETL que extrai dados de todos os pokémons da [PokéAPI](https://pokeapi.co/), persiste em banco SQLite e exporta em formato Parquet.

## Pré-requisito

- [Docker](https://docs.docker.com/get-docker/) instalado

---

## 1. Clone o repositório

```bash
git clone <url-do-repo>
cd case_ml_engineer_pleno/parte_1
```

---

## 2. Configure o arquivo `.env`

Crie o arquivo `.env` na raiz de `parte_1/`:

```env
# Log
LOG_LEVEL=DEBUG
CONSOLE_LOG=TRUE

# Database
DATABASE_URL=sqlite:///database.db

# Storage
NOME_PASTA_SOR=SOR/pokemons/today_date/
NOME_ARQUIVO_SOR=pokemons.jsonl
NOME_PASTA_SOT=SOT/
CAMINHO_DADOS=./data/

# Client - paginação
LIMIT_OFFSET=20

# Client - retry
RETRY=5
BACKOFF_FACTOR=0.5

# Client - connection limits
CLIENT_MAX_CONNECTIONS=50
MAX_KEEPALIVE_CONNECTIONS=20
KEEPALIVE_EXPIRY=10
POKEAPI_BASE_URL=https://pokeapi.co/api/v2/
```

---

## 3. Crie os arquivos de persistência local

```bash
mkdir -p data
touch database.db
```

> O `database.db` precisa existir antes de subir o container — caso contrário o Docker cria um diretório no lugar.

---

## 4. Execute

```bash
docker compose up
```

Na primeira execução a imagem será buildada automaticamente. Nas seguintes, use `--build` apenas se o código ou dependências mudarem:

```bash
docker compose up --build
```

---

## Saída esperada

Ao final da execução, os dados estarão disponíveis localmente em:

```
data/
├── SOR/
│   └── pokemons/
│       └── <ano>/<mes>/<dia>/
│           └── pokemons.jsonl      # dados brutos (um JSON por linha)
└── SOT/
    ├── pokemon/<ano>/<mes>/<dia>/pokemon.parquet
    ├── pokemon_ability/<ano>/<mes>/<dia>/pokemon_ability.parquet
    ├── pokemon_stats/<ano>/<mes>/<dia>/pokemon_stats.parquet
    └── pokemon_type/<ano>/<mes>/<dia>/pokemon_type.parquet

database.db                         # banco SQLite com todas as tabelas
```

## Analise de dados
- adicione as tabelas ao seu ambiente

- criei a tabela usando o UI do databricks

- importe as tabelas no notebook


## Modelagem de dados

Sugestão: padronizar o nome dos campos 

pokemon_id:
pokemon_name:

etc