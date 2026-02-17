import time
from typing import Any

from ..base_db import BaseDB, TableSpec


class CommercialChecksDB(BaseDB):
    _db_name = "commercial_checks_db"

    TABLE = TableSpec(
        name="commercial_checks_db",
        columns=[
            "uid INTEGER PRIMARY KEY AUTOINCREMENT",  # uuid
            "cid INTEGER NOT NULL",  # credential.id
            "csid INTEGER NOT NULL",  # commerce_services_db.id
            "tax_id TEXT",  # айди от налоговой
            "status TEXT NOT NULL",  # status
            "timestamp INTEGER NOT NULL",  # дата обноления последнего данного сервиса (обычно это будет когда статус последний раз изменился)
            "snap BLOB NOT NULL",  # json blob
        ],
    )

    @classmethod
    def set_up(cls) -> None:
        cls._init_from_spec(cls.TABLE)

    @classmethod
    def create(
        cls,
        cid: int,
        csid: int,
        status: str,
        snap: dict[str, Any] | None = None,
        timestamp: int | None = None,
        tax_id: str | None = None,
    ) -> None:
        if timestamp is None:
            timestamp = int(time.time())

        cls._insert(
            cid=(cid, int),
            csid=(csid, int),
            tax_id=(tax_id, str),
            status=(status, str),
            timestamp=(timestamp, int),
            snap=(snap or {}, dict),
        )

    @classmethod
    def update(
        cls,
        uid: int,
        *,
        cid: int | None = None,
        csid: int | None = None,
        tax_id: str | None = None,
        status: str | None = None,
        timestamp: int | None = None,
        snap: dict[str, Any] | None = None,
    ) -> None:
        cols = {}

        if cid is not None:
            cols["cid"] = (cid, int)

        if csid is not None:
            cols["csid"] = (csid, int)

        if tax_id is not None:
            cols["tax_id"] = (tax_id, str)

        if status is not None:
            cols["status"] = (status, str)

        if timestamp is not None:
            cols["timestamp"] = (timestamp, int)

        if snap is not None:
            cols["snap"] = (snap, dict)

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
                "cid": int,
                "csid": int,
                "tax_id": str,
                "status": str,
                "timestamp": int,
                "snap": dict,
            },
        )

    @classmethod
    def list_by_owner(cls, cid: int) -> list[dict[str, Any]]:
        return cls._list(
            where=("cid", cid),
            order_by="timestamp DESC, uid DESC",
            fields={
                "uid": int,
                "cid": int,
                "csid": int,
                "tax_id": str,
                "status": str,
                "timestamp": int,
                "snap": dict,
            },
        )

    @classmethod
    def list_by_service(cls, csid: int) -> list[dict[str, Any]]:
        return cls._list(
            where=("csid", csid),
            order_by="timestamp DESC, uid DESC",
            fields={
                "uid": int,
                "cid": int,
                "csid": int,
                "tax_id": str,
                "status": str,
                "timestamp": int,
                "snap": dict,
            },
        )
