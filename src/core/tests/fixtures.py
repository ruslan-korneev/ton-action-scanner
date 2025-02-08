import asyncio
from collections.abc import AsyncGenerator, Generator

import alembic
import alembic.command
import alembic.config
import asyncpg
import pytest
import pytest_asyncio
from _pytest.monkeypatch import MonkeyPatch
from httpx import ASGITransport, AsyncClient
from pytest_httpx import HTTPXMock
from sqlalchemy import Connection
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession, create_async_engine

from src.core.asgi import get_app
from src.core.config import settings
from src.core.dependencies.db import get_async_session
from src.core.dependencies.http import get_httpx_client


@pytest.fixture(scope="session")
def monkey_session() -> Generator[MonkeyPatch, None, None]:
    mp = MonkeyPatch()
    yield mp
    mp.undo()


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        yield loop
    finally:
        loop.close()


@pytest.fixture(scope="session")
def postgres_test_db_name(request: pytest.FixtureRequest) -> str:
    db_name = f"test-{settings.db.name}"
    xdist_suffix = getattr(request.config, "workerinput", {}).get("workerid")
    if xdist_suffix:  # NOTE: Put a suffix like _gw0, _gw1 etc on xdist processes
        db_name += f"_{xdist_suffix}"
    return db_name


@pytest.fixture(scope="session")
def postgres_test_db_url(postgres_test_db_name: str) -> str:
    return settings.db.get_url(scheme="postgresql+asyncpg", db_name=postgres_test_db_name).get_secret_value()


async def _create_test_db_if_not_exists(db_name: str) -> None:
    dsn = settings.db.get_url(scheme="postgresql", db_name=db_name).get_secret_value()
    try:
        await asyncpg.connect(dsn=dsn)
    except asyncpg.InvalidCatalogNameError:  # Database does not exist, create it.
        dsn = settings.db.get_url(scheme="postgresql").get_secret_value()
        sys_conn = await asyncpg.connect(dsn)
        await sys_conn.execute(f'CREATE DATABASE "{db_name}"')
        await sys_conn.close()


async def _delete_test_db_if_exists(db_name: str) -> None:
    dsn = settings.db.get_url(scheme="postgresql").get_secret_value()
    sys_conn = await asyncpg.connect(dsn)
    await sys_conn.execute(
        "SELECT pg_terminate_backend(pg_stat_activity.pid) "
        f"FROM pg_stat_activity WHERE pg_stat_activity.datname = '{db_name}'"
    )
    await sys_conn.execute(f'DROP DATABASE "{db_name}"')
    await sys_conn.close()


@pytest.fixture(scope="session", autouse=True)
async def create_test_db_if_not_exists(postgres_test_db_name: str) -> AsyncGenerator[None]:
    await _create_test_db_if_not_exists(postgres_test_db_name)
    yield
    await _delete_test_db_if_exists(postgres_test_db_name)


@pytest_asyncio.fixture(scope="session")
async def connection(postgres_test_db_url: str) -> AsyncGenerator[AsyncConnection]:
    engine = create_async_engine(url=postgres_test_db_url, pool_pre_ping=True)
    async with engine.connect() as conn:
        yield conn


@pytest_asyncio.fixture(scope="session")
async def alembic_config(postgres_test_db_url: str) -> alembic.config.Config:
    config = alembic.config.Config(settings.root_dir / "alembic.ini")
    config.set_main_option("sqlalchemy.url", postgres_test_db_url)
    return config


def _upgrade_database(connection: Connection, alembic_config: alembic.config.Config) -> None:
    alembic_config.attributes["connection"] = connection
    alembic.command.upgrade(config=alembic_config, revision="head")


@pytest_asyncio.fixture(scope="session", autouse=True)
async def migrate_database(connection: AsyncConnection, alembic_config: alembic.config.Config) -> None:
    await connection.run_sync(_upgrade_database, alembic_config)


@pytest_asyncio.fixture(autouse=True)
async def wrap_tests_with_transaction(migrate_database: None, connection: AsyncConnection) -> AsyncGenerator[None]:
    _ = migrate_database
    transaction = connection
    await transaction.begin()

    yield

    await transaction.rollback()


@pytest.fixture(scope="session")
async def session(connection: AsyncConnection) -> AsyncGenerator[AsyncSession]:
    async with AsyncSession(bind=connection) as session:
        yield session


@pytest.fixture
async def httpx_client(httpx_mock: HTTPXMock) -> AsyncGenerator[AsyncClient]:
    _ = httpx_mock
    async with AsyncClient() as client:
        yield client


@pytest.fixture(scope="session")
async def api_client(session: AsyncSession) -> AsyncGenerator[AsyncClient]:
    async def _get_test_async_session() -> AsyncGenerator[AsyncSession]:
        try:
            yield session
            await session.commit()
        except IntegrityError as exc:
            await session.rollback()
            raise exc

    async def _get_test_async_client() -> AsyncGenerator[AsyncClient]:
        async with AsyncClient() as client:
            yield client

    app = get_app()
    app.dependency_overrides[get_async_session] = _get_test_async_session
    app.dependency_overrides[get_httpx_client] = _get_test_async_client
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://0.0.0.0/") as client:
        yield client
