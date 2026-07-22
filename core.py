import contextlib

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from template_env import LOCAL_SETUP


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

if LOCAL_SETUP:
    app.mount(
        "/static",
        StaticFiles(directory="static"),
        name="static",
    )
