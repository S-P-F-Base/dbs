import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

from db_control import UserDomain

router = APIRouter()
log = logging.getLogger(__name__)


async def _read_body(request: Request) -> dict[str, Any]:
    try:
        body: Any = await request.json()

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail="Request body must be valid JSON",
        ) from exc

    if not isinstance(body, dict):
        raise HTTPException(
            status_code=422,
            detail="Request body must be a JSON object",
        )

    return body


def _ok_response(**payload: Any) -> JSONResponse:
    return JSONResponse({"ok": True, **payload}, status_code=200)


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


def _norm_optional_cid(value: object | None) -> int | None:
    if value is None:
        return None

    text = str(value).strip()
    if not text:
        return None

    try:
        cid = int(text)

    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail="cid must be an integer") from exc

    if cid <= 0:
        raise HTTPException(status_code=422, detail="cid must be greater than 0")

    return cid


def _norm_optional_access(value: object | None) -> dict[str, bool] | None:
    if value is None:
        return None

    if not isinstance(value, dict):
        raise HTTPException(status_code=422, detail="access must be an object")

    normalized: dict[str, bool] = {}
    for key, key_value in value.items():
        key_text = str(key).strip()
        if not key_text:
            raise HTTPException(status_code=422, detail="access keys must not be empty")

        if not isinstance(key_value, bool):
            raise HTTPException(
                status_code=422,
                detail=f"access.{key_text} must be boolean",
            )

        normalized[key_text] = key_value

    return normalized


def _resolve_user(
    *,
    cid: int | None,
    discord_id: str | None,
    steam_id: str | None,
) -> dict[str, Any] | None:
    if cid is not None:
        return UserDomain.get_user_block(cid)

    if discord_id is not None:
        return UserDomain.get_user_block_by_discord(discord_id)

    if steam_id is not None:
        return UserDomain.get_user_block_by_steam(steam_id)

    raise HTTPException(
        status_code=422,
        detail="One of cid, discord_id or steam_id is required",
    )


def _resolve_user_from_body(
    body: dict[str, Any],
    *,
    discord_key: str = "discord_id",
    steam_key: str = "steam_id",
) -> dict[str, Any] | None:
    return _resolve_user(
        cid=_norm_optional_cid(body.get("cid")),
        discord_id=_norm_optional(body.get(discord_key)),
        steam_id=_norm_optional(body.get(steam_key)),
    )


def _extract_user_cid(user: dict[str, Any]) -> int:
    credentials = user.get("credentials")
    if not isinstance(credentials, dict):
        raise HTTPException(status_code=500, detail="User payload is invalid")

    try:
        return int(credentials["id"])

    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=500, detail="User payload is invalid") from exc


@router.post("/dbs/user/create")
async def create_user(request: Request):
    try:
        body = await _read_body(request)

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
        return _ok_response(created=created, cid=cid, user=user)

    except HTTPException:
        raise

    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    except Exception as exc:
        log.exception("Failed create_user: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to create user") from exc


@router.post("/dbs/user/get")
async def get_user(request: Request):
    try:
        body = await _read_body(request)
        user = _resolve_user_from_body(body)

        if user is None:
            return _ok_response(found=False)

        return _ok_response(
            found=True,
            cid=_extract_user_cid(user),
            user=user,
        )

    except HTTPException:
        raise

    except Exception as exc:
        log.exception("Failed get_user: %s", exc)
        raise HTTPException(
            status_code=500,
            detail="Failed to get user",
        ) from exc


@router.post("/dbs/user/delete")
async def delete_user(request: Request):
    try:
        body = await _read_body(request)
        user = _resolve_user_from_body(body)

        if user is None:
            return _ok_response(deleted=False)

        user_cid = _extract_user_cid(user)
        UserDomain.delete_user(user_cid)
        return _ok_response(
            deleted=True,
            cid=user_cid,
        )

    except HTTPException:
        raise

    except Exception as exc:
        log.exception("Failed delete_user: %s", exc)
        raise HTTPException(
            status_code=500,
            detail="Failed to delete user",
        ) from exc


@router.post("/dbs/user/update")
async def update_user(request: Request):
    try:
        body = await _read_body(request)
        user = _resolve_user_from_body(body)

        if user is None:
            return _ok_response(updated=False)

        user_cid = _extract_user_cid(user)
        discord_id = _norm_optional(body.get("new_discord_id"))
        steam_id = _norm_optional(body.get("new_steam_id"))
        access = _norm_optional_access(body.get("access"))
        name = _norm_optional(body.get("name"))
        avatar_url = _norm_optional(body.get("avatar_url"))

        if (
            discord_id is None
            and steam_id is None
            and access is None
            and name is None
            and avatar_url is None
        ):
            raise HTTPException(
                status_code=422,
                detail="At least one update field is required",
            )

        UserDomain.update_user_block(
            cid=user_cid,
            discord_id=discord_id,
            steam_id=steam_id,
            access=access,
            name=name,
            path_to_image=avatar_url,
        )
        updated_user = UserDomain.get_user_block(user_cid)
        return _ok_response(updated=True, cid=user_cid, user=updated_user)

    except HTTPException:
        raise

    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    except Exception as exc:
        log.exception("Failed update_user: %s", exc)
        raise HTTPException(
            status_code=500,
            detail="Failed to update user",
        ) from exc
