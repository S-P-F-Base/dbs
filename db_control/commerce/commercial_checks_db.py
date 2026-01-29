from queue import Queue

from ..base_db import BaseDB, SQLTask, TableSpec


class CommercialChecksDB(BaseDB):
    _db_name = "commercial_checks_db"

    _worker_started: bool = False
    _queue = Queue()

    TABLE = TableSpec(
        name="commercial_checks_db",
        columns=[
            "uid INTEGER PRIMARY KEY AUTOINCREMENT",  # uuid
            "cid INTEGER NOT NULL",  # credential.id
            "csid INTEGER NOT NULL",  # commerce_services_db.id
            "tax_id TEXT",  # айди от налоговой
            "status TEXT NOT NULL",  # status
            "timestamp INTEGER NOT NULL",  # дата обноления последнего данного сервиса (обычно это будет когда статус последний раз изменился)
            "snap BLOB NOT NULL",  # json blob
        ],
    )

    @classmethod
    def set_up(cls) -> None:
        cls._init_from_spec(cls.TABLE)
