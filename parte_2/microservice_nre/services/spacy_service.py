"""Serviço de gerenciamento e inferência com modelos spaCy.

Mantém modelos carregados em memória para evitar o custo de I/O do ``spacy.load``
a cada requisição. Os modelos são populados no lifespan da aplicação e ao registrar
novos modelos via API.
"""

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
    """Gerencia modelos spaCy em memória e executa inferência de NER.

    Attributes:
        request_count: Contador de requisições de predição processadas desde o startup.
        startup_time: Momento de instanciação do serviço, usado para cálculo de uptime.
    """

    def __init__(self) -> None:
        self._models: dict[str, spacy.Language] = {}
        self.request_count = 0
        self.startup_time = datetime.now()

    @property
    def loaded_models(self) -> int:
        """Número de modelos atualmente carregados em memória."""
        return len(self._models)

    def add_model(self, name: str, nlp: spacy.Language) -> None:
        """Registra um modelo spaCy já carregado no cache em memória.

        Args:
            name: Nome do pacote spaCy (ex: ``"pt_core_news_sm"``).
            nlp: Objeto ``spacy.Language`` já inicializado.
        """
        self._models[name] = nlp

    def remove_model(self, name: str) -> None:
        """Remove um modelo do cache em memória, se presente.

        Args:
            name: Nome do pacote spaCy a ser removido.
        """
        self._models.pop(name, None)

    def clear(self) -> None:
        """Remove todos os modelos do cache. Chamado no encerramento da aplicação."""
        self._models.clear()

    async def process_text(self, text: str, model: str) -> PredictResponse:
        """Executa reconhecimento de entidades nomeadas (NER) em um texto.

        Args:
            text: Texto de entrada a ser processado.
            model: Nome do modelo spaCy a ser utilizado. Deve estar previamente
                carregado via ``add_model``; caso contrário, levanta ``KeyError``.

        Returns:
            ``TransacaoEntidades`` com os campos ``Operacao``, ``Valor``,
            ``Destino`` e ``Data`` preenchidos a partir das entidades extraídas.

        Raises:
            KeyError: Se o modelo não estiver no cache em memória.
        """
        self.request_count += 1
        output = await asyncio.to_thread(self._models[model], text)

        nlp_analysis = {
            _LABEL_TO_FIELD[e.label_]: e.text for e in output.ents if e.label_ in _LABEL_TO_FIELD
        }
        return PredictResponse(**nlp_analysis)
