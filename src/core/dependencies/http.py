from typing import Annotated

from fastapi import Depends
from httpx import AsyncClient

from src.core.http import AsyncClientSingleton


def get_httpx_client() -> AsyncClient:
    return AsyncClientSingleton()


AsyncClientDep = Annotated[AsyncClient, Depends(get_httpx_client)]
