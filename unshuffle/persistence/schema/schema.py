import sqlite3

from .schema_ddl import (
    create_coherence_tables,
    create_core_tables,
    create_indexes,
    create_search_objects,
)
from unshuffle.persistence.schema_migrations import ensure_feature_schema_columns, ensure_schema_version


def migrations_up(conn: sqlite3.Connection) -> None:
    # ensure schema_version table exists
    # get current version from schema_version or 0
    # get migration file up to current version
    # for each run file, increase schema_version and move forward

    pass


def initialize_v1_schema(conn: sqlite3.Connection, schema_version: int) -> None:
    # ensure schema_version table exists
    # get current version from schema_version or 0
    # get migration file up to current version
    # for each run file, increase schema_version and move forward

    ensure_schema_version(conn, schema_version)
    create_core_tables(conn)
    ensure_coherence_schema(conn)
    create_search_objects(conn)
    ensure_feature_schema_columns(conn)
    create_indexes(conn)


def ensure_coherence_schema(conn: sqlite3.Connection) -> None:
    create_coherence_tables(conn)
