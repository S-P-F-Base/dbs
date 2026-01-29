from queue import Queue

from ..base_db import BaseDB, SQLTask, TableSpec


class ForgetmeDB(BaseDB):
    _db_name = "forgetme_db"

    _worker_started: bool = False
    _queue = Queue()

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
