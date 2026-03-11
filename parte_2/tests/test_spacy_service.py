from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from microservice_nre.services.spacy_service import SpacyService


def test_service_initializes_with_empty_state():
    service = SpacyService()

    assert service._models == {}
    assert service.request_count == 0
    assert service.startup_time is not None


def test_add_model_stores_nlp_in_cache():
    service = SpacyService()
    mock_nlp = MagicMock()

    service.add_model('pt_core_news_sm', mock_nlp)

    assert service._models['pt_core_news_sm'] is mock_nlp


def test_loaded_models_returns_count():
    service = SpacyService()
    service._models = {'a': MagicMock(), 'b': MagicMock()}

    assert service.loaded_models == 2


def test_remove_model_removes_from_cache():
    service = SpacyService()
    service._models = {'pt_core_news_sm': MagicMock()}

    service.remove_model('pt_core_news_sm')

    assert 'pt_core_news_sm' not in service._models


def test_remove_model_is_noop_when_missing():
    service = SpacyService()

    service.remove_model('nonexistent')  # não deve lançar exceção


def test_clear_removes_all_cached_models():
    service = SpacyService()
    service._models = {'model_a': MagicMock(), 'model_b': MagicMock()}

    service.clear()

    assert service._models == {}


@pytest.mark.asyncio
async def test_process_text_increments_request_count():
    service = SpacyService()
    mock_doc = MagicMock()
    mock_doc.ents = []
    service._models['test_model'] = MagicMock()

    with patch('asyncio.to_thread', new_callable=AsyncMock, return_value=mock_doc):
        await service.process_text('hello world', 'test_model')

    assert service.request_count == 1


@pytest.mark.asyncio
async def test_process_text_returns_entities():
    service = SpacyService()

    ent_per = MagicMock()
    ent_per.label_ = 'PER'
    ent_per.text = 'João'

    ent_loc = MagicMock()
    ent_loc.label_ = 'LOC'
    ent_loc.text = 'Brasil'

    mock_doc = MagicMock()
    mock_doc.ents = [ent_per, ent_loc]
    service._models['pt_core_news_sm'] = MagicMock()

    with patch('asyncio.to_thread', new_callable=AsyncMock, return_value=mock_doc):
        result = await service.process_text('João está no Brasil', 'pt_core_news_sm')

    assert result == {'PER': 'João', 'LOC': 'Brasil'}


@pytest.mark.asyncio
async def test_process_text_increments_on_multiple_calls():
    service = SpacyService()
    mock_doc = MagicMock()
    mock_doc.ents = []
    service._models['model'] = MagicMock()

    with patch('asyncio.to_thread', new_callable=AsyncMock, return_value=mock_doc):
        await service.process_text('text one', 'model')
        await service.process_text('text two', 'model')
        await service.process_text('text three', 'model')

    assert service.request_count == 3


@pytest.mark.asyncio
async def test_process_text_raises_key_error_when_model_not_loaded():
    service = SpacyService()

    with pytest.raises(KeyError):
        await service.process_text('texto', 'modelo_nao_carregado')
