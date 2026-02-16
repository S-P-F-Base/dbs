from ..base_db import BaseDB, TableSpec


class ForgetmeDB(BaseDB):
    _db_name = "forgetme_db"

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
