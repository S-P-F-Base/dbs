from typing import Any, Literal

from ..base_db import BaseDB, TableSpec

LoreCharStatus = Literal[
    "free",  # Свободен
    "taken",  # Занят
    "npb",  # Требуется отыграть на другом лорнике чтобы взять этого
    "block",  # Заблокирован
]


class LoreCharRegistryDB(BaseDB):
    _db_name = "lore_char_registry"

    TABLE = TableSpec(
        name="lore_char_registry",
        columns=[
            "uid INTEGER PRIMARY KEY AUTOINCREMENT",  # uuid
            "name TEXT NOT NULL",  # имя
            "status TEXT NOT NULL",  # статус
            "cid INTEGER",  # credential.id
            "game_db_id INTEGER",  # Пока что nill
            "wiki_url TEXT",  # Ссылка на вики персонажа
        ],
    )

    @classmethod
    def set_up(cls) -> None:
        cls._init_from_spec(cls.TABLE)

    @classmethod
    def create(
        cls,
        name: str,
        status: LoreCharStatus,
        cid: int | None = None,
        game_db_id: int | None = None,
        wiki_url: str | None = None,
    ) -> None:
        cls._insert(
            name=(name, str),
            status=(status, str),
            cid=(cid, int),
            game_db_id=(game_db_id, int),
            wiki_url=(wiki_url, str),
        )

    @classmethod
    def update(
        cls,
        uid: int,
        *,
        name: str | None = None,
        status: LoreCharStatus | None = None,
        cid: int | None = None,
        game_db_id: int | None = None,
        wiki_url: str | None = None,
    ) -> None:
        cols = {}

        if name is not None:
            cols["name"] = (name, str)

        if status is not None:
            cols["status"] = (status, str)

        if cid is not None:
            cols["cid"] = (cid, int)

        if game_db_id is not None:
            cols["game_db_id"] = (game_db_id, int)

        if wiki_url is not None:
            cols["wiki_url"] = (wiki_url, str)

        if not cols:
            return

        cls._update(
            where=("uid", uid),
            **cols,
        )

    @classmethod
    def delete(cls, uid: int) -> None:
        cls._delete(where=("uid", uid))

    @classmethod
    def get(cls, uid: int) -> dict[str, Any] | None:
        return cls._get(
            where=("uid", uid),
            fields={
                "uid": int,
                "name": str,
                "status": str,
                "cid": int,
                "game_db_id": int,
                "wiki_url": str,
            },
        )

    @classmethod
    def list_by_status(cls, status: LoreCharStatus) -> list[dict[str, Any]]:
        return cls._list(
            where=("status", status),
            order_by="uid",
            fields={
                "uid": int,
                "name": str,
                "status": str,
                "cid": int,
                "game_db_id": int,
                "wiki_url": str,
            },
        )

    @classmethod
    def list_by_owner(cls, cid: int) -> list[dict[str, Any]]:
        return cls._list(
            where=("cid", cid),
            order_by="uid",
            fields={
                "uid": int,
                "name": str,
                "status": str,
                "cid": int,
                "game_db_id": int,
                "wiki_url": str,
            },
        )

    @classmethod
    def list_all(cls) -> list[dict[str, Any]]:
        return cls._list(
            order_by="uid",
            fields={
                "uid": int,
                "name": str,
                "status": str,
                "cid": int,
                "game_db_id": int,
                "wiki_url": str,
            },
        )
