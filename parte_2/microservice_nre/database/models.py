from datetime import datetime

from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, registry

table_registry = registry()


@table_registry.mapped_as_dataclass
class MLModel:
    __tablename__ = "models"
   
    model_version: Mapped[int] = mapped_column(primary_key=True,init=False)
    model: Mapped[str]


@table_registry.mapped_as_dataclass
class PredictLogs:
    __tablename__ = "predict_logs"

    log_id: Mapped[int] = mapped_column(primary_key=True,init=False)
    request: Mapped[str]
    response: Mapped[str]
    timestamp: Mapped[datetime] = mapped_column(init=False,server_default=func.now())
    model_version: Mapped[int] = mapped_column(ForeignKey("models.model_version"))