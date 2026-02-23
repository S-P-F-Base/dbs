import sqlite3
from collections.abc import Callable
from typing import Any

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from db_control import (
    AccessDB,
    BlacklistDB,
    CredentialsDB,
    CustomizationDB,
    OptinDB,
    PermaLimitDB,
)

router = APIRouter()


@router.get("/dbs/user/{id}")
async def user_get(id: int):
    return JSONResponse(
        {
            "ok": True,
            "id": id,
        },
        status_code=200,
    )


@router.post("/dbs/user/{id}/{action}")
async def user_post(id: int, action: str, payload: dict[str, Any]):
    func = _USER_POST_DISP.get(action, None)
    if func is None:
        return JSONResponse(
            {"ok": False, "info": f"unknown type of action: {action}"},
            status_code=400,
        )

    return func(id, payload)


def create_user(id: int, payload: dict[str, Any]) -> JSONResponse:
    if id != 0:
        return JSONResponse(
            {"ok": False, "info": "(id != 0) is false"},
            status_code=400,
        )

    if (discord_id := payload.get("discord_id", None)) is None:
        pass

    steam_id = payload.get("steam_id", None)
    if steam_id is not None:
        steam_id = str(steam_id)

    try:
        new_user_id = CredentialsDB.create(str(discord_id), steam_id)

    except sqlite3.IntegrityError:
        return JSONResponse(
            {"ok": False, "info": "discord_id duplication"},
            status_code=400,
        )

    CustomizationDB.create(
        cid=new_user_id,
    )

    AccessDB.create(  # TODO:
        cid=new_user_id,
    )

    BlacklistDB.create(  # TODO:
        cid=new_user_id,
    )

    OptinDB.create(  # TODO:
        cid=new_user_id,
    )

    PermaLimitDB.create(  # Сделано
        cid=new_user_id,
        char_slot=2,
        lore_char_slot=1,
        weight_bytes=50 * 1024 * 1024,  # 50 mb
    )

    return JSONResponse(
        {"ok": True, "id": new_user_id},
        status_code=200,
    )


def delete_user(id: int, payload: dict[str, Any]) -> JSONResponse:  # TODO:
    pass


_USER_POST_DISP: dict[str, Callable[[int, dict[str, Any]], JSONResponse]] = {
    "create": create_user,
    "delete": delete_user,
}
