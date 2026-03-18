"""Schemas Pydantic para validação de entrada e serialização de saída da API.

Separa a camada de transporte (HTTP) dos modelos ORM, garantindo que apenas
os campos necessários sejam expostos em cada contexto.
"""

from datetime import datetime

from pydantic import BaseModel, Field

from microservice_nre.utils.settings import Settings

_s = Settings()


class MLModelSchema(BaseModel):
    """Payload de entrada para registro de um novo modelo.

    Attributes:
        model: Nome do pacote spaCy a ser registrado (ex: ``"pt_core_news_sm"``).
    """

    model: str


class MLModelPublic(BaseModel):
    """Representação pública de um modelo registrado.

    Retornado nos endpoints de listagem e registro de modelos.

    Attributes:
        model_version: Versão autoincremental atribuída pelo banco.
        model: Nome do pacote spaCy.
    """

    model_version: int
    model: str


class PredictLogsPublic(BaseModel):
    """Representação pública de um log de predição.

    Retornado no endpoint ``GET /predict/list``.

    Attributes:
        input: Payload original da requisição de predição.
        output: Entidades extraídas no formato ``{label: texto}``.
        timestamp: Data e hora em que a predição foi realizada.
        model_version: Versão do modelo utilizado na inferência.
    """

    input: dict
    output: dict
    timestamp: datetime
    model_version: int


class PredictRequest(BaseModel):
    """Payload de entrada para o endpoint de inferência.

    Attributes:
        text: Texto a ser processado. Mínimo 1 caractere,
            máximo definido por ``MAX_TEXT_LENGTH`` nas settings.
        model: Nome do modelo spaCy a ser utilizado na inferência.
    """

    text: str = Field(..., min_length=1, max_length=_s.MAX_TEXT_LENGTH)
    model: str = Field(..., min_length=1)


class PredictResponse(BaseModel):
    """Resposta do endpoint de inferência NER."""

    money: str = ''
    person: str = ''
    date: str = ''
