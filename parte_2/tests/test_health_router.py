from datetime import datetime
from http import HTTPStatus
from unittest.mock import MagicMock


def test_health_returns_healthy(client):
    mock_service = MagicMock()
    mock_service.startup_time = datetime.now()
    mock_service.request_count = 10
    mock_service.loaded_models = 1
    client.app.state.service = mock_service
    response = client.get('/health')

    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data['status'] == 'healthy'
    assert 'timestamp' in data
    assert 'uptime_seconds' in data
    assert data['requests_total'] == 10
    assert data['models_in_memory'] == 1


def test_health_returns_healthy_with_no_models(client):
    mock_service = MagicMock()
    mock_service.startup_time = datetime.now()
    mock_service.request_count = 0
    mock_service.loaded_models = 0
    client.app.state.service = mock_service

    response = client.get('/health')

    assert response.status_code == HTTPStatus.OK
    assert response.json()['models_in_memory'] == 0


def test_health_returns_503_when_service_not_initialized(client):
    client.app.state.service = None

    response = client.get('/health')

    assert response.status_code == HTTPStatus.SERVICE_UNAVAILABLE
    assert response.json() == {'status': 'starting'}
