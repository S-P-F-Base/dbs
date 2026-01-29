import json
import logging
import sqlite3
from collections.abc import Sequence
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from queue import Queue
from threading import Thread
from typing import Any

_DB_DIR = Path("data/dbs")


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
            SQLTask(
                f"CREATE TABLE IF NOT EXISTS {self.name} ({', '.join(self.columns)});"
            )
        ]

        for idx in self.indexes:
            tasks.append(SQLTask(idx))

        return tasks


class BaseDB:
    _db_name: str = ""

    @classmethod
    def _get_queue(cls) -> Queue:
        if cls._queue is None:
            cls._queue = Queue()

        return cls._queue

    @classmethod
    def _db_path(cls) -> Path:
        return _DB_DIR / f"{cls._db_name}.db"

    @classmethod
    def _connect(cls) -> sqlite3.Connection:
        conn = sqlite3.connect(
            cls._db_path(),
            timeout=5.0,
            isolation_level=None,
            check_same_thread=False,
        )
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute("PRAGMA busy_timeout=5000;")
        return conn

    @classmethod
    def _execute_write(cls, task: SQLTask):
        conn = cls._connect()
        try:
            conn.execute("BEGIN;")
            conn.execute(task.sql, task.params or ())
            conn.execute("COMMIT;")

        except Exception:
            conn.execute("ROLLBACK;")
            raise

        finally:
            conn.close()

    @classmethod
    def _start_worker(cls):
        if cls._worker_started:
            return

        cls._worker_started = True
        queue = cls._get_queue()

        def worker():
            while True:
                task = queue.get()
                try:
                    cls._execute_write(task)

                except Exception:
                    logging.exception(f"DB {cls._db_name} write failed: {task}")

                finally:
                    queue.task_done()

        Thread(target=worker, daemon=True).start()

    @classmethod
    def _init_from_spec(cls, spec: TableSpec) -> None:
        cls._init_db(spec.sql_tasks())

    @classmethod
    def _init_db(cls, sql_t: list[SQLTask]) -> None:
        _DB_DIR.mkdir(parents=True, exist_ok=True)
        cls._start_worker()

        queue = cls._get_queue()
        for task in sql_t:
            queue.put(task)

    @classmethod
    def _pack(cls, value, typ):
        if typ is json:
            return json.dumps(value, ensure_ascii=False)

        return value

    @classmethod
    def _unpack(cls, value, typ):
        if typ is json:
            return json.loads(value)

        return typ(value) if typ is not None else value

    @classmethod
    def submit_write(cls, sql_t: SQLTask):
        cls._get_queue().put(sql_t)

    @classmethod
    @contextmanager
    def read(cls):
        conn = cls._connect()
        try:
            yield conn

        finally:
            conn.close()

    @classmethod
    def _insert(cls, **cols):
        keys = []
        vals = []

        for k, (v, t) in cols.items():
            keys.append(k)
            vals.append(cls._pack(v, t))

        sql = f"INSERT INTO {cls._db_name} ({', '.join(keys)}) VALUES ({', '.join('?' * len(vals))})"
        cls.submit_write(SQLTask(sql, tuple(vals)))

    @classmethod
    def _update(cls, *, where: tuple[str, object], **cols):
        set_sql = []
        params = []

        for k, (v, t) in cols.items():
            set_sql.append(f"{k} = ?")
            params.append(cls._pack(v, t))

        w_key, w_val = where
        params.append(w_val)

        sql = f"UPDATE {cls._db_name} SET {', '.join(set_sql)} WHERE {w_key} = ?"
        cls.submit_write(SQLTask(sql, tuple(params)))

    @classmethod
    def _get(cls, *, where: tuple[str, object], fields: dict[str, type]):
        w_key, w_val = where
        cols = ", ".join(fields.keys())

        with cls.read() as conn:
            cur = conn.execute(
                f"SELECT {cols} FROM {cls._db_name} WHERE {w_key} = ?",
                (w_val,),
            )
            row = cur.fetchone()

        if row is None:
            return None

        return {k: cls._unpack(v, fields[k]) for k, v in zip(fields.keys(), row)}

    @classmethod
    def _delete(cls, *, where: tuple[str, Any]) -> None:
        col, value = where

        cls.submit_write(
            SQLTask(
                f"DELETE FROM {cls._db_name} WHERE {col} = ?",
                (value,),
            )
        )
