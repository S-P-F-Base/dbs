import dataset
from sqlalchemy import text


class DataBase:
    obj = dataset.connect("sqlite:///main.db")
    profiles: dataset.Table
    sessions: dataset.Table

    @classmethod
    def init(cls) -> None:
        cls.obj.executable.execute(
            text("""\
                CREATE TABLE IF NOT EXISTS profiles (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    login TEXT UNIQUE,
                    password_hash BLOB
                )
            """)
        )

        cls.obj.executable.execute(
            text("""\
                CREATE TABLE IF NOT EXISTS sessions (
                    token TEXT PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)
        )

        cls.profiles = cls.obj["profiles"]
        cls.sessions = cls.obj["sessions"]
