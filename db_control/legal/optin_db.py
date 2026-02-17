from typing import Any

from ..base_db import BaseDB, TableSpec


class OptinDB(BaseDB):
    _db_name = "optin_db"

    TABLE = TableSpec(
        name="optin_db",
        columns=[
            "cid INTEGER PRIMARY KEY",  # credential.id
            "data BLOB NOT NULL",  # blob json
        ],
    )

    @classmethod
    def set_up(cls) -> None:
        cls._init_from_spec(cls.TABLE)

    @classmethod
    def create(
        cls,
        cid: int,
        data: dict[str, Any] | None = None,
    ) -> None:
        cls._insert(
            cid=(cid, int),
            data=(data or {}, dict),
        )

    @classmethod
    def update(
        cls,
        cid: int,
        *,
        data: dict[str, Any] | None = None,
    ) -> None:
        if data is None:
            return

        cls._update(
            where=("cid", cid),
            data=(data, dict),
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
                "data": dict,
            },
        )
