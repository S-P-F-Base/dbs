from queue import Queue
from typing import Literal

from ..base_db import BaseDB, SQLTask, TableSpec

LoreCharStatus = Literal[
    "free",  # Свободен
    "taken",  # Занят
    "npb",  # Требуется отыграть на другом лорнике чтобы взять этого
    "block",  # Заблокирован
]


class LoreCharRegistryDB(BaseDB):
    _db_name = "lore_char_registry"

    _worker_started: bool = False
    _queue = Queue()

    TABLE = TableSpec(
        name="lore_char_registry",
        columns=[
            "uid INTEGER PRIMARY KEY AUTOINCREMENT",  # uuid
            "name TEXT NOT NULL",  # имя
            "status TEXT NOT NULL",  # статус
            "cid INTEGER",  # credential.id
            "game_db_id INTEGER",  # Пока что nill
            "wiki_url TEXT",  # Ссылка на вики персонажа
        ],
    )

    @classmethod
    def set_up(cls) -> None:
        cls._init_from_spec(cls.TABLE)
