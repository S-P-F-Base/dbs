from typing import Any

from ..base_db import BaseDB, TableSpec


class AccessDB(BaseDB):
    _db_name = "access_db"

    TABLE = TableSpec(
        name="access_db",
        columns=[
            "cid INTEGER PRIMARY KEY",  # credential.cid
            "version INTEGER NOT NULL DEFAULT 0",
            "data BLOB NOT NULL",  # json blob
        ],
    )

    @classmethod
    def set_up(cls) -> None:
        cls._init_from_spec(cls.TABLE)

    @classmethod
    def create(
        cls,
        cid: int,
        access: dict[str, bool] | None = None,
        version: int = 0,
    ) -> None:
        cls._insert(
            cid=(cid, int),
            version=(version, int),
            data=(access or {}, dict),
        )

    @classmethod
    def update(
        cls,
        cid: int,
        *,
        access: dict[str, bool] | None = None,
        version: int | None = None,
    ) -> None:
        cols = {}

        if version is not None:
            cols["version"] = (version, int)

        if access is not None:
            cols["data"] = (access, dict)

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
                "version": int,
                "data": dict,
            },
        )

    @classmethod
    def get_by_version(cls, version: int) -> list[dict[str, Any]]:
        rows = cls._list(
            where=("version", version),
            order_by="cid",
            fields={
                "cid": int,
                "version": int,
                "data": dict,
            },
        )

        return [
            {
                "cid": row["cid"],
                "version": row["version"],
                "access": row["data"],
            }
            for row in rows
        ]
