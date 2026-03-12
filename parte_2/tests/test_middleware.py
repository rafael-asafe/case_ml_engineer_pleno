import uuid


def test_middleware_adds_request_id_header(client):
    response = client.get('/')

    assert 'x-request-id' in response.headers


def test_middleware_request_id_is_valid_uuid(client):
    response = client.get('/')

    request_id = response.headers['x-request-id']
    parsed = uuid.UUID(request_id)
    assert str(parsed) == request_id


def test_middleware_adds_process_time_header(client):
    response = client.get('/')

    assert 'x-process-time-ms' in response.headers


def test_middleware_process_time_is_non_negative(client):
    response = client.get('/')

    process_time = float(response.headers['x-process-time-ms'])
    assert process_time >= 0


def test_middleware_each_request_has_unique_id(client):
    response_a = client.get('/')
    response_b = client.get('/')

    assert response_a.headers['x-request-id'] != response_b.headers['x-request-id']
