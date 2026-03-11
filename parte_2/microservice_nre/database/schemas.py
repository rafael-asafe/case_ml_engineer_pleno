from datetime import datetime

from pydantic import BaseModel


class MLModelSchema(BaseModel):
    model: str


class MLModelPublic(BaseModel):
    model_version: int
    model: str


class PredictLogsSchema(BaseModel):
    log_id: int
    request: dict
    response: dict
    timestamp: datetime
    model_version: int


class PredictLogsPublic(BaseModel):
    request: dict
    response: dict
    timestamp: datetime
    model_version: int
