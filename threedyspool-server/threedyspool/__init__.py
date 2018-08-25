import os
from pathlib import Path
from dataclasses import dataclass
import runpy
import sqlite3
from typing import Dict, NamedTuple

from flask import Flask, jsonify  # type: ignore
from yoyo import default_migration_table, get_backend, read_migrations # type: ignore
import yoyo.connections
import yoyo.backends  # type: ignore


app = Flask(__name__)
app.config.from_object('threedyspool.default_settings')
app.config.from_envvar('THREEDYSPOOL_CONFIG')


class SQLite3BackendWithConnection(yoyo.backends.DatabaseBackend):
    driver_module = 'sqlite3'
    list_tables_sql = "SELECT name FROM sqlite_master WHERE type = 'table'"

    def __init__(self, conn, *args, **kwargs):
        self.conn = conn
        super().__init__(*args, **kwargs)

    def connect(self, _):
        self.conn.isolation_level = None
        return self.conn


def apply_migrations(dbconn: sqlite3.Connection) -> None:
    url = yoyo.connections.parse_uri(f'sqlite:///{app.config["DB_PATH"]}')
    backend = SQLite3BackendWithConnection(dbconn, url, default_migration_table)
    migrations = read_migrations('migrations/')
    with backend.lock():
        backend.apply_migrations(backend.to_apply(migrations))


dbconn = sqlite3.connect(
    app.config['DB_PATH'],
    detect_types=sqlite3.PARSE_COLNAMES | sqlite3.PARSE_DECLTYPES
)
apply_migrations(dbconn)


class Job:
    def __init__(self, id, name, owner, date, usage, origUrl, stlUrl, thumbUrl):
        pass


@app.route('/jobs')
def jobs():
    """
    Get the currently existent jobs.
    """
    db = dbconn.cursor()
    return str(list(db.execute("""SELECT * FROM jobs""")))
