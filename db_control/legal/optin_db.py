from queue import Queue

from ..base_db import BaseDB, TableSpec


class OptinDB(BaseDB):
    _db_name = "optin_db"

    _worker_started: bool = False
    _queue = Queue()

    TABLE = TableSpec(
        name="optin_db",
        columns=[
            "cid INTEGER PRIMARY KEY",  # credential.id
            "data BLOB NOT NULL",  # blob json
        ],
    )

    @classmethod
    def set_up(cls) -> None:
        cls._init_from_spec(cls.TABLE)
