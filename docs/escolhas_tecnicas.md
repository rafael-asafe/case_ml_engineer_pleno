# Escolhas técnicas

## Uso de IA

Foi utilizado o assistente **Claude Code** para revisão de código, criação de testes unitários e criação de documentações.

O assistente se mostrou eficiente para criar cenários de testes, padronizar logs e gerar docstrings, mas todo material está sendo revisado manualmente ao longo do projeto.

---

## Gerenciamento de projeto

### [Poetry](https://python-poetry.org/)

Gerenciador de dependências e empacotamento para Python. Substitui a combinação de `pip` + `requirements.txt` com um fluxo declarativo via `pyproject.toml`, garantindo ambientes reproduzíveis por meio do `poetry.lock`.

- Separação de dependências de produção e desenvolvimento (`[tool.poetry.dev-dependencies]`)
- Resolução determinística de versões com lockfile versionado
- Comandos unificados para instalação, publicação e gerenciamento de ambiente virtual

---

## Ferramentas de documentação

### [MkDocs](https://www.mkdocs.org/)

Ferramenta de escrita de documentação de projetos, bastante personalizável, com suporte a diversos plugins.

- **[mkdocstrings-python](https://mkdocstrings.github.io/python/)** — lê diretórios especificados no `mkdocs.yml` e gera páginas automaticamente a partir das docstrings do projeto.
- **[mkdocs-material](https://squidfunk.github.io/mkdocs-material/)** — tema visual com suporte a pesquisa, dark mode, navegação por abas e diversos componentes prontos.
- **[mkdocs-macros-plugin](https://mkdocs-macros-plugin.readthedocs.io/)** — permite usar variáveis e macros Jinja2 dentro das páginas de documentação, evitando repetição de conteúdo.

---

## Configuração

### [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)

Extensão do Pydantic para gerenciamento de configurações via variáveis de ambiente. Permite definir as settings da aplicação como um `BaseSettings`, com validação de tipos automática e suporte a arquivos `.env`.

---

## Processamento de dados

### [Polars](https://docs.pola.rs/)

Biblioteca de DataFrames em Python com core em Rust. Utilizada na Parte 1 para transformar e manipular os dados extraídos da PokeAPI antes de salvar os dados na camada SOT.

- Execução lazy com otimização de plano de consulta
- API expressiva para filtros, agregações e joins
- Performance superior ao Pandas em grandes volumes de dados

### [PyArrow](https://arrow.apache.org/docs/python/)

Biblioteca para trabalhar com o formato columnar Apache Arrow. Utilizada em conjunto com o Polars para exportar os dados transformados em formato **Parquet**, garantindo compressão eficiente e leitura rápida.

---

## Web Framework

### [FastAPI](https://fastapi.tiangolo.com/)

Framework web assíncrono de alta performance utilizado na Parte 2 para expor o microserviço de NER. Gera documentação OpenAPI automaticamente a partir das anotações de tipo e modelos Pydantic.

- Injeção de dependências nativa (`Depends`)
- Suporte a rotas assíncronas com `async def`
- Integração direta com Pydantic para validação de request/response

### [Uvicorn](https://www.uvicorn.org/)

Servidor ASGI leve e de alta performance utilizado para executar a aplicação FastAPI em produção.

---

## ORMs e banco de dados

### [SQLAlchemy](https://www.sqlalchemy.org/)

ORM (Object-Relational Mapping) que facilita a integração da aplicação com o banco de dados por meio de mapeamento de objetos. Reduz o acoplamento a um banco específico, permitindo trocar o driver com mínima alteração de código.

- **[Alembic](https://alembic.sqlalchemy.org/en/latest/)** — ferramenta auxiliar ao SQLAlchemy para migração de dados e gerenciamento do esquema do banco de dados.
- **[aiosqlite](https://aiosqlite.omnilib.dev/)** — driver assíncrono para SQLite, utilizado na Parte 2 com `SQLAlchemy[asyncio]` para operações não bloqueantes em produção e em testes com banco em memória.

### [Pydantic](https://docs.pydantic.dev/latest/)

A biblioteca mais usada para validação de dados em Python, com core em Rust para alto desempenho. Integra-se nativamente com SQLAlchemy e HTTPX no ecossistema do projeto.

- Validação de tipos com mensagens de erro claras
- Serialização e desserialização facilitadas
- `BaseModel` estende as dataclasses nativas do Python com novas funcionalidades

---

## HTTP

### [HTTPX](https://www.python-httpx.org/)

Biblioteca moderna de HTTP para Python com suporte nativo a operações assíncronas. Escolhida por sua compatibilidade com `asyncio` e por servir de base para as bibliotecas auxiliares do projeto.

- **[Hishel](https://hishel.com/)** — camada de cache HTTP sobre o HTTPX, armazenando respostas em SQLite para evitar requisições duplicadas à PokeAPI durante o ETL.
- **[httpx-retries](https://github.com/michaelkaye/httpx-retries)** — retentativas automáticas com backoff exponencial, aumentando a resiliência frente a falhas transitórias de rede.
- **Event hooks** — o cliente foi configurado com hooks de `before_request` e `after_response` para injetar IDs únicos de rastreamento e registrar métricas estruturadas (método, URL, status, tempo de resposta) em cada requisição.

---

## Testes

### [pytest](https://docs.pytest.org/)

Framework de testes principal do projeto, utilizado nas duas partes com configurações adaptadas a cada contexto.

- Na **Parte 1**, os testes síncronos executam corrotinas via `asyncio.run()` e utilizam fixtures customizadas para construir objetos `httpx.Response` de forma controlada.
- Na **Parte 2**, o plugin `pytest-asyncio` com `asyncio_mode = "auto"` elimina a necessidade de decorar cada teste manualmente, e o `TestClient` do FastAPI é empregado nos testes de rotas.

### [pytest-cov](https://pytest-cov.readthedocs.io/)

Plugin do pytest para geração de relatórios de cobertura de testes. Integrado ao comando de teste via Taskipy, permitindo visualizar quais linhas de código não estão cobertas.

### [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)

Plugin do pytest para suporte a testes assíncronos na Parte 2. Com `asyncio_mode = "auto"` no `pyproject.toml`, todas as corrotinas de teste são detectadas e executadas automaticamente.

### [Faker](https://faker.readthedocs.io/)

Biblioteca de geração de dados falsos. Integrada às factories de teste para produzir valores realistas (nomes, URLs, inteiros aleatórios) sem a necessidade de fixtures estáticas frágeis.

### [Factory Boy](https://factoryboy.readthedocs.io/)

Biblioteca para criação declarativa de objetos de teste. As factories definem a estrutura dos dados uma única vez e permitem gerar instâncias únicas ou em lote com `build()` / `build_batch(n)`.

- Utilizado em conjunto com `Faker` para popular atributos como nomes de Pokémon, URLs e estatísticas aleatórias.
- Suporta `factory.Sequence()` para IDs sequenciais e `factory.LazyFunction()` para valores computados em tempo de execução.

### [Respx](https://lundberg.github.io/respx/)

Biblioteca declarada como dependência de desenvolvimento para mock de requisições HTTPX. O assistente, optou-se por mockar as respostas HTTP diretamente com `unittest.mock` e instâncias manuais de `httpx.Request` / `httpx.Response`, vou refatorar essa parte.

---

## Qualidade de código

### [Ruff](https://docs.astral.sh/ruff/)

Linter e formatador para Python escrito em Rust. Substitui ferramentas como Flake8 e pycodestyle com execução significativamente mais rápida. Configurado no `pyproject.toml` de ambas as partes.

### [isort](https://pycqa.github.io/isort/)

Ferramenta para ordenação automática de imports Python. Garante consistência na organização dos blocos de import (stdlib, third-party, local) em todos os arquivos do projeto.

### [Taskipy](https://github.com/taskipy/taskipy)

Executor de tarefas configurado no `pyproject.toml` via `[tool.taskipy.tasks]`. Centraliza comandos recorrentes como `lint`, `test`, `run` e `docs`, evitando scripts shell avulsos e padronizando o fluxo de desenvolvimento.
