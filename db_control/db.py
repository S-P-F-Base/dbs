from pathlib import Path

import dataset


class DB:
    _base_dir = Path(__file__).parents[1] / "data"
    _db_path = _base_dir / "app.db"

    @classmethod
    def init(cls) -> None:
        cls._base_dir.mkdir(parents=True, exist_ok=True)
        cls._main = dataset.connect(f"sqlite:///{cls._db_path}?timeout=5")
        cls._init_schema()

    @classmethod
    def _init_schema(cls) -> None:  # TODO: make all shemas
        cls._main.query("""\
            CREATE TABLE IF NOT EXISTS credentials (
                id INTEGER PRIMARY KEY AUTOINCREMENT
            )
        """)

    @classmethod
    def get_db(cls):
        return cls._main
