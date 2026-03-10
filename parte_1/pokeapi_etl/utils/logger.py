import logging
import sys
import uuid

from utils.settings import Settings

execution_id = str(uuid.uuid4())

def setup_logger(log_to_console: bool = True) -> logging.Logger:
    """Configuração do logger"""

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
