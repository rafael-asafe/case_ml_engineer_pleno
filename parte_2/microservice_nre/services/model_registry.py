

from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from microservice_nre.database.models import MLModel
from microservice_nre.services.model_downloader import download_model


class ModelRegistry:
    

    async def register(self, model_name: str, session: AsyncSession) -> MLModel:
        
        if await session.scalar(select(MLModel).where(MLModel.model == model_name)):
            raise HTTPException(status_code=HTTPStatus.CONFLICT, detail='Modelo já registrado')

        await download_model(model_name)

        model_obj = MLModel(model=model_name)
        session.add(model_obj)
        await session.commit()
        await session.refresh(model_obj)
        return model_obj

    async def list(self, session: AsyncSession) -> list[MLModel]:
        
        return (await session.execute(select(MLModel))).scalars().all()

    async def get_by_version(self, model_version: int, session: AsyncSession) -> MLModel:
        
        model_obj = await session.scalar(
            select(MLModel).where(MLModel.model_version == model_version)
        )
        if not model_obj:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Modelo não encontrado')
        return model_obj

    async def get_by_name(self, model_name: str, session: AsyncSession) -> MLModel | None:
        
        return await session.scalar(select(MLModel).where(MLModel.model == model_name))

    async def delete(self, model_version: int, session: AsyncSession) -> None:
        
        model_obj = await self.get_by_version(model_version, session)
        await session.delete(model_obj)
        await session.commit()
