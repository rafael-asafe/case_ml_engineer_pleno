

import asyncio
import sys

from microservice_nre.utils.logger import logger


async def download_model(model_name: str) -> str:
    
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
