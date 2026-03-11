# Planejamento e Desenvolvimento


## Uso de IA

Foi utilizado o assistente **Claude Code** para revisão de código e criação de testes unitários.

Utilizando o prompt : "explique como você auxiliou no projeto e exporte para formato markdown o relatório abaixo foi gerado"

### Contribuições

#### 1. Criação de Testes Unitários

Criação da suite de testes para a Parte 1 do projeto (ETL da PokeAPI):

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

**`storage/storage.py`** — abstracao de codigo para criação de diretório em uma função privada, reduzindo duplicação de código e removendo comentários TO-DOs resolvidos.

**`database/database.py`** — padronização de mensagens de log.


### Review 

Embora foi necessário algumas revisões e ajustes nos testes criados, o assistente se mostrou muito eficiênte para criar cenários de testes,fazer padronizações de logs e docstrings 
