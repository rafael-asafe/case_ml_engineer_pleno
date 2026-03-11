"""Registro de modelos spaCy no banco de dados.

Responsável por persistir, consultar e remover modelos registrados,
além de acionar o download quando um novo modelo é adicionado ao sistema.
"""

from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from microservice_nre.database.models import MLModel
from microservice_nre.services.model_downloader import download_model


class ModelRegistry:
    """Gerencia o ciclo de vida dos modelos registrados no banco de dados.

    Atua como camada de acesso a dados (repository) para a tabela ``models``,
    garantindo consistência entre o banco e o estado do sistema.
    """

    async def register(self, model_name: str, session: AsyncSession) -> MLModel:
        """Registra um novo modelo e aciona o download do pacote spaCy.

        Args:
            model_name: Nome do pacote spaCy (ex: ``"pt_core_news_sm"``).
            session: Sessão assíncrona do SQLAlchemy.

        Returns:
            Objeto ``MLModel`` recém-criado com a versão atribuída pelo banco.

        Raises:
            HTTPException(409): Se o modelo já estiver registrado.
            RuntimeError: Se o download do modelo falhar.
        """
        if await session.scalar(select(MLModel).where(MLModel.model == model_name)):
            raise HTTPException(status_code=HTTPStatus.CONFLICT, detail='Modelo já registrado')

        await download_model(model_name)

        model_obj = MLModel(model=model_name)
        session.add(model_obj)
        await session.commit()
        await session.refresh(model_obj)
        return model_obj

    async def list(self, session: AsyncSession) -> list[MLModel]:
        """Retorna todos os modelos registrados no banco.

        Args:
            session: Sessão assíncrona do SQLAlchemy.

        Returns:
            Lista de objetos ``MLModel``. Pode ser vazia se nenhum modelo foi registrado.
        """
        return (await session.execute(select(MLModel))).scalars().all()

    async def get_by_version(self, model_version: int, session: AsyncSession) -> MLModel:
        """Busca um modelo pelo número de versão.

        Args:
            model_version: Identificador único da versão do modelo.
            session: Sessão assíncrona do SQLAlchemy.

        Returns:
            Objeto ``MLModel`` correspondente à versão.

        Raises:
            HTTPException(404): Se nenhum modelo com essa versão for encontrado.
        """
        model_obj = await session.scalar(
            select(MLModel).where(MLModel.model_version == model_version)
        )
        if not model_obj:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Modelo não encontrado')
        return model_obj

    async def get_by_name(self, model_name: str, session: AsyncSession) -> MLModel | None:
        """Busca um modelo pelo nome do pacote spaCy.

        Args:
            model_name: Nome do pacote spaCy (ex: ``"pt_core_news_sm"``).
            session: Sessão assíncrona do SQLAlchemy.

        Returns:
            Objeto ``MLModel`` se encontrado, ``None`` caso contrário.
        """
        return await session.scalar(select(MLModel).where(MLModel.model == model_name))

    async def delete(self, model_version: int, session: AsyncSession) -> None:
        """Remove um modelo do banco pelo número de versão.

        Args:
            model_version: Identificador único da versão a ser removida.
            session: Sessão assíncrona do SQLAlchemy.

        Raises:
            HTTPException(404): Se nenhum modelo com essa versão for encontrado.
        """
        model_obj = await self.get_by_version(model_version, session)
        await session.delete(model_obj)
        await session.commit()
