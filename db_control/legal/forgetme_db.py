import time
from typing import Any

from ..base_db import BaseDB, TableSpec


class ForgetmeDB(BaseDB):
    _db_name = "forgetme_db"

    TABLE = TableSpec(
        name="forgetme_db",
        columns=[
            "discord_id INTEGER PRIMARY KEY",  # дискорд айди
            "timestamp INTEGER NOT NULL",  # время попадания в эту бд
        ],
    )

    @classmethod
    def set_up(cls) -> None:
        cls._init_from_spec(cls.TABLE)

    @classmethod
    def create(
        cls,
        discord_id: int,
        timestamp: int | None = None,
    ) -> None:
        if timestamp is None:
            timestamp = int(time.time())

        cls._insert(
            discord_id=(discord_id, int),
            timestamp=(timestamp, int),
        )

    @classmethod
    def update(
        cls,
        discord_id: int,
        *,
        timestamp: int | None = None,
    ) -> None:
        if timestamp is None:
            timestamp = int(time.time())

        cls._update(
            where=("discord_id", discord_id),
            timestamp=(timestamp, int),
        )

    @classmethod
    def delete(cls, discord_id: int) -> None:
        cls._delete(where=("discord_id", discord_id))

    @classmethod
    def get(cls, discord_id: int) -> dict[str, Any] | None:
        return cls._get(
            where=("discord_id", discord_id),
            fields={
                "discord_id": int,
                "timestamp": int,
            },
        )

    @classmethod
    def list_since(cls, ts: int) -> list[dict[str, Any]]:
        with cls.read() as conn:
            cur = conn.execute(
                """
                SELECT discord_id, timestamp
                FROM forgetme_db
                WHERE timestamp >= ?
                ORDER BY timestamp
                """,
                (ts,),
            )
            rows = cur.fetchall()

        return [
            {
                "discord_id": row[0],
                "timestamp": row[1],
            }
            for row in rows
        ]
