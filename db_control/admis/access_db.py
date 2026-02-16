import json
from typing import Any

from ..base_db import BaseDB, TableSpec


class AccessDB(BaseDB):
    _db_name = "access_db"

    TABLE = TableSpec(
        name="access_db",
        columns=[
            "cid INTEGER PRIMARY KEY",  # credential.cid
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
            data=(access or {}, json),
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
            cols["data"] = (access, json)

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
                "data": json,
            },
        )

    @classmethod
    def get_by_version(cls, version: int) -> list[dict[str, Any]]:
        with cls.read() as conn:
            cur = conn.execute(
                "SELECT cid, version, data FROM access_db WHERE version = ?",
                (version,),
            )
            rows = cur.fetchall()

        return [
            {
                "cid": cid,
                "version": ver,
                "access": json.loads(raw),
            }
            for cid, ver, raw in rows
        ]
