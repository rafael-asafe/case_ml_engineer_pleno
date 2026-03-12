"""Download assíncrono de modelos spaCy.

Executa ``python -m spacy download <model>`` como subprocesso, permitindo
que o event loop continue processando outras requisições durante o download.
"""

import asyncio
import sys

from microservice_nre.utils.logger import logger


async def download_model(model_name: str) -> str:
    """Baixa um modelo spaCy via subprocesso assíncrono.


    Args:
        model_name: Nome do pacote spaCy a ser baixado (ex: ``"pt_core_news_sm"``).

    Returns:
        O próprio ``model_name`` em caso de sucesso.

    Raises:
        RuntimeError: Se o subprocesso retornar código de saída diferente de zero,
            indicando falha no download (modelo inválido, sem conexão, etc.).
    """
    logger.info(f"Downloading model '{model_name}'...")

    proc = await asyncio.create_subprocess_exec(
        sys.executable,
        '-m',
        'spacy',
        'download',
        model_name,
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.PIPE,
    )
    _, stderr = await proc.communicate()
    if proc.returncode != 0:
        logger.error(f"Failed to download model '{model_name}': {stderr.decode()}")
        raise RuntimeError(f"Failed to download model '{model_name}'")

    logger.info(f"Model '{model_name}' ready")
    return model_name
