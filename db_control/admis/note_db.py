from typing import Any

from ..base_db import BaseDB, TableSpec


class NoteDB(BaseDB):
    _db_name = "note_db"

    TABLE = TableSpec(
        name="note_db",
        columns=[
            "uid INTEGER PRIMARY KEY AUTOINCREMENT",  # uuid
            "cid INTEGER NOT NULL",  # credential.cid
            "type TEXT NOT NULL",  # тип
            "msg TEXT NOT NULL",  # строка описания
        ],
        indexes=[
            "CREATE INDEX IF NOT EXISTS idx_player_char_db_id ON note_db (cid);",
        ],
    )

    @classmethod
    def set_up(cls) -> None:
        cls._init_from_spec(cls.TABLE)

    @classmethod
    def create(
        cls,
        cid: int,
        type: str,
        msg: str,
    ) -> None:
        cls._insert(
            cid=(cid, int),
            type=(type, str),
            msg=(msg, str),
        )

    @classmethod
    def update(
        cls,
        uid: int,
        *,
        type: str | None = None,
        msg: str | None = None,
    ) -> None:
        cols = {}

        if type is not None:
            cols["type"] = (type, str)

        if msg is not None:
            cols["msg"] = (msg, str)

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
                "cid": int,
                "type": str,
                "msg": str,
            },
        )

    @classmethod
    def list_by_owner(cls, cid: int) -> list[dict[str, Any]]:
        return cls._list(
            where=("cid", cid),
            order_by="uid",
            fields={
                "uid": int,
                "cid": int,
                "type": str,
                "msg": str,
            },
        )
