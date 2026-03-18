<<<<<<< Updated upstream
"""Configuração centralizada do logger da aplicação.

Cria um logger nomeado pelo módulo com nível, formato e handlers definidos
pelas variáveis de ambiente via ``Settings``. Um ``execution_id`` UUID único
por processo é embutido em todas as mensagens, permitindo correlacionar logs
de uma mesma instância da aplicação mesmo em ambientes com múltiplos containers.

Handlers disponíveis (ativados via settings):
    - Console (``CONSOLE_LOG=true``): escreve em ``stdout``.
    - Arquivo (``LOG_FILE=<path>``): escreve em arquivo com encoding UTF-8.
"""

=======
>>>>>>> Stashed changes
import logging
import sys
import uuid

<<<<<<< Updated upstream
from microservice_nre.utils.settings import Settings

_s = Settings()
=======
from utils.settings import settings
>>>>>>> Stashed changes

execution_id = str(uuid.uuid4())

logger = logging.getLogger(__name__)
<<<<<<< Updated upstream
logger.setLevel(_s.LOG_LEVEL)

formatter = logging.Formatter(
    f'[%(asctime)s] %(levelname)-8s %(message)s exec_id:[{execution_id}]',
    datefmt='%H:%M:%S',
)

if _s.CONSOLE_LOG:
=======
logger.setLevel(settings.LOG_LEVEL)
formatter = logging.Formatter(
    f'[%(asctime)s] %(levelname)-8s %(message)s exec_id:[{execution_id}]', datefmt='%H:%M:%S'
)
if settings.CONSOLE_LOG:
>>>>>>> Stashed changes
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(settings.LOG_LEVEL)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
<<<<<<< Updated upstream

if _s.LOG_FILE:
    file_handler = logging.FileHandler(_s.LOG_FILE, encoding='utf-8')
    file_handler.setLevel(_s.LOG_LEVEL)
=======
if settings.LOG_FILE:
    file_handler = logging.FileHandler(settings.LOG_FILE, encoding='utf-8')
    file_handler.setLevel(settings.LOG_LEVEL)
>>>>>>> Stashed changes
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
