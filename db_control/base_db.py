import json
import os
import sqlite3
from collections.abc import Sequence
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_DEFAULT_DB_DIR = _PROJECT_ROOT / "data" / "dbs"
_DB_DIR = Path(os.getenv("DBS_DATA_DIR", str(_DEFAULT_DB_DIR))).resolve()


@dataclass(frozen=True)
class SQLTask:
    sql: str
    params: Sequence | None = None


@dataclass(frozen=True)
class TableSpec:
    name: str
    columns: list[str]
    indexes: list[str] = field(default_factory=list)

    def sql_tasks(self) -> list[SQLTask]:
        tasks = [
            SQLTask("PRAGMA journal_mode=WAL;"),
            SQLTask("PRAGMA synchronous=NORMAL;"),
            SQLTask(
                f"CREATE TABLE IF NOT EXISTS {self.name} ({', '.join(self.columns)});"
            ),
        ]

        for idx in self.indexes:
            tasks.append(SQLTask(idx))

        return tasks


class BaseDB:
    _db_name: str = ""

    @classmethod
    def _db_path(cls) -> Path:
        return _DB_DIR / f"{cls._db_name}.db"

    @classmethod
    def _table_name(cls) -> str:
        table = getattr(cls, "TABLE", None)
        table_name = getattr(table, "name", None)
        if isinstance(table_name, str) and table_name:
            return table_name

        return cls._db_name

    @classmethod
    def _connect(cls) -> sqlite3.Connection:
        conn = sqlite3.connect(
            cls._db_path(),
            timeout=5.0,
        )
        conn.execute("PRAGMA busy_timeout=5000;")
        return conn

    @classmethod
    def _init_from_spec(cls, spec: TableSpec) -> None:
        cls._init_db(spec.sql_tasks())

    @classmethod
    def _init_db(cls, sql_t: list[SQLTask]) -> None:
        _DB_DIR.mkdir(parents=True, exist_ok=True)

        for task in sql_t:
            cls.write(task)

    @classmethod
    def _pack(cls, value: Any, typ: type):
        if value is None:
            return None

        if typ in (dict, list):
            return json.dumps(value, ensure_ascii=False)

        return value

    @classmethod
    def _unpack(cls, value: Any, typ: type):
        if value is None:
            return None

        if typ in (dict, list):
            decoded = json.loads(value)
            if not isinstance(decoded, typ):
                raise TypeError(
                    f"Expected {typ.__name__}, got {type(decoded).__name__}"
                )

            return decoded

        return typ(value)

    @classmethod
    @contextmanager
    def read(cls):
        conn = cls._connect()
        try:
            yield conn

        finally:
            conn.close()

    @classmethod
    def write(cls, task: SQLTask, return_lastid: bool = False) -> int | None:
        with cls._connect() as conn:
            cur = conn.execute(task.sql, task.params or ())
            conn.commit()
            if return_lastid:
                return cur.lastrowid

            else:
                return None

    @classmethod
    def _insert(cls, **cols) -> int:
        keys = []
        vals = []

        for k, (v, t) in cols.items():
            keys.append(k)
            vals.append(cls._pack(v, t))

        table_name = cls._table_name()
        sql = f"INSERT INTO {table_name} ({', '.join(keys)}) VALUES ({', '.join('?' * len(vals))})"
        return cls.write(SQLTask(sql, tuple(vals)), True)  # pyright: ignore[reportReturnType]

    @classmethod
    def _update(cls, *, where: tuple[str, object], **cols):
        set_sql = []
        params = []

        for k, (v, t) in cols.items():
            set_sql.append(f"{k} = ?")
            params.append(cls._pack(v, t))

        w_key, w_val = where
        params.append(w_val)

        table_name = cls._table_name()
        sql = f"UPDATE {table_name} SET {', '.join(set_sql)} WHERE {w_key} = ?"
        cls.write(SQLTask(sql, tuple(params)))

    @classmethod
    def _get(
        cls,
        *,
        where: tuple[str, object] | list[tuple[str, object]],
        fields: dict[str, type],
    ):
        cols = ", ".join(fields.keys())

        if isinstance(where, tuple):
            where_items = [where]

        else:
            where_items = where

        where_sql = " AND ".join(f"{key} = ?" for key, _ in where_items)
        params = tuple(value for _, value in where_items)
        table_name = cls._table_name()

        with cls.read() as conn:
            cur = conn.execute(
                f"SELECT {cols} FROM {table_name} WHERE {where_sql}",
                params,
            )
            row = cur.fetchone()

        if row is None:
            return None

        return {k: cls._unpack(v, fields[k]) for k, v in zip(fields.keys(), row)}

    @classmethod
    def _list(
        cls,
        *,
        fields: dict[str, type],
        where: tuple[str, object] | None = None,
        order_by: str | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        cols = ", ".join(fields.keys())
        table_name = cls._table_name()
        sql = f"SELECT {cols} FROM {table_name}"
        params: list[object] = []

        if where is not None:
            w_key, w_val = where
            sql += f" WHERE {w_key} = ?"
            params.append(w_val)

        if order_by is not None:
            sql += f" ORDER BY {order_by}"

        if limit is not None:
            sql += " LIMIT ?"
            params.append(limit)

        with cls.read() as conn:
            cur = conn.execute(sql, tuple(params))
            rows = cur.fetchall()

        return [
            {k: cls._unpack(v, fields[k]) for k, v in zip(fields.keys(), row)}
            for row in rows
        ]

    @classmethod
    def _delete(cls, *, where: tuple[str, Any]) -> None:
        col, value = where
        table_name = cls._table_name()

        cls.write(
            SQLTask(
                f"DELETE FROM {table_name} WHERE {col} = ?",
                (value,),
            )
        )
