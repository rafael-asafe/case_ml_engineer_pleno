from http import HTTPStatus


def test_root_deve_retornar_ok_e_ola_mundo(client):
    response = client.get('/')

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Hello World'}

# @pytest.mark.asyncio
def test_create_model(client):
    response = client.post('/load/', json={'model': 'teste'})
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {'model': 'teste', 'model_version': 1}
