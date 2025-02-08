from types import TracebackType

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.config import settings


class AsyncSessionMaker:
    _engine = create_async_engine(
        url=settings.db.get_url().get_secret_value(),
        pool_pre_ping=True,
        future=True,
    )
    _sessionmaker = async_sessionmaker(
        bind=_engine,
        autoflush=False,
        autocommit=False,
    )

    def __init__(self) -> None:
        self._session = self._sessionmaker()

    async def __aenter__(self) -> AsyncSession:
        return await self._session.__aenter__()

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        return await self._session.__aexit__(exc_type, exc_value, traceback)
