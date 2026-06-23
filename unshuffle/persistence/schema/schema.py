import sqlite3
from pathlib import Path
import pydantic
from peewee import SqliteDatabase
import peewee

from .models import SchemaVersion, db_proxy
from .schema_ddl import (
    create_coherence_tables,
    create_core_tables,
    create_indexes,
    create_search_objects, ensure_id_fields,
)
from unshuffle.persistence.schema_migrations import ensure_feature_schema_columns, ensure_schema_version
from ...core.logging import logger


class FileModel(pydantic.BaseModel):
    name: str
    version: int
    file: Path

def migrations_up(db, conn: sqlite3.Connection) -> None:
    # ensure schema_version table exists
    version = 0
    _version = None
    _database = SqliteDatabase(db.db_path)
    db_proxy.initialize(_database)
    try:
        _version = SchemaVersion.select()[0]
        logger.info(f'Current version: {_version.version}')
    except peewee.OperationalError as e:
        logger.error(f"Error finding version: {e}")
        return

    migrations_folder = Path(__file__).parents[1].joinpath('migrations').resolve()

    def _parse_version(_file_name: str)->int:
        return int(_file_name.split('_')[0])

    files = [
        FileModel(version=_parse_version(f.name), name=str(f), file=f)
        for f in migrations_folder.iterdir() if f.is_file() and _parse_version(f.name) > _version.version
    ]

    # get current version from schema_version or 0
    # get migration file up to current version
    # for each run file, increase schema_version and move forward

    for f in files:
        try:
            with f.file.open("r", encoding="utf-8") as _f:
                _migration_text = _f.read()
                _database.execute_sql(_migration_text)
                version+=1
                _version.version=version
                _version.save()

        except Exception as e:
            logger.error(f"Error running migration {f.name}: {type(e)} {e}")


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
    ensure_id_fields(conn)


def ensure_coherence_schema(conn: sqlite3.Connection) -> None:
    create_coherence_tables(conn)
