import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

from db_control import UserDomain

router = APIRouter()
log = logging.getLogger(__name__)


def _norm_required(value: object, *, field: str) -> str:
    normalized = str(value or "").strip()
    if not normalized:
        raise HTTPException(status_code=422, detail=f"{field} must not be empty")

    return normalized


def _norm_optional(value: object | None) -> str | None:
    normalized = str(value or "").strip()
    if not normalized:
        return None

    return normalized


@router.post("/users/discord/upsert")
async def upsert_user_by_discord(request: Request):
    try:
        body: dict[str, Any] = await request.json()
        if not isinstance(body, dict):
            raise HTTPException(
                status_code=422, detail="Request body must be a JSON object"
            )

        discord_id = _norm_required(body.get("discord_id"), field="discord_id")
        steam_id = _norm_optional(body.get("steam_id"))
        name = _norm_optional(body.get("name"))
        avatar_url = _norm_optional(body.get("avatar_url"))

        cid, created = UserDomain.create_or_get_user(
            discord_id=discord_id,
            steam_id=steam_id,
        )

        UserDomain.update_user_block(
            cid=cid,
            discord_id=discord_id,
            steam_id=steam_id,
            name=name,
            path_to_image=avatar_url,
        )

        user = UserDomain.get_user_block(cid)
        return JSONResponse(
            {
                "ok": True,
                "created": created,
                "cid": cid,
                "user": user,
            },
            status_code=200,
        )

    except HTTPException:
        raise

    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    except Exception as exc:
        log.exception("Failed upsert_user_by_discord: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to upsert user") from exc


@router.get("/users/steam/{steam_id}")
async def get_user_by_steam(steam_id: str):
    normalized_steam_id = _norm_required(steam_id, field="steam_id")
    try:
        user = UserDomain.get_user_block_by_steam(normalized_steam_id)
        if user is None:
            return JSONResponse(
                {
                    "ok": True,
                    "found": False,
                },
                status_code=200,
            )

        credentials = user.get("credentials") or {}
        cid = int(credentials["id"])
        return JSONResponse(
            {
                "ok": True,
                "found": True,
                "cid": cid,
                "user": user,
            },
            status_code=200,
        )

    except HTTPException:
        raise

    except Exception as exc:
        log.exception("Failed get_user_by_steam: %s", exc)
        raise HTTPException(
            status_code=500,
            detail="Failed to get user by steam",
        ) from exc
