import contextlib

from fastapi import FastAPI

from router.info_api import router as info_api_router
from router.overlord_api import router as overlord_api_router
from router.user_api import router as user_api_router

from db_control import (
    AccessDB,
    BlacklistDB,
    CommerceServicesDB,
    CommercialChecksDB,
    CredentialsDB,
    CustomizationDB,
    ForgetmeDB,
    LoreCharRegistryDB,
    NoteDB,
    OptinDB,
    PermaLimitDB,
    PlayerCharDB,
    TimedLimitDB,
)


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        for cl in [
            AccessDB,
            BlacklistDB,
            CommerceServicesDB,
            CommercialChecksDB,
            CredentialsDB,
            CustomizationDB,
            ForgetmeDB,
            LoreCharRegistryDB,
            NoteDB,
            OptinDB,
            PermaLimitDB,
            PlayerCharDB,
            TimedLimitDB,
        ]:
            cl.set_up()

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
