from ..base_db import BaseDB, TableSpec


class LimitDB(BaseDB):
    _db_name = "limit"

    TABLE = TableSpec(
        name="limit",
        columns=[
            "uid INTEGER PRIMARY KEY AUTOINCREMENT",  # uuid
            "cid INTEGER PRIMARY KEY",  # credential.id
            # TODO: Сделать уже нормальный блок с лимитами а не вон то говно что сейчас
        ],
    )

    @classmethod
    def set_up(cls) -> None:
        cls._init_from_spec(cls.TABLE)
