from typing import Any, Final, Literal

from ..base_db import BaseDB, TableSpec

LimitStatus = Literal["normal", "canceled", "revoked", "expired"]


class LimitDB(BaseDB):
    _db_name = "limit_db"

    _FIELDS: Final[dict[str, type]] = {
        "uid": int,
        "cid": int,
        "title": str,
        "description": str,
        "weight_bytes_add": int,
        "char_slots_add": int,
        "lore_slots_add": int,
        "expires_at": int,
        "status": str,
    }

    TABLE = TableSpec(
        name="limit_db",
        columns=[
            "uid INTEGER PRIMARY KEY AUTOINCREMENT",  # uuid
            "cid INTEGER NOT NULL",  # credential.id
            "title TEXT NOT NULL",  # short title
            "description TEXT",  # long description
            "weight_bytes_add INTEGER NOT NULL DEFAULT 0",
            "char_slots_add INTEGER NOT NULL DEFAULT 0",
            "lore_slots_add INTEGER NOT NULL DEFAULT 0",
            "expires_at INTEGER",  # unix timestamp when limit expires
            "status TEXT NOT NULL DEFAULT 'normal'",
        ],
        indexes=[
            "CREATE INDEX IF NOT EXISTS idx_limit_db_cid ON limit_db (cid);",
            "CREATE INDEX IF NOT EXISTS idx_limit_db_status ON limit_db (status);",
        ],
    )

    @classmethod
    def set_up(cls) -> None:
        cls._init_from_spec(cls.TABLE)

    @classmethod
    def create(
        cls,
        cid: int,
        title: str,
        description: str | None = None,
        weight_bytes_add: int = 0,
        char_slots_add: int = 0,
        lore_slots_add: int = 0,
        expires_at: int | None = None,
        status: LimitStatus = "normal",
    ) -> int:
        return cls._insert(
            cid=(cid, int),
            title=(title, str),
            description=(description, str),
            weight_bytes_add=(weight_bytes_add, int),
            char_slots_add=(char_slots_add, int),
            lore_slots_add=(lore_slots_add, int),
            expires_at=(expires_at, int),
            status=(status, str),
        )

    @classmethod
    def update(
        cls,
        uid: int,
        *,
        title: str | None = None,
        description: str | None = None,
        weight_bytes_add: int | None = None,
        char_slots_add: int | None = None,
        lore_slots_add: int | None = None,
        expires_at: int | None = None,
        status: LimitStatus | None = None,
    ) -> None:
        cols: dict[str, tuple[object, type]] = {}

        if title is not None:
            cols["title"] = (title, str)

        if description is not None:
            cols["description"] = (description, str)

        if weight_bytes_add is not None:
            cols["weight_bytes_add"] = (weight_bytes_add, int)

        if char_slots_add is not None:
            cols["char_slots_add"] = (char_slots_add, int)

        if lore_slots_add is not None:
            cols["lore_slots_add"] = (lore_slots_add, int)

        if expires_at is not None:
            cols["expires_at"] = (expires_at, int)

        if status is not None:
            cols["status"] = (status, str)

        if not cols:
            return

        cls._update(
            where=("uid", uid),
            **cols,
        )

    @classmethod
    def clear_expiration(cls, uid: int) -> None:
        cls._update(
            where=("uid", uid),
            expires_at=(None, int),
        )

    @classmethod
    def set_status(cls, uid: int, status: LimitStatus) -> None:
        cls._update(
            where=("uid", uid),
            status=(status, str),
        )

    @classmethod
    def set_canceled(cls, uid: int) -> None:
        cls.set_status(uid, "canceled")

    @classmethod
    def set_revoked(cls, uid: int) -> None:
        cls.set_status(uid, "revoked")

    @classmethod
    def set_expired(cls, uid: int) -> None:
        cls.set_status(uid, "expired")

    @classmethod
    def set_normal(cls, uid: int) -> None:
        cls.set_status(uid, "normal")

    @classmethod
    def delete(cls, uid: int) -> None:
        cls._delete(where=("uid", uid))

    @classmethod
    def get(cls, uid: int) -> dict[str, Any] | None:
        return cls._get(
            where=("uid", uid),
            fields=cls._FIELDS,
        )

    @classmethod
    def list_by_owner(cls, cid: int) -> list[dict[str, Any]]:
        return cls._list(
            where=("cid", cid),
            order_by="uid DESC",
            fields=cls._FIELDS,
        )
