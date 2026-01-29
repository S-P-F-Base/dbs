from queue import Queue

from ..base_db import BaseDB, SQLTask, TableSpec


class CommerceServicesDB(BaseDB):
    _db_name = "commerce_services_db"

    _worker_started: bool = False
    _queue = Queue()

    TABLE = TableSpec(
        name="commerce_services_db",
        columns=[
            "uid INTEGER PRIMARY KEY AUTOINCREMENT",  # uuid
            "name TEXT NOT NULL",  # имя
            "desc TEXT NOT NULL",  # описание
            "price TEXT NOT NULL",  # цена (ибо float привет передавало)
            "discount TEXT NOT NULL",  # скидка (ибо float привет передавало)
            "discount_end_time INTEGER NOT NULL",  # когда скидка закончится
            "time_of_create INTEGER NOT NULL",  # когда создано
        ],
    )

    @classmethod
    def set_up(cls) -> None:
        cls._init_from_spec(cls.TABLE)
