from dataclasses import asdict
from http import HTTPStatus
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from microservice_nre.services.model_registry import ModelRegistry


@pytest.mark.asyncio
async def test_register_new_model(session: AsyncSession):
    registry = ModelRegistry()

    with patch(
        'microservice_nre.services.model_registry.download_model',
        new_callable=AsyncMock,
    ):
        result = await registry.register('test_model', session)

    assert result.model == 'test_model'
    assert result.model_version is not None


@pytest.mark.asyncio
async def test_register_duplicate_model_raises_conflict(session: AsyncSession):
    registry = ModelRegistry()

    with patch(
        'microservice_nre.services.model_registry.download_model',
        new_callable=AsyncMock,
    ):
        await registry.register('test_model', session)

    with pytest.raises(HTTPException) as exc_info:
        with patch(
            'microservice_nre.services.model_registry.download_model',
            new_callable=AsyncMock,
        ):
            await registry.register('test_model', session)

    assert exc_info.value.status_code == HTTPStatus.CONFLICT


@pytest.mark.asyncio
async def test_list_returns_all_models(session: AsyncSession):
    registry = ModelRegistry()

    with patch(
        'microservice_nre.services.model_registry.download_model',
        new_callable=AsyncMock,
    ):
        await registry.register('model_a', session)
        await registry.register('model_b', session)

    models = await registry.list(session)

    assert len(models) == 2
    names = {m.model for m in models}
    assert names == {'model_a', 'model_b'}


@pytest.mark.asyncio
async def test_list_empty_returns_empty_list(session: AsyncSession):
    registry = ModelRegistry()

    models = await registry.list(session)

    assert models == []


@pytest.mark.asyncio
async def test_get_by_version_returns_correct_model(session: AsyncSession):
    registry = ModelRegistry()

    with patch(
        'microservice_nre.services.model_registry.download_model',
        new_callable=AsyncMock,
    ):
        created = await registry.register('test_model', session)

    found = await registry.get_by_version(created.model_version, session)

    assert found.model == 'test_model'
    assert found.model_version == created.model_version


@pytest.mark.asyncio
async def test_get_by_version_raises_404_when_not_found(session: AsyncSession):
    registry = ModelRegistry()

    with pytest.raises(HTTPException) as exc_info:
        await registry.get_by_version(999, session)

    assert exc_info.value.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_get_by_name_returns_model(session: AsyncSession):
    registry = ModelRegistry()

    with patch(
        'microservice_nre.services.model_registry.download_model',
        new_callable=AsyncMock,
    ):
        created = await registry.register('my_model', session)

    found = await registry.get_by_name('my_model', session)

    assert found is not None
    assert found.model_version == created.model_version


@pytest.mark.asyncio
async def test_get_by_name_returns_none_when_not_found(session: AsyncSession):
    registry = ModelRegistry()

    result = await registry.get_by_name('nonexistent', session)

    assert result is None


@pytest.mark.asyncio
async def test_delete_removes_model(session: AsyncSession):
    registry = ModelRegistry()

    with patch(
        'microservice_nre.services.model_registry.download_model',
        new_callable=AsyncMock,
    ):
        created = await registry.register('to_delete', session)

    await registry.delete(created.model_version, session)

    models = await registry.list(session)
    assert len(models) == 0


@pytest.mark.asyncio
async def test_delete_raises_404_for_missing_version(session: AsyncSession):
    registry = ModelRegistry()

    with pytest.raises(HTTPException) as exc_info:
        await registry.delete(999, session)

    assert exc_info.value.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_register_returns_correct_schema(session: AsyncSession):
    registry = ModelRegistry()

    with patch(
        'microservice_nre.services.model_registry.download_model',
        new_callable=AsyncMock,
    ):
        result = await registry.register('schema_model', session)

    assert asdict(result) == {'model': 'schema_model', 'model_version': 1}
