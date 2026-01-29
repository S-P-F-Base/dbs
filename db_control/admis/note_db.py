from queue import Queue

from ..base_db import BaseDB, SQLTask, TableSpec


class NoteDB(BaseDB):
    _db_name = "note_db"

    _worker_started: bool = False
    _queue = Queue()

    TABLE = TableSpec(
        name="note_db",
        columns=[
            "uid INTEGER PRIMARY KEY AUTOINCREMENT",  # uuid
            "cid INTEGER NOT NULL",  # credential.cid
            "type TEXT NOT NULL",  # тип
            "msg TEXT NOT NULL",  # строка описания
        ],
        indexes=[
            "CREATE INDEX IF NOT EXISTS idx_player_char_db_id ON note_db (cid);",
        ],
    )

    @classmethod
    def set_up(cls) -> None:
        cls._init_from_spec(cls.TABLE)
