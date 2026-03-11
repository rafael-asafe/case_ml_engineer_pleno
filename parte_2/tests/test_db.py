from dataclasses import asdict

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from microservice_nre.database.models import MLModel


@pytest.mark.asyncio
async def test_create_ml_model(session: AsyncSession):

    new_user = MLModel(model='teste')

    session.add(new_user)
    await session.commit()

    ml_model = await session.scalar(select(MLModel).where(MLModel.model == 'teste'))

    assert asdict(ml_model) == {'model': 'teste', 'model_version': 1}
