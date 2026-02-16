from ..base_db import BaseDB, TableSpec


class CustomizationDB(BaseDB):
    _db_name = "customization_db"

    TABLE = TableSpec(
        name="customization_db",
        columns=[
            "cid INTEGER PRIMARY KEY",  # credential.id
            "name TEXT",  # имя отображаемое на сайте
            "path_to_image TEXT",  # путь до кастомной иконки
        ],
    )

    @classmethod
    def set_up(cls) -> None:
        cls._init_from_spec(cls.TABLE)
