from queue import Queue
from typing import Literal

from ..base_db import BaseDB, SQLTask

LoreCharStatus = Literal["free", "taken", "npb", "block"]


class LoreCharRegistryDB(BaseDB):
    _db_name = "lore_char_registry"

    _worker_started: bool = False
    _queue = Queue()

    @classmethod
    def set_up(cls) -> None:
        sql_t = [
            SQLTask(
                """
                CREATE TABLE IF NOT EXISTS lore_char_registry (
                    name TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    who_pick INTEGER, 
                    game_db_id INTEGER,
                    wiki_url TEXT
                );
                """
            ),
        ]
        super()._init_db(sql_t)

    # TODO: methods
