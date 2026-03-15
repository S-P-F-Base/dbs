from typing import Any

from . import AccessDB, CredentialsDB, CustomizationDB, LimitDB
from .limit_db import LimitStatus


class UserDomain:
    @staticmethod
    def set_up_bd() -> None:
        CredentialsDB.set_up()
        AccessDB.set_up()
        CustomizationDB.set_up()
        LimitDB.set_up()

    @staticmethod
    def _str_id(value: int | str | None) -> str | None:
        if value is None:
            return None

        return str(value)

    @staticmethod
    def _build_user_block(credentials: dict[str, Any]) -> dict[str, Any]:
        cid = credentials["id"]

        return {
            "credentials": credentials,
            "access": AccessDB.get(cid),
            "customization": CustomizationDB.get(cid),
            "limits": LimitDB.list_by_owner(cid),
        }

    @staticmethod
    def create_new_user(
        discord_id: int | str, steam_id: int | str | None = None
    ) -> int:
        cid = CredentialsDB.create(
            discord_id=str(discord_id),
            steam64_id=UserDomain._str_id(steam_id),
        )
        AccessDB.create(cid)
        CustomizationDB.create(cid)
        return cid

    @staticmethod
    def user_exists_by_id(cid: int, *, include_dead: bool = False) -> bool:
        if include_dead:
            return CredentialsDB.get_by_id(cid) is not None

        return CredentialsDB.get_alive_by_id(cid) is not None

    @staticmethod
    def user_exists_by_discord(
        discord_id: int | str, *, include_dead: bool = False
    ) -> bool:
        if include_dead:
            return CredentialsDB.get_by_discord(str(discord_id)) is not None

        return CredentialsDB.get_alive_by_discord(str(discord_id)) is not None

    @staticmethod
    def user_exists_by_steam(
        steam_id: int | str, *, include_dead: bool = False
    ) -> bool:
        if include_dead:
            return CredentialsDB.get_by_steam(str(steam_id)) is not None

        return CredentialsDB.get_alive_by_steam(str(steam_id)) is not None

    @staticmethod
    def create_or_get_user(
        discord_id: int | str,
        steam_id: int | str | None = None,
    ) -> tuple[int, bool]:
        existing = CredentialsDB.get_alive_by_discord(str(discord_id))
        if existing is not None:
            return existing["id"], False

        if steam_id is not None:
            existing = CredentialsDB.get_alive_by_steam(str(steam_id))
            if existing is not None:
                return existing["id"], False

        cid = UserDomain.create_new_user(discord_id=discord_id, steam_id=steam_id)
        return cid, True

    @staticmethod
    def get_user_block(
        cid: int, *, include_dead: bool = False
    ) -> dict[str, Any] | None:
        credentials = (
            CredentialsDB.get_by_id(cid)
            if include_dead
            else CredentialsDB.get_alive_by_id(cid)
        )

        if credentials is None:
            return None

        return UserDomain._build_user_block(credentials)

    @staticmethod
    def get_user_block_by_discord(
        discord_id: int | str,
        *,
        include_dead: bool = False,
    ) -> dict[str, Any] | None:
        credentials = (
            CredentialsDB.get_by_discord(str(discord_id))
            if include_dead
            else CredentialsDB.get_alive_by_discord(str(discord_id))
        )

        if credentials is None:
            return None

        return UserDomain._build_user_block(credentials)

    @staticmethod
    def get_user_block_by_steam(
        steam_id: int | str,
        *,
        include_dead: bool = False,
    ) -> dict[str, Any] | None:
        credentials = (
            CredentialsDB.get_by_steam(str(steam_id))
            if include_dead
            else CredentialsDB.get_alive_by_steam(str(steam_id))
        )

        if credentials is None:
            return None

        return UserDomain._build_user_block(credentials)

    @staticmethod
    def update_user_block(
        cid: int,
        *,
        discord_id: int | str | None = None,
        steam_id: int | str | None = None,
        access: dict[str, bool] | None = None,
        name: str | None = None,
        path_to_image: str | None = None,
    ) -> None:
        if discord_id is not None or steam_id is not None:
            CredentialsDB.update(
                cid,
                discord_id=UserDomain._str_id(discord_id),
                steam64_id=UserDomain._str_id(steam_id),
            )

        if access is not None:
            AccessDB.update(cid=cid, access=access)

        if name is not None or path_to_image is not None:
            CustomizationDB.update(
                cid=cid,
                name=name,
                path_to_image=path_to_image,
            )

    @staticmethod
    def add_limit(
        cid: int,
        *,
        title: str,
        description: str | None = None,
        expires_at: int | None = None,
        status: LimitStatus = "normal",
    ) -> int:
        return LimitDB.create(
            cid=cid,
            title=title,
            description=description,
            expires_at=expires_at,
            status=status,
        )

    @staticmethod
    def update_limit(
        uid: int,
        *,
        title: str | None = None,
        description: str | None = None,
        expires_at: int | None = None,
        status: LimitStatus | None = None,
    ) -> None:
        LimitDB.update(
            uid=uid,
            title=title,
            description=description,
            expires_at=expires_at,
            status=status,
        )

    @staticmethod
    def clear_limit_expiration(uid: int) -> None:
        LimitDB.clear_expiration(uid)

    @staticmethod
    def set_limit_status(uid: int, status: LimitStatus) -> None:
        LimitDB.set_status(uid, status)

    @staticmethod
    def get_limit(uid: int) -> dict[str, Any] | None:
        return LimitDB.get(uid)

    @staticmethod
    def list_limits(cid: int) -> list[dict[str, Any]]:
        return LimitDB.list_by_owner(cid)

    @staticmethod
    def delete_limit(uid: int) -> None:
        LimitDB.delete(uid)

    @staticmethod
    def delete_user(cid: int) -> None:
        CredentialsDB.set_dead(cid)

    @staticmethod
    def restore_user(cid: int) -> None:
        CredentialsDB.clear_dead(cid)
