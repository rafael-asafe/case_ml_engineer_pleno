"""Modelos ORM do banco de dados.

Define as tabelas persistidas via SQLAlchemy usando a API de dataclass mapeada.
Todas as classes são registradas em `table_registry` e criadas pelo lifespan da aplicação.
"""

from datetime import datetime

from sqlalchemy import JSON, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, registry

table_registry = registry()


@table_registry.mapped_as_dataclass
class MLModel:
    """Representa um modelo spaCy registrado no sistema.

    Cada registro corresponde a uma versão única de modelo disponível para inferência.
    A versão (`model_version`) é gerada automaticamente pelo banco como chave primária
    autoincremental.

    Attributes:
        model_version: Identificador único e autoincremental da versão do modelo.
        model: Nome do pacote spaCy (ex: ``"pt_core_news_sm"``).
    """

    __tablename__ = "models"

    model_version: Mapped[int] = mapped_column(primary_key=True, init=False)
    model: Mapped[str]


@table_registry.mapped_as_dataclass
class PredictLogs:
    """Registro de uma predição realizada pelo serviço de NER.

    Armazena entrada, saída e metadados de cada chamada ao endpoint ``POST /predict``,
    permitindo auditoria e rastreabilidade das inferências.

    Attributes:
        log_id: Identificador único e autoincremental do log.
        input: Payload enviado na requisição (texto e nome do modelo).
        output: Entidades extraídas pelo modelo no formato ``{label: texto}``.
        timestamp: Data e hora da predição, preenchida automaticamente pelo banco.
        model_version: Referência à versão do modelo utilizado na inferência.
    """

    __tablename__ = "predict_logs"

    log_id: Mapped[int] = mapped_column(primary_key=True, init=False)
    input: Mapped[dict] = mapped_column(JSON)
    output: Mapped[dict] = mapped_column(JSON)
    timestamp: Mapped[datetime] = mapped_column(init=False, server_default=func.now())
    model_version: Mapped[int] = mapped_column(ForeignKey("models.model_version"))
