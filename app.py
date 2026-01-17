import contextlib

from fastapi import FastAPI

from router.info_api import router as info_api_router
from router.overlord_api import router as overlord_api_router
from router.user_api import router as user_api_router


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        yield

    finally:
        pass


app = FastAPI(
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

app.include_router(info_api_router)
app.include_router(user_api_router)
app.include_router(overlord_api_router)
