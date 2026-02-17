from typing import Any, Literal

from ..base_db import BaseDB, TableSpec

PlayerCharType = Literal["lore", "norm"]


class PlayerCharDB(BaseDB):
    _db_name = "player_char_db"

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
        cls._insert(
            cid=(cid, int),
            name=(name, str),
            discord_url=(discord_url, str),
            char_type=(char_type, str),
            content_ids=(content_ids, list),
            game_db_id=(game_db_id, int),
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
        cols = {}

        if name is not None:
            cols["name"] = (name, str)

        if discord_url is not None:
            cols["discord_url"] = (discord_url, str)

        if char_type is not None:
            cols["char_type"] = (char_type, str)

        if content_ids is not None:
            cols["content_ids"] = (content_ids, list)

        if game_db_id is not None:
            cols["game_db_id"] = (game_db_id, int)

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
                "name": str,
                "discord_url": str,
                "char_type": str,
                "content_ids": list,
                "game_db_id": int,
            },
        )

    @classmethod
    def list_by_owner(cls, cid: int) -> list[dict[str, Any]]:
        return cls._list(
            where=("cid", cid),
            order_by="uid",
            fields={
                "uid": int,
                "cid": int,
                "name": str,
                "discord_url": str,
                "char_type": str,
                "content_ids": list,
                "game_db_id": int,
            },
        )
