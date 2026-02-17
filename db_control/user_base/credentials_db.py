from typing import Any

from ..base_db import BaseDB, TableSpec


class CredentialsDB(BaseDB):
    _db_name = "credentials_db"

    TABLE = TableSpec(
        name="credentials_db",
        columns=[
            "id INTEGER PRIMARY KEY AUTOINCREMENT",  # credential.id (анкер поинт всех таблиц)
            "discord_id TEXT NOT NULL UNIQUE",  # дискорд айди. По нему идёт вся регистрация
            "steam64_id TEXT",  # стим айди чтобы проще было потом связывать игру и сайт
            "dirty INTEGER NOT NULL DEFAULT 1",  # статус синхранизации. Пока что все не синхонизированы
        ],
    )

    @classmethod
    def set_up(cls) -> None:
        cls._init_from_spec(cls.TABLE)

    @classmethod
    def create(cls, discord_id: str, steam64_id: str | None) -> None:
        cls._insert(
            discord_id=(discord_id, str),
            steam64_id=(steam64_id, str),
        )

    @classmethod
    def delete(cls, id: int) -> None:
        cls._delete(where=("id", id))

    @classmethod
    def update(
        cls,
        id: int,
        discord_id: str | None,
        steam64_id: str | None,
    ) -> None:
        cols = {}

        if discord_id is not None:
            cols["discord_id"] = (discord_id, str)

        if steam64_id is not None:
            cols["steam64_id"] = (steam64_id, str)

        if not cols:
            return

        cls._update(
            where=("id", id),
            **cols,
        )

    @classmethod
    def _get_by(cls, field: str, value: object) -> dict[str, Any] | None:
        return cls._get(
            where=(field, value),
            fields={
                "id": int,
                "discord_id": str,
                "steam64_id": str,
                "dirty": bool,
            },
        )

    @classmethod
    def get_by_id(cls, id: int) -> dict[str, Any] | None:
        return cls._get_by(field="id", value=id)

    @classmethod
    def get_by_discord(cls, discord_id: str) -> dict[str, Any] | None:
        return cls._get_by(field="discord_id", value=discord_id)

    @classmethod
    def get_by_steam(cls, steam64_id: str) -> dict[str, Any] | None:
        return cls._get_by(field="steam64_id", value=steam64_id)

    @classmethod
    def set_dirty(cls, id: int) -> None:
        cls._update(
            where=("id", id),
            dirty=(1, int),
        )

    @classmethod
    def clear_dirty(cls, id: int) -> None:
        cls._update(
            where=("id", id),
            dirty=(0, int),
        )
