from pathlib import Path

import dataset


class DB:
    _main: dataset.Database = None  # pyright: ignore[reportAssignmentType]

    @classmethod
    def init(cls) -> None:
        if cls._main is None:
            db_path = Path(__file__).parents[1] / "data" / "app.db"
            db_path.parent.mkdir(exist_ok=True)
            cls._main = dataset.connect(f"sqlite:///{db_path}?timeout=5")

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
