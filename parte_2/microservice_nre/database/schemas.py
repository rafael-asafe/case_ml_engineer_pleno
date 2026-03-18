

from datetime import datetime

from pydantic import BaseModel, Field

from microservice_nre.utils.settings import settings


class MLModelSchema(BaseModel):
    

    model: str


class MLModelPublic(BaseModel):
    

    model_version: int
    model: str


class PredictLogsPublic(BaseModel):
    

    input: dict
    output: dict
    timestamp: datetime
    model_version: int


class PredictRequest(BaseModel):
    

    text: str = Field(..., min_length=1, max_length=settings.MAX_TEXT_LENGTH)
    model: str = Field(..., min_length=1)


class PredictResponse(BaseModel):
    

    money: str = ''
    person: str = ''
    date: str = ''
