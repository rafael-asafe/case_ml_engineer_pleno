from http import HTTPStatus
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from microservice_nre.database.models import MLModel


def test_load_model_returns_created(client):
    mock_model = MLModel(model='new_model')
    mock_model.model_version = 1

    with (
        patch(
            'microservice_nre.routers.model.registry.register',
            new_callable=AsyncMock,
            return_value=mock_model,
        ),
        patch('microservice_nre.routers.model.asyncio.to_thread', new_callable=AsyncMock),
    ):
        response = client.post('/models/load', json={'model': 'new_model'})

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {'model': 'new_model', 'model_version': 1}


def test_load_model_conflict_returns_409(client):
    with patch(
        'microservice_nre.routers.model.registry.register',
        new_callable=AsyncMock,
        side_effect=HTTPException(
            status_code=HTTPStatus.CONFLICT, detail='Modelo já registrado'
        ),
    ):
        response = client.post('/models/load', json={'model': 'existing_model'})

    assert response.status_code == HTTPStatus.CONFLICT


def test_list_models_returns_empty_list(client):
    with patch(
        'microservice_nre.routers.model.registry.list',
        new_callable=AsyncMock,
        return_value=[],
    ):
        response = client.get('/models/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == []


def test_list_models_returns_registered_models(client):
    model_a = MLModel(model='model_a')
    model_a.model_version = 1
    model_b = MLModel(model='model_b')
    model_b.model_version = 2

    with patch(
        'microservice_nre.routers.model.registry.list',
        new_callable=AsyncMock,
        return_value=[model_a, model_b],
    ):
        response = client.get('/models/')

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert len(data) == 2


def test_delete_model_returns_no_content(client):
    mock_model = MLModel(model='some_model')
    mock_model.model_version = 1

    with (
        patch(
            'microservice_nre.routers.model.registry.get_by_version',
            new_callable=AsyncMock,
            return_value=mock_model,
        ),
        patch(
            'microservice_nre.routers.model.registry.delete',
            new_callable=AsyncMock,
        ),
    ):
        response = client.delete('/models/1')

    assert response.status_code == HTTPStatus.NO_CONTENT


def test_delete_model_not_found_returns_404(client):
    with patch(
        'microservice_nre.routers.model.registry.get_by_version',
        new_callable=AsyncMock,
        side_effect=HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Modelo não encontrado'
        ),
    ):
        response = client.delete('/models/999')

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_load_model_requires_model_field(client):
    response = client.post('/models/load', json={})

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
