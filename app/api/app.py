from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI

from app.api.routes import router
from app.config.database import get_engine
from app.config.logging import setup_logging
from app.config.settings import get_settings
from app.config.schema import init_schema


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    setup_logging(settings.log_level)
    await init_schema(get_engine())
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="Marjon Suv API", version="0.1.0", lifespan=lifespan)
    app.include_router(router)
    return app


app = create_app()
