import time
from typing import Any, Literal

from ..base_db import BaseDB, TableSpec

TimedLimitStatus = Literal[
    "active",  # активно
    "expired",  # истекло
    "disabled",  # отменено
]


class TimedLimitDB(BaseDB):
    _db_name = "timed_limit"

    TABLE = TableSpec(
        name="timed_limit",
        columns=[
            "uid INTEGER PRIMARY KEY AUTOINCREMENT",  # uuid
            "cid INTEGER NOT NULL",  # credential.id
            "char_slot INTEGER NOT NULL DEFAULT 0",  # сколько слотов добавлено этой записью
            "weight_bytes INTEGER NOT NULL DEFAULT 0",  # сколько веса было добавлено
            "expired INTEGER NOT NULL",  # когда истечёт
            "status TEXT NOT NULL",  # статус
        ],
        indexes=[
            "CREATE INDEX IF NOT EXISTS idx_timed_limit_id ON timed_limit (cid);",
            "CREATE INDEX IF NOT EXISTS idx_timed_limit_expired ON timed_limit (expired);",
        ],
    )

    @classmethod
    def set_up(cls) -> None:
        cls._init_from_spec(cls.TABLE)

    @staticmethod
    def _row_to_dict(row: tuple[Any, ...]) -> dict[str, Any]:
        return {
            "uid": row[0],
            "cid": row[1],
            "char_slot": row[2],
            "weight_bytes": row[3],
            "expired": row[4],
            "status": row[5],
        }

    @classmethod
    def create(
        cls,
        cid: int,
        char_slot: int,
        weight_bytes: int,
        expired: int,
        status: TimedLimitStatus = "active",
    ) -> None:
        cls._insert(
            cid=(cid, int),
            char_slot=(char_slot, int),
            weight_bytes=(weight_bytes, int),
            expired=(expired, int),
            status=(status, str),
        )

    @classmethod
    def update(
        cls,
        uid: int,
        char_slot: int | None = None,
        weight_bytes: int | None = None,
        expired: int | None = None,
        status: TimedLimitStatus | None = None,
    ) -> None:
        cols = {}

        if char_slot is not None:
            cols["char_slot"] = (char_slot, int)

        if weight_bytes is not None:
            cols["weight_bytes"] = (weight_bytes, int)

        if expired is not None:
            cols["expired"] = (expired, int)

        if status is not None:
            cols["status"] = (status, str)

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
                "char_slot": int,
                "weight_bytes": int,
                "expired": int,
                "status": str,
            },
        )

    @classmethod
    def list_by_owner(cls, cid: int) -> list[dict[str, Any]]:
        return cls._list(
            where=("cid", cid),
            order_by="expired",
            fields={
                "uid": int,
                "cid": int,
                "char_slot": int,
                "weight_bytes": int,
                "expired": int,
                "status": str,
            },
        )

    @classmethod
    def list_active(
        cls,
        cid: int,
        now: int | None = None,
    ) -> list[dict[str, Any]]:
        if now is None:
            now = int(time.time())

        with cls.read() as conn:
            cur = conn.execute(
                """
                SELECT uid, cid, char_slot, weight_bytes, expired, status
                FROM timed_limit
                WHERE cid = ?
                  AND status = 'active'
                  AND expired > ?
                ORDER BY expired
                """,
                (cid, now),
            )
            rows = cur.fetchall()

        return [cls._row_to_dict(row) for row in rows]
