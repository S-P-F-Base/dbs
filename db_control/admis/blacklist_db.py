from ..base_db import BaseDB, TableSpec


class BlacklistDB(BaseDB):
    _db_name = "blacklist_db"

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
