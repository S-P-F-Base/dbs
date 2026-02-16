from typing import Any

from ..base_db import BaseDB, SQLTask, TableSpec


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
        cls.write(
            SQLTask(
                """
                INSERT INTO perma_limit (cid, char_slot, lore_char_slot, weight_bytes)
                VALUES (?, ?, ?, ?)
                """,
                (cid, char_slot, lore_char_slot, weight_bytes),
            )
        )

    @classmethod
    def update(
        cls,
        cid: int,
        char_slot: int | None = None,
        lore_char_slot: int | None = None,
        weight_bytes: int | None = None,
    ) -> None:
        fields = []
        params: list[Any] = []

        if char_slot is not None:
            fields.append("char_slot = ?")
            params.append(char_slot)

        if lore_char_slot is not None:
            fields.append("lore_char_slot = ?")
            params.append(lore_char_slot)

        if weight_bytes is not None:
            fields.append("weight_bytes = ?")
            params.append(weight_bytes)

        if not fields:
            return

        params.append(cid)

        cls.write(
            SQLTask(
                f"""
                UPDATE perma_limit
                SET {", ".join(fields)}
                WHERE cid = ?
                """,
                tuple(params),
            )
        )

    @classmethod
    def delete(cls, cid: int) -> None:
        cls.write(SQLTask("DELETE FROM perma_limit WHERE cid = ?", (cid,)))

    @classmethod
    def get(cls, cid: int) -> dict[str, Any] | None:
        with cls.read() as conn:
            cur = conn.execute(
                """
                SELECT cid, char_slot, lore_char_slot, weight_bytes
                FROM perma_limit
                WHERE cid = ?
                """,
                (cid,),
            )
            row = cur.fetchone()

        if row is None:
            return None

        return {
            "cid": row[0],
            "char_slot": row[1],
            "lore_char_slot": row[2],
            "weight_bytes": row[3],
        }
