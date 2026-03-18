

import asyncio
from datetime import datetime

import spacy

from microservice_nre.database.schemas import PredictResponse

_LABEL_TO_FIELD: dict[str, str] = {
    'MONEY': 'money',
    'PERSON': 'person',
    'DATE': 'date',
}


class SpacyService:
    

    def __init__(self) -> None:
        self._models: dict[str, spacy.Language] = {}
        self.request_count = 0
        self.startup_time = datetime.now()

    @property
    def loaded_models(self) -> int:
        
        return len(self._models)

    def add_model(self, name: str, nlp: spacy.Language) -> None:
        
        self._models[name] = nlp

    def remove_model(self, name: str) -> None:
        
        self._models.pop(name, None)

    def clear(self) -> None:
        
        self._models.clear()

    async def process_text(self, text: str, model: str) -> PredictResponse:
        
        self.request_count += 1
        output = await asyncio.to_thread(self._models[model], text)

        nlp_analysis = {
            _LABEL_TO_FIELD[e.label_]: e.text for e in output.ents if e.label_ in _LABEL_TO_FIELD
        }
        return PredictResponse(**nlp_analysis)
