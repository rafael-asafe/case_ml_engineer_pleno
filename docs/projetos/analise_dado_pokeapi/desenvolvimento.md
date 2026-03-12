# Planejamento e Desenvolvimento

## Uso de IA

Foi utilizado o assistente **Claude Code** para revisão de código e criação de testes unitários.

### Contribuições

#### 1. Criação de Testes Unitários

Suite de testes criada para a Parte 1 do projeto (ETL da PokeAPI):

**`tests/test_schemas.py`** — 10 testes cobrindo os schemas Pydantic:

- Extração de campos aninhados (`type_name`, `stat_name`, `ability_name`)
- Validação de tipos (`base_stat` como `int`, `is_hidden` como `bool`)
- Comportamento de defaults (`base_experience` ausente → `0`)
- Geração de IDs únicos por instância
- Erro ao receber payload inválido

**`tests/test_storage.py`** — 5 testes cobrindo `OperadorArmazenamento.gerar_pokemons()`:

- Retorno de schema válido
- Preservação de nome e IDs
- Múltiplos retornos
- Lista vazia

#### 2. Refatorações

**`storage/storage.py`** — abstração de código para criação de diretório em uma função privada, reduzindo duplicação e removendo comentários TO-DO resolvidos.

**`database/database.py`** — padronização de mensagens de log.

### Avaliação

O assistente se mostrou eficiente para criar cenários de testes, padronizar logs e gerar docstrings. Alguns ajustes manuais foram necessários após revisão.
