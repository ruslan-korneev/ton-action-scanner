from typing import cast

from sqlalchemy import func, inspect, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import SAModel


class BaseRepository[_MT: SAModel]:
    _model: type[_MT]
    _session: AsyncSession

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def is_modified(data: _MT) -> bool:
        """
        Check if model instance has been modified
        """
        inspr = inspect(data)
        return inspr.modified or not inspr.has_identity

    async def save(self, data: _MT) -> _MT:
        """
        Save a new model instance or update if exists
        """
        if not self.is_modified(data):
            return data

        self._session.add(data)
        await self._session.flush()
        await self._session.refresh(data)

        return data

    async def count(self) -> int:
        query = select(func.count(self._model.id))
        result = await self._session.execute(query)
        return cast(int, result.scalar())
