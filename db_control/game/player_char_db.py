import json
from queue import Queue
from typing import Any, Literal

from ..base_db import BaseDB, SQLTask, TableSpec

PlayerCharType = Literal["lore", "norm"]


class PlayerCharDB(BaseDB):
    _db_name = "player_char_db"

    _worker_started: bool = False
    _queue = Queue()

    TABLE = TableSpec(
        name="player_char_db",
        columns=[
            "uid INTEGER PRIMARY KEY AUTOINCREMENT",  # uuid
            "cid INTEGER NOT NULL",  # credential.id
            "name TEXT NOT NULL",  # имя персонажа
            "discord_url TEXT",  # discord url
            "char_type TEXT NOT NULL",  # тип персонажа
            "content_ids BLOB NOT NULL",  # айдишки контента к этому персонажу
            "game_db_id INTEGER",  # Пока что nill
        ],
        indexes=[
            "CREATE INDEX IF NOT EXISTS idx_player_char_db_id ON player_char_db (cid);",
        ],
    )

    @classmethod
    def set_up(cls) -> None:
        cls._init_from_spec(cls.TABLE)

    @classmethod
    def create(
        cls,
        cid: int,
        name: str,
        char_type: PlayerCharType,
        content_ids: list[str],
        discord_url: str | None = None,
        game_db_id: int | None = None,
    ) -> None:
        payload = json.dumps(content_ids, ensure_ascii=False)

        cls.submit_write(
            SQLTask(
                """
                INSERT INTO player_char_db
                (cid, name, discord_url, char_type, content_ids, game_db_id)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (cid, name, discord_url, char_type, payload, game_db_id),
            )
        )

    @classmethod
    def update(
        cls,
        uid: int,
        name: str | None = None,
        discord_url: str | None = None,
        char_type: PlayerCharType | None = None,
        content_ids: list[str] | None = None,
        game_db_id: int | None = None,
    ) -> None:
        fields = []
        params: list[Any] = []

        if name is not None:
            fields.append("name = ?")
            params.append(name)

        if discord_url is not None:
            fields.append("discord_url = ?")
            params.append(discord_url)

        if char_type is not None:
            fields.append("char_type = ?")
            params.append(char_type)

        if content_ids is not None:
            fields.append("content_ids = ?")
            params.append(json.dumps(content_ids, ensure_ascii=False))

        if game_db_id is not None:
            fields.append("game_db_id = ?")
            params.append(game_db_id)

        if not fields:
            return

        params.append(uid)

        cls.submit_write(
            SQLTask(
                f"""
                UPDATE player_char_db
                SET {", ".join(fields)}
                WHERE uid = ?
                """,
                tuple(params),
            )
        )

    @classmethod
    def delete(cls, uid: int) -> None:
        cls.submit_write(SQLTask("DELETE FROM player_char_db WHERE uid = ?", (uid,)))

    @classmethod
    def get(cls, uid: int) -> dict[str, Any] | None:
        with cls.read() as conn:
            cur = conn.execute(
                """
                SELECT uid, cid, name, discord_url, char_type, content_ids, game_db_id
                FROM player_char_db
                WHERE uid = ?
                """,
                (uid,),
            )
            row = cur.fetchone()

        if row is None:
            return None

        try:
            content_ids = json.loads(row[5])

        except Exception:
            content_ids = []

        return {
            "uid": row[0],
            "cid": row[1],
            "name": row[2],
            "discord_url": row[3],
            "char_type": row[4],
            "content_ids": content_ids,
            "game_db_id": row[6],
        }

    @classmethod
    def list_by_owner(cls, cid: int) -> list[dict[str, Any]]:
        with cls.read() as conn:
            cur = conn.execute(
                """
                SELECT uid, cid, name, discord_url, char_type, content_ids, game_db_id
                FROM player_char_db
                WHERE cid = ?
                ORDER BY uid
                """,
                (cid,),
            )
            rows = cur.fetchall()

        out: list[dict[str, Any]] = []

        for row in rows:
            try:
                content_ids = json.loads(row[5])

            except Exception:
                content_ids = []

            out.append(
                {
                    "uid": row[0],
                    "cid": row[1],
                    "name": row[2],
                    "discord_url": row[3],
                    "char_type": row[4],
                    "content_ids": content_ids,
                    "game_db_id": row[6],
                }
            )

        return out
