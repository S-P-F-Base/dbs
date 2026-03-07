from typing import Any, Final

from ..base_db import BaseDB, TableSpec


class CredentialsDB(BaseDB):
    _db_name = "credentials_db"

    _FIELDS: Final[dict[str, type]] = {
        "id": int,
        "discord_id": str,
        "steam64_id": str,
        "dirty": bool,
        "dead": bool,
    }

    TABLE = TableSpec(
        name="credentials_db",
        columns=[
            "id INTEGER PRIMARY KEY AUTOINCREMENT",  # Внутренний идентификатор учётки. Основной anchor/id для остальных доменов.
            "discord_id TEXT NOT NULL",  # Discord ID. Основной внешний идентификатор для логина, регистрации и привязки профиля.
            "steam64_id TEXT",  # Steam64 ID. Необязательная привязка Steam-аккаунта для связи сайта и игры.
            "dirty INTEGER NOT NULL DEFAULT 1",  # Флаг несинхронизированного состояния. 1 = запись требует синхронизации, 0 = синхронизирована.
            "dead INTEGER NOT NULL DEFAULT 0",  # Флаг soft delete. 1 = запись считается удалённой/неактивной, 0 = живая.
        ],
        indexes=[
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_credentials_db_discord_alive
            ON credentials_db (discord_id)
            WHERE dead = 0;
            """,
        ],
    )

    @classmethod
    def set_up(cls) -> None:
        cls._init_from_spec(cls.TABLE)

    @classmethod
    def create(cls, discord_id: str, steam64_id: str | None = None) -> int:
        return cls._insert(
            discord_id=(discord_id, str),
            steam64_id=(steam64_id, str),
        )

    @classmethod
    def delete(cls, credential_id: int) -> None:
        cls._delete(where=("id", credential_id))

    @classmethod
    def update(
        cls,
        credential_id: int,
        discord_id: str | None = None,
        steam64_id: str | None = None,
    ) -> None:
        cols: dict[str, tuple[object, type]] = {}

        if discord_id is not None:
            cols["discord_id"] = (discord_id, str)

        if steam64_id is not None:
            cols["steam64_id"] = (steam64_id, str)

        if not cols:
            return

        cls._update(
            where=("id", credential_id),
            **cols,
        )

    @classmethod
    def _get_by(cls, field: str, value: object) -> dict[str, Any] | None:
        return cls._get(
            where=(field, value),
            fields=cls._FIELDS,
        )

    @classmethod
    def _get_alive_by(cls, field: str, value: object) -> dict[str, Any] | None:
        return cls._get(
            where=[(field, value), ("dead", 0)],
            fields=cls._FIELDS,
        )

    @classmethod
    def get_by_id(cls, credential_id: int) -> dict[str, Any] | None:
        return cls._get_by(field="id", value=credential_id)

    @classmethod
    def get_by_discord(cls, discord_id: str) -> dict[str, Any] | None:
        return cls._get_by(field="discord_id", value=discord_id)

    @classmethod
    def get_by_steam(cls, steam64_id: str) -> dict[str, Any] | None:
        return cls._get_by(field="steam64_id", value=steam64_id)

    @classmethod
    def get_alive_by_id(cls, credential_id: int) -> dict[str, Any] | None:
        return cls._get_alive_by(field="id", value=credential_id)

    @classmethod
    def get_alive_by_discord(cls, discord_id: str) -> dict[str, Any] | None:
        return cls._get_alive_by(field="discord_id", value=discord_id)

    @classmethod
    def get_alive_by_steam(cls, steam64_id: str) -> dict[str, Any] | None:
        return cls._get_alive_by(field="steam64_id", value=steam64_id)

    @classmethod
    def _set_flag(cls, credential_id: int, field: str, value: bool) -> None:
        cls._update(
            where=("id", credential_id),
            **{field: (int(value), int)},
        )

    @classmethod
    def set_dirty(cls, credential_id: int) -> None:
        cls._set_flag(credential_id, "dirty", True)

    @classmethod
    def clear_dirty(cls, credential_id: int) -> None:
        cls._set_flag(credential_id, "dirty", False)

    @classmethod
    def set_dead(cls, credential_id: int) -> None:
        cls._set_flag(credential_id, "dead", True)

    @classmethod
    def clear_dead(cls, credential_id: int) -> None:
        cls._set_flag(credential_id, "dead", False)
