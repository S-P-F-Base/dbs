from pathlib import Path
from sqlite3 import IntegrityError

import dataset
from dataset import OutRow


class CredentialsNotFoundError(Exception):
    def __init__(self, cid: int) -> None:
        self.cid = cid
        super().__init__(f"Credentials with {cid=} not found")


class DiscordIDCollision(Exception):
    def __init__(self, discord_id: str, cid: int | None = None) -> None:
        self.discord_id = discord_id
        self.cid = cid
        super().__init__(f"User with {discord_id=} already exists ({cid=})")


class SteamIDCollision(Exception):
    def __init__(self, steam_id: str, cid: int | None = None) -> None:
        self.steam_id = steam_id
        self.cid = cid
        super().__init__(f"User with {steam_id=} already exists ({cid=})")


class DB:
    _main: dataset.Database = None  # pyright: ignore[reportAssignmentType]

    @classmethod
    def init(cls) -> None:
        if cls._main is None:
            db_path = Path(__file__).parents[1] / "data" / "app.db"
            db_path.parent.mkdir(exist_ok=True)
            cls._main = dataset.connect(
                f"sqlite:///{db_path}?timeout=5",
                on_connect_statements=[
                    "PRAGMA foreign_keys = ON;",
                ],
            )

        cls._init_schema()

    @classmethod
    def _init_schema(cls) -> None:  # TODO: make all shemas
        # Таблица под основную информацию об юзере
        cls._main.query("""\
            CREATE TABLE IF NOT EXISTS credentials (
                cid INTEGER PRIMARY KEY AUTOINCREMENT,
                discord_id TEXT NOT NULL UNIQUE,
                steam_id TEXT UNIQUE,
                is_disabled INTEGER DEFAULT 0,
                disable_reason TEXT
            )
        """)

    @classmethod
    def create_user(cls, discord_id: str, steam_id: str | None = None) -> int:
        try:
            # region credentials setup
            cid = cls._main["credentials"].insert(
                {
                    "discord_id": discord_id,
                    "steam_id": steam_id,
                    "is_disabled": 0,
                    "disable_reason": None,
                }
            )
            # endregion

            return cid

        except IntegrityError as e:
            str_e = str(e)
            if "credentials.discord_id" in str_e:
                existing = cls._main["credentials"].find_one(discord_id=discord_id)
                raise DiscordIDCollision(
                    discord_id, cid=existing["cid"] if existing else None
                )

            elif "credentials.steam_id" in str_e:
                # В данном случае у нас 100% есть steamid, но пайланс так не считает
                assert steam_id is not None, "Unattainable"
                existing = cls._main["credentials"].find_one(steam_id=steam_id)
                raise SteamIDCollision(
                    steam_id, cid=existing["cid"] if existing else None
                )

            raise e

    @classmethod
    def get_user_cred(cls, cid: int) -> OutRow:
        existing = cls._main["credentials"].find_one(cid=cid)
        if not existing:
            raise CredentialsNotFoundError(cid)

        return existing

    @classmethod
    def disable_user(cls, cid: int, reason: str) -> None:
        cls.get_user_cred(cid)

        cls._main["credentials"].update(
            {"cid": cid, "is_disabled": 1, "disable_reason": reason},
            ["cid"],
        )

    @classmethod
    def enable_user(cls, cid: int) -> None:
        cls.get_user_cred(cid)

        cls._main["credentials"].update(
            {"cid": cid, "is_disabled": 0, "disable_reason": None},
            ["cid"],
        )

    @classmethod
    def get_db(cls):
        return cls._main
