from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from typing import Optional


@dataclass
class UsageEvent:
    timestamp_utc: float
    app_name: str
    window_title: Optional[str]


def get_connection(db_path: str) -> sqlite3.Connection:
    connection = sqlite3.connect(db_path)
    connection.execute("PRAGMA journal_mode=WAL;")
    connection.execute("PRAGMA synchronous=NORMAL;")
    return connection


def ensure_schema(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS usage_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp_utc REAL NOT NULL,
            app_name TEXT NOT NULL,
            window_title TEXT
        );
        """
    )
    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_usage_events_timestamp ON usage_events(timestamp_utc);
        """
    )
    connection.commit()


def insert_usage_event(connection: sqlite3.Connection, event: UsageEvent) -> None:
    connection.execute(
        "INSERT INTO usage_events (timestamp_utc, app_name, window_title) VALUES (?, ?, ?)",
        (event.timestamp_utc, event.app_name, event.window_title),
    )
    connection.commit()