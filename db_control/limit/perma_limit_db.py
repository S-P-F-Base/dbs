from typing import Any

from ..base_db import BaseDB, TableSpec


class PermaLimitDB(BaseDB):
    _db_name = "perma_limit"

    TABLE = TableSpec(
        name="perma_limit",
        columns=[
            "cid INTEGER PRIMARY KEY",  # credential.id
            "char_slot INTEGER NOT NULL DEFAULT 0",  # количество обычных слотов
            "lore_char_slot INTEGER NOT NULL DEFAULT 0",  # количество лорных слотов
            "weight_bytes INTEGER NOT NULL DEFAULT 0",  # байтики доступные
        ],
    )

    @classmethod
    def set_up(cls) -> None:
        cls._init_from_spec(cls.TABLE)

    @classmethod
    def create(
        cls,
        cid: int,
        char_slot: int = 0,
        lore_char_slot: int = 0,
        weight_bytes: int = 0,
    ) -> None:
        cls._insert(
            cid=(cid, int),
            char_slot=(char_slot, int),
            lore_char_slot=(lore_char_slot, int),
            weight_bytes=(weight_bytes, int),
        )

    @classmethod
    def update(
        cls,
        cid: int,
        char_slot: int | None = None,
        lore_char_slot: int | None = None,
        weight_bytes: int | None = None,
    ) -> None:
        cols = {}

        if char_slot is not None:
            cols["char_slot"] = (char_slot, int)

        if lore_char_slot is not None:
            cols["lore_char_slot"] = (lore_char_slot, int)

        if weight_bytes is not None:
            cols["weight_bytes"] = (weight_bytes, int)

        if not cols:
            return

        cls._update(
            where=("cid", cid),
            **cols,
        )

    @classmethod
    def delete(cls, cid: int) -> None:
        cls._delete(where=("cid", cid))

    @classmethod
    def get(cls, cid: int) -> dict[str, Any] | None:
        return cls._get(
            where=("cid", cid),
            fields={
                "cid": int,
                "char_slot": int,
                "lore_char_slot": int,
                "weight_bytes": int,
            },
        )
