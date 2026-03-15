import contextlib

from fastapi import FastAPI

from db_control import (
    BlacklistDB,
    CommerceServicesDB,
    CommercialChecksDB,
    LoreCharRegistryDB,
    NoteDB,
    OptinDB,
    PlayerCharDB,
    TraitRegistryDB,
    UserDomain,
)
from router.overlord_api import router as overlord_api_router


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        for cl in [
            UserDomain,
        ]:
            cl.set_up_bd()

        for cl in [
            BlacklistDB,
            CommerceServicesDB,
            CommercialChecksDB,
            LoreCharRegistryDB,
            NoteDB,
            OptinDB,
            PlayerCharDB,
            TraitRegistryDB,
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

app.include_router(overlord_api_router)
