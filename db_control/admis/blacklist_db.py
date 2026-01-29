from queue import Queue

from ..base_db import BaseDB, SQLTask, TableSpec


class BlacklistDB(BaseDB):
    _db_name = "blacklist_db"

    _worker_started: bool = False
    _queue = Queue()

    TABLE = TableSpec(
        name="blacklist_db",
        columns=[
            "cid INTEGER PRIMARY KEY",  # credential.cid
            "data BLOB NOT NULL",  # blob json
        ],
    )

    @classmethod
    def set_up(cls) -> None:
        cls._init_from_spec(cls.TABLE)
