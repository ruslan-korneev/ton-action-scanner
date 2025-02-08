from fastapi import FastAPI
from sentry_sdk import init as sentry_init
from sentry_sdk.integrations.asyncio import AsyncioIntegration
from sentry_sdk.integrations.asyncpg import AsyncPGIntegration
from sentry_sdk.integrations.loguru import LoguruIntegration
from starlette.middleware.cors import CORSMiddleware

from src.core.api import api_v1
from src.core.config import settings


def get_app() -> FastAPI:
    if sentry_dsn := settings.sentry_dsn.get_secret_value():
        sentry_init(
            dsn=sentry_dsn,
            enable_tracing=True,
            traces_sample_rate=1.0,
            profiles_sample_rate=1.0,
            integrations=[
                AsyncioIntegration(),
                AsyncPGIntegration(),
                LoguruIntegration(),
            ],
        )

    app = FastAPI(
        debug=settings.logging_level == "DEBUG",
        title=settings.project_title,
        description=settings.project_description,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_origin_regex="^https?://.*$",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.mount("/v1", api_v1)
    return app
