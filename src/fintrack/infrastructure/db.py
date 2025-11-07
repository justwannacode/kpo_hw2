from __future__ import annotations
import sqlite3
from pathlib import Path
from typing import Iterable, Any, Sequence

class Database:
    # обертка над sqlite3
    def __init__(self, db_path: str | Path = ":memory:") -> None:
        self._db_path = str(db_path)
        self._conn = sqlite3.connect(self._db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys=ON")
        self._init_schema()

    @property
    def connection(self) -> sqlite3.Connection:
        return self._conn

    def _init_schema(self) -> None:
        cur = self._conn.cursor()
        cur.executescript(
            """
            CREATE TABLE IF NOT EXISTS bank_accounts(
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                balance TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS categories(
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL CHECK(type IN ('INCOME','EXPENSE')),
                name TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS operations(
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL CHECK(type IN ('INCOME','EXPENSE')),
                bank_account_id TEXT NOT NULL,
                amount TEXT NOT NULL,
                date TEXT NOT NULL,
                description TEXT,
                category_id TEXT NOT NULL,
                FOREIGN KEY(bank_account_id) REFERENCES bank_accounts(id) ON DELETE CASCADE,
                FOREIGN KEY(category_id) REFERENCES categories(id) ON DELETE RESTRICT
            );
            """
        )
        self._conn.commit()

    def execute(self, sql: str, params: Sequence[Any] | None = None) -> None:
        self._conn.execute(sql, params or [])
        self._conn.commit()

    def executemany(self, sql: str,
                    seq_of_params: Iterable[Sequence[Any]]) -> None:
        self._conn.executemany(sql, seq_of_params)
        self._conn.commit()

    def query(self, sql: str,
              params: Sequence[Any] | None = None) -> list[sqlite3.Row]:
        cur = self._conn.execute(sql, params or [])
        return cur.fetchall()
