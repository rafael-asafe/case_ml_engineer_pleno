import logging
import sys

from utils.settings import Settings


def setup_logger(log_to_console=True):
    """Configuração do logger"""

    # inicializa o logger
    logger = logging.getLogger(__name__)
    logger.setLevel(Settings().LOG_LEVEL)

    # específica o formato da mensagem
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)-8s %(message)s", datefmt="%H:%M:%S"
    )

    # adiciona um handler para mostrar as informações no stout, caso necessário
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)  # Mostra INFO e acima no terminal
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


logger = setup_logger(log_to_console=Settings().CONSOLE_LOG)
