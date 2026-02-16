import time
from typing import Any, Literal

from ..base_db import BaseDB, SQLTask, TableSpec

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

    @classmethod
    def create(
        cls,
        cid: int,
        char_slot: int,
        weight_bytes: int,
        expired: int,
        status: TimedLimitStatus = "active",
    ) -> None:
        cls.write(
            SQLTask(
                """
                INSERT INTO timed_limit
                (cid, char_slot, weight_bytes, expired, status)
                VALUES (?, ?, ?, ?, ?)
                """,
                (cid, char_slot, weight_bytes, expired, status),
            )
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
        fields = []
        params: list[Any] = []

        if char_slot is not None:
            fields.append("char_slot = ?")
            params.append(char_slot)

        if weight_bytes is not None:
            fields.append("weight_bytes = ?")
            params.append(weight_bytes)

        if expired is not None:
            fields.append("expired = ?")
            params.append(expired)

        if status is not None:
            fields.append("status = ?")
            params.append(status)

        if not fields:
            return

        params.append(uid)

        cls.write(
            SQLTask(
                f"""
                UPDATE timed_limit
                SET {", ".join(fields)}
                WHERE uid = ?
                """,
                tuple(params),
            )
        )

    @classmethod
    def delete(cls, uid: int) -> None:
        cls.write(SQLTask("DELETE FROM timed_limit WHERE uid = ?", (uid,)))

    @classmethod
    def get(cls, uid: int) -> dict[str, Any] | None:
        with cls.read() as conn:
            cur = conn.execute(
                """
                SELECT uid, cid, char_slot, weight_bytes, expired, status
                FROM timed_limit
                WHERE uid = ?
                """,
                (uid,),
            )
            row = cur.fetchone()

        if row is None:
            return None

        return {
            "uid": row[0],
            "cid": row[1],
            "char_slot": row[2],
            "weight_bytes": row[3],
            "expired": row[4],
            "status": row[5],
        }

    @classmethod
    def list_by_owner(cls, cid: int) -> list[dict[str, Any]]:
        with cls.read() as conn:
            cur = conn.execute(
                """
                SELECT uid, cid, char_slot, weight_bytes, expired, status
                FROM timed_limit
                WHERE cid = ?
                ORDER BY expired
                """,
                (cid,),
            )
            rows = cur.fetchall()

        return [
            {
                "uid": row[0],
                "cid": row[1],
                "char_slot": row[2],
                "weight_bytes": row[3],
                "expired": row[4],
                "status": row[5],
            }
            for row in rows
        ]

    @classmethod
    def list_active(
        cls,
        cid: int,
        now: int | None = None,
    ) -> list[dict[str, Any]]:
        now = now or int(time.time())

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

        return [
            {
                "uid": row[0],
                "cid": row[1],
                "char_slot": row[2],
                "weight_bytes": row[3],
                "expired": row[4],
                "status": row[5],
            }
            for row in rows
        ]
