import json
from queue import Queue
from typing import Any

from ..base_db import BaseDB, SQLTask, TableSpec


class AccessDB(BaseDB):
    _db_name = "access_db"

    _worker_started: bool = False
    _queue = Queue()

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
        version: int = 0,
        access: dict[str, bool] | None = None,
    ) -> None:
        payload = json.dumps(access or {}, ensure_ascii=False)

        cls.submit_write(
            SQLTask(
                """
                INSERT INTO access_db (cid, version, data)
                VALUES (?, ?, ?)
                """,
                (cid, version, payload),
            )
        )

    @classmethod
    def update(
        cls,
        cid: int,
        version: int | None = None,
        access: dict[str, bool] | None = None,
    ) -> None:
        fields = []
        params: list[Any] = []

        if version is not None:
            fields.append("version = ?")
            params.append(version)

        if access is not None:
            fields.append("data = ?")
            params.append(json.dumps(access, ensure_ascii=False))

        if not fields:
            return

        params.append(cid)

        cls.submit_write(
            SQLTask(
                f"""
                UPDATE access_db
                SET {", ".join(fields)}
                WHERE cid = ?
                """,
                tuple(params),
            )
        )

    @classmethod
    def delete(cls, cid: int) -> None:
        cls.submit_write(SQLTask("DELETE FROM access_db WHERE cid = ?", (cid,)))

    @classmethod
    def get(cls, cid: int) -> dict[str, Any] | None:
        with cls.read() as conn:
            cur = conn.execute(
                """
                SELECT cid, version, data
                FROM access_db
                WHERE cid = ?
                """,
                (cid,),
            )
            row = cur.fetchone()

        if row is None:
            return None

        try:
            access_data = json.loads(row[2])

        except Exception:
            access_data = {}

        return {
            "cid": row[0],
            "version": row[1],
            "access": access_data,
        }

    @classmethod
    def get_by_version(
        cls,
        version: int = 0,
    ) -> list[dict[str, Any]]:
        with cls.read() as conn:
            cur = conn.execute(
                """
                SELECT cid, version, data
                FROM access_db
                WHERE version = ?
                """,
                (version,),
            )
            rows = cur.fetchall()

        out: list[dict[str, Any]] = []

        for id_, ver, raw_access in rows:
            try:
                access_data = json.loads(raw_access)

            except Exception:
                access_data = {}

            out.append(
                {
                    "cid": id_,
                    "version": ver,
                    "access": access_data,
                }
            )

        return out
