import time
from typing import Any

from ..base_db import BaseDB, TableSpec


class CommerceServicesDB(BaseDB):
    _db_name = "commerce_services_db"

    TABLE = TableSpec(
        name="commerce_services_db",
        columns=[
            "uid INTEGER PRIMARY KEY AUTOINCREMENT",  # uuid
            "name TEXT NOT NULL",  # имя
            "desc TEXT NOT NULL",  # описание
            "price TEXT NOT NULL",  # цена (ибо float привет передавало)
            "discount TEXT NOT NULL",  # скидка (ибо float привет передавало)
            "discount_end_time INTEGER NOT NULL",  # когда скидка закончится
            "time_of_create INTEGER NOT NULL",  # когда создано
        ],
    )

    @classmethod
    def set_up(cls) -> None:
        cls._init_from_spec(cls.TABLE)

    @classmethod
    def create(
        cls,
        name: str,
        desc: str,
        price: str,
        discount: str,
        discount_end_time: int,
        time_of_create: int | None = None,
    ) -> None:
        if time_of_create is None:
            time_of_create = int(time.time())

        cls._insert(
            name=(name, str),
            desc=(desc, str),
            price=(price, str),
            discount=(discount, str),
            discount_end_time=(discount_end_time, int),
            time_of_create=(time_of_create, int),
        )

    @classmethod
    def update(
        cls,
        uid: int,
        *,
        name: str | None = None,
        desc: str | None = None,
        price: str | None = None,
        discount: str | None = None,
        discount_end_time: int | None = None,
        time_of_create: int | None = None,
    ) -> None:
        cols = {}

        if name is not None:
            cols["name"] = (name, str)

        if desc is not None:
            cols["desc"] = (desc, str)

        if price is not None:
            cols["price"] = (price, str)

        if discount is not None:
            cols["discount"] = (discount, str)

        if discount_end_time is not None:
            cols["discount_end_time"] = (discount_end_time, int)

        if time_of_create is not None:
            cols["time_of_create"] = (time_of_create, int)

        if not cols:
            return

        cls._update(
            where=("uid", uid),
            **cols,
        )

    @classmethod
    def delete(cls, uid: int) -> None:
        cls._delete(where=("uid", uid))

    @classmethod
    def get(cls, uid: int) -> dict[str, Any] | None:
        return cls._get(
            where=("uid", uid),
            fields={
                "uid": int,
                "name": str,
                "desc": str,
                "price": str,
                "discount": str,
                "discount_end_time": int,
                "time_of_create": int,
            },
        )

    @classmethod
    def list_all(cls) -> list[dict[str, Any]]:
        return cls._list(
            order_by="uid",
            fields={
                "uid": int,
                "name": str,
                "desc": str,
                "price": str,
                "discount": str,
                "discount_end_time": int,
                "time_of_create": int,
            },
        )
