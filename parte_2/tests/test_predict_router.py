from http import HTTPStatus
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from microservice_nre.database.models import MLModel
from microservice_nre.database.schemas import PredictResponse


def test_predict_returns_entities(client):
    mock_service = MagicMock()
    mock_service.process_text = AsyncMock(
        return_value=PredictResponse(person='João', money='', date='')
    )
    client.app.state.service = mock_service

    with patch(
        'microservice_nre.routers.predict.registry.get_by_name',
        new_callable=AsyncMock,
        return_value=None,
    ):
        response = client.post(
            '/predict/',
            json={'text': 'João está no Brasil', 'model': 'pt_core_news_sm'},
        )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'money': '', 'person': 'João', 'date': ''}


def test_predict_returns_empty_entities(client):
    mock_service = MagicMock()
    mock_service.process_text = AsyncMock(return_value=PredictResponse())
    client.app.state.service = mock_service

    with patch(
        'microservice_nre.routers.predict.registry.get_by_name',
        new_callable=AsyncMock,
        return_value=None,
    ):
        response = client.post(
            '/predict/',
            json={'text': 'texto sem entidades', 'model': 'pt_core_news_sm'},
        )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'money': '', 'person': '', 'date': ''}


def test_predict_logs_to_db_when_model_registered(client):
    mock_model = MLModel(model='pt_core_news_sm')
    mock_model.model_version = 1

    mock_service = MagicMock()
    mock_service.process_text = AsyncMock(return_value=PredictResponse())
    client.app.state.service = mock_service

    with patch(
        'microservice_nre.routers.predict.registry.get_by_name',
        new_callable=AsyncMock,
        return_value=mock_model,
    ):
        response = client.post(
            '/predict/',
            json={'text': 'Brasil é grande', 'model': 'pt_core_news_sm'},
        )

    assert response.status_code == HTTPStatus.OK


def test_predict_returns_503_when_service_unavailable(client):
    client.app.state.service = None

    response = client.post(
        '/predict/',
        json={'text': 'test text', 'model': 'pt_core_news_sm'},
    )

    assert response.status_code == HTTPStatus.SERVICE_UNAVAILABLE


def test_predict_requires_text_field(client):
    mock_service = MagicMock()
    client.app.state.service = mock_service

    response = client.post('/predict/', json={'model': 'pt_core_news_sm'})

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_predict_requires_model_field(client):
    mock_service = MagicMock()
    client.app.state.service = mock_service

    response = client.post('/predict/', json={'text': 'some text'})

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_predict_rejects_empty_text(client):
    mock_service = MagicMock()
    client.app.state.service = mock_service

    response = client.post('/predict/', json={'text': '', 'model': 'pt_core_news_sm'})

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_list_predicts_returns_empty_list(client):
    response = client.get('/predict/list')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == []
