import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from microservice_nre.services.model_downloader import download_model


@pytest.mark.asyncio
async def test_download_model_success():
    mock_proc = AsyncMock()
    mock_proc.returncode = 0
    mock_proc.communicate = AsyncMock(return_value=(b'', b''))

    with patch('asyncio.create_subprocess_exec', return_value=mock_proc):
        result = await download_model('test_model')

    assert result == 'test_model'


@pytest.mark.asyncio
async def test_download_model_failure_raises_runtime_error():
    mock_proc = AsyncMock()
    mock_proc.returncode = 1
    mock_proc.communicate = AsyncMock(return_value=(b'', b'Download failed'))

    with patch('asyncio.create_subprocess_exec', return_value=mock_proc):
        with pytest.raises(RuntimeError, match="Failed to download model 'bad_model'"):
            await download_model('bad_model')


@pytest.mark.asyncio
async def test_download_model_calls_spacy_download_command():
    import sys

    mock_proc = AsyncMock()
    mock_proc.returncode = 0
    mock_proc.communicate = AsyncMock(return_value=(0, 0))

    with patch('asyncio.create_subprocess_exec', return_value=mock_proc) as mock_exec:
        await download_model('pt_core_news_sm')

    mock_exec.assert_called_once_with(
        sys.executable,
        '-m',
        'spacy',
        'download',
        'pt_core_news_sm',
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.PIPE,
    )


@pytest.mark.asyncio
async def test_download_model_returns_model_name_on_success():
    mock_proc = AsyncMock()
    mock_proc.returncode = 0
    mock_proc.communicate = AsyncMock(return_value=(b'output', b''))

    with patch('asyncio.create_subprocess_exec', return_value=mock_proc):
        result = await download_model('en_core_web_sm')

    assert result == 'en_core_web_sm'
