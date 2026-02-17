from typing import Any

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

    @classmethod
    def create(
        cls,
        cid: int,
        name: str | None = None,
        path_to_image: str | None = None,
    ) -> None:
        cls._insert(
            cid=(cid, int),
            name=(name, str),
            path_to_image=(path_to_image, str),
        )

    @classmethod
    def update(
        cls,
        cid: int,
        *,
        name: str | None = None,
        path_to_image: str | None = None,
    ) -> None:
        cols = {}

        if name is not None:
            cols["name"] = (name, str)

        if path_to_image is not None:
            cols["path_to_image"] = (path_to_image, str)

        if not cols:
            return

        cls._update(
            where=("cid", cid),
            **cols,
        )

    @classmethod
    def delete(cls, cid: int) -> None:
        cls._delete(where=("cid", cid))

    @classmethod
    def get(cls, cid: int) -> dict[str, Any] | None:
        return cls._get(
            where=("cid", cid),
            fields={
                "cid": int,
                "name": str,
                "path_to_image": str,
            },
        )
