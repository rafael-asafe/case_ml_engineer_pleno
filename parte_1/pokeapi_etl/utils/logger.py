"""Configuração centralizada de logging para o pipeline ETL.

Fornece um logger pré-configurado (``logger``) e um ID de execução único
(``execution_id``) gerado no início de cada execução do processo. O ID é
incluído em todas as mensagens de log para facilitar a correlação de eventos
em ambientes com múltiplas execuções simultâneas ou em análise de logs históricos.

Uso típico::

    from utils.logger import logger

    logger.info('Mensagem informativa')
    logger.error('Ocorreu um erro')
"""

import logging
import sys
import uuid

from utils.settings import Settings

execution_id = str(uuid.uuid4())

def setup_logger(log_to_console: bool = True) -> logging.Logger:
    """Cria e configura uma instância de logger para o módulo atual.

    Inicializa o logger com o nível definido em ``Settings().LOG_LEVEL`` e
    aplica um formato padrão que inclui timestamp, nível, mensagem e o
    ``execution_id`` da execução corrente. Opcionalmente adiciona um handler
    de console (stdout).

    Args:
        log_to_console: Se ``True`` (padrão), adiciona um ``StreamHandler``
            direcionado ao ``stdout`` para exibir os logs no terminal. Defina
            como ``False`` em contextos onde o log de console não é desejado
            (ex.: testes automatizados com ``CONSOLE_LOG=false``).

    Returns:
        logging.Logger: Logger configurado com o handler e formatador definidos.

    Note:
        O formato das mensagens segue o padrão:
        ``[HH:MM:SS] LEVEL    mensagem exec_id:[uuid]``

        O ``execution_id`` é gerado uma única vez por processo (módulo importado)
        e permanece constante durante toda a execução.
    """

    # inicializa o logger
    logger = logging.getLogger(__name__)
    logger.setLevel(Settings().LOG_LEVEL)

    # específica o formato da mensagem
    formatter = logging.Formatter(f"[%(asctime)s] %(levelname)-8s %(message)s exec_id:[{execution_id}]", datefmt="%H:%M:%S"
    )

    # adiciona um handler para mostrar as informações no stout, caso necessário
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(Settings().LOG_LEVEL)  # Mostra INFO e acima no terminal
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


logger = setup_logger(log_to_console=Settings().CONSOLE_LOG)
