# Load BIRD benchmark dataset: questions, database schemas, and gold SQL

import json
import os
import sqlite3
from dataclasses import dataclass
from typing import Any

from config import BIRD_DEV_JSON, BIRD_TABLES_JSON, BIRD_DB_DIR


@dataclass
class BirdExample:
    """Represents a single example from the BIRD benchmark dataset."""

    question_id: int
    db_id: str
    question: str
    evidence: str
    gold_sql: str
    difficulty: str

    def __repr__(self) -> str:
        return (
            f"BirdExample(id={self.question_id}, db={self.db_id!r}, "
            f"difficulty={self.difficulty!r},\n"
            f"  question={self.question!r},\n"
            f"  evidence={self.evidence!r},\n"
            f"  gold_sql={self.gold_sql!r})"
        )


class BirdLoader:
    """Load and iterate over BIRD benchmark examples."""

    def __init__(
        self,
        dev_json_path: str = BIRD_DEV_JSON,
        tables_json_path: str = BIRD_TABLES_JSON,
        db_dir: str = BIRD_DB_DIR,
    ) -> None:
        self.dev_json_path = dev_json_path
        self.tables_json_path = tables_json_path
        self.db_dir = db_dir

        # Pre-load schema index from dev_tables.json: {db_id -> table entry}
        self._tables_index: dict[str, dict] = self._load_tables_index()

    def _load_tables_index(self) -> dict[str, dict]:
        """Load dev_tables.json and index by db_id."""
        with open(self.tables_json_path, encoding="utf-8") as f:
            tables = json.load(f)
        return {entry["db_id"]: entry for entry in tables}

    def load(self) -> list[BirdExample]:
        """Load all examples from dev.json and return as BirdExample list."""
        with open(self.dev_json_path, encoding="utf-8") as f:
            raw = json.load(f)
        return [
            BirdExample(
                question_id=item["question_id"],
                db_id=item["db_id"],
                question=item["question"],
                evidence=item.get("evidence", ""),
                gold_sql=item["SQL"],
                difficulty=item.get("difficulty", ""),
            )
            for item in raw
        ]

    def get_schema(self, db_id: str) -> dict[str, list[str]]:
        """
        Return the schema for a database as {table_name: [col1, col2, ...]}.

        Uses dev_tables.json (column_names_original) as the primary source.
        Falls back to querying the SQLite file directly if db_id is not found.
        """
        if db_id in self._tables_index:
            entry = self._tables_index[db_id]
            tables = entry["table_names_original"]
            # column_names_original: list of [table_idx, col_name], table_idx=-1 means wildcard
            schema: dict[str, list[str]] = {t: [] for t in tables}
            for table_idx, col_name in entry["column_names_original"]:
                if table_idx == -1:
                    continue  # skip the global '*' row
                schema[tables[table_idx]].append(col_name)
            return schema

        # Fallback: read schema directly from SQLite
        db_path = self.get_db_path(db_id)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        schema = {}
        for table in tables:
            cursor.execute(f"PRAGMA table_info({table});")
            schema[table] = [row[1] for row in cursor.fetchall()]
        conn.close()
        return schema

    def get_foreign_keys(self, db_id: str) -> list[tuple[str, str, str, str]]:
        """
        Return foreign key relationships for a database.

        Returns a list of (from_table, from_col, to_table, to_col) tuples.
        """
        if db_id not in self._tables_index:
            return []
        entry = self._tables_index[db_id]
        tables = entry["table_names_original"]
        cols = entry["column_names_original"]  # [[table_idx, col_name], ...]
        fks = []
        for from_col_idx, to_col_idx in entry.get("foreign_keys", []):
            from_t_idx, from_col = cols[from_col_idx]
            to_t_idx, to_col = cols[to_col_idx]
            fks.append((tables[from_t_idx], from_col, tables[to_t_idx], to_col))
        return fks

    def get_db_path(self, db_id: str) -> str:
        """Return the filesystem path to the SQLite file for db_id."""
        return os.path.join(self.db_dir, db_id, f"{db_id}.sqlite")
