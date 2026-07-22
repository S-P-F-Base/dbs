import dataset
from sqlalchemy import text


class DataBase:
    obj = dataset.connect("sqlite:///main.db")

    @classmethod
    def init(cls) -> None:
        cls.obj.executable.execute(
            text("""\
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    login TEXT UNIQUE,
                    password_hash BLOB
                )
            """)
        )
