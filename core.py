import contextlib

from fastapi import FastAPI

from router.authorization import router as auth_router


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

app.include_router(auth_router)
