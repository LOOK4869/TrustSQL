# Load BIRD benchmark dataset: questions, database schemas, and gold SQL

import json
import os
import sqlite3
from typing import Any

from config import BIRD_DEV_JSON, BIRD_DB_DIR


class BirdExample:
    """Represents a single example from the BIRD benchmark dataset."""

    def __init__(self, data: dict[str, Any]) -> None:
        """
        Initialize from a raw BIRD JSON record.

        Args:
            data: Dict with keys like question, db_id, SQL, evidence, etc.
        """
        pass

    def __repr__(self) -> str:
        """Return string representation."""
        pass


class BirdLoader:
    """Load and iterate over BIRD benchmark examples."""

    def __init__(self, dev_json_path: str = BIRD_DEV_JSON, db_dir: str = BIRD_DB_DIR) -> None:
        """
        Initialize loader with paths to BIRD data.

        Args:
            dev_json_path: Path to dev.json file.
            db_dir: Directory containing per-database SQLite files.
        """
        pass

    def load(self) -> list[BirdExample]:
        """Load all examples from dev.json and return as BirdExample list."""
        pass

    def get_schema(self, db_id: str) -> dict[str, list[str]]:
        """
        Retrieve the full schema for a database as {table: [columns]}.

        Args:
            db_id: BIRD database identifier.

        Returns:
            Dict mapping table names to lists of column names.
        """
        pass

    def get_db_path(self, db_id: str) -> str:
        """Return the filesystem path to the SQLite file for db_id."""
        pass
