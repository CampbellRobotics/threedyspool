import os
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
import runpy
import sqlite3
from typing import Any, Dict, NamedTuple, Optional, Type
import tempfile
import werkzeug

from flask import Flask, jsonify, request, Response  # type: ignore
from yoyo import default_migration_table, get_backend, read_migrations # type: ignore
import yoyo.connections  # type: ignore
import yoyo.backends  # type: ignore


app = Flask(__name__)
app.config.from_object('threedyspool.default_settings')
if 'THREEDYSPOOL_CONFIG' in os.environ:
    app.config.from_envvar('THREEDYSPOOL_CONFIG')
if not app.config.get('UPLOAD_FOLDER'):
    app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()


class SQLite3BackendWithConnection(yoyo.backends.DatabaseBackend):
    driver_module = 'sqlite3'
    list_tables_sql = "SELECT name FROM sqlite_master WHERE type = 'table'"

    def __init__(self, conn, *args, **kwargs) -> None:
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
    detect_types=sqlite3.PARSE_DECLTYPES
)
apply_migrations(dbconn)


@dataclass
class User:
    id: str
    email: str
    displayName: str


@dataclass
class Job:
    id: int
    name: str
    owner: str
    date: int
    usage: str
    origUrl: str
    stlUrl: str
    thumbUrl: str
    def owner_(self, db: sqlite3.Cursor) -> Optional[User]:
        row = db.execute("""SELECT * FROM users WHERE user.id = ?""", (self.owner,)).fetchone()
        if not row:
            return None
        return db_make_obj(User, row)


def db_make_obj(klass: Any, row: sqlite3.Row) -> Any:
    cols = row.keys()
    return klass(**{k: v for (k, v) in zip(cols, row)})


OK_RESP = {
    'status': 'ok',
    'message': 'success',
    'data': None
}


@app.route('/jobs')
def jobs():
    """
    Get the currently existent jobs.
    """
    resp = OK_RESP.copy()
    resp['data'] = {
        'jobs': list(dbconn.execute("""SELECT * FROM jobs"""))
    }
    return jsonify(resp)


OK_EXTENSIONS = set(['stl', 'stp', 'rvt', 'rfa', 'f3d', 'sat'])


def filename_is_ok(name: str) -> bool:
    return '.' in name and name.rsplit('.', 1)[1].lower() in OK_EXTENSIONS


class HttpError(Exception):
    status_code = 500

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        return {
            'status': self.__class__.__name__,
            'message': self.message,
            'data': self.payload
        }


def BadRequest(HttpError):
    pass


@app.errorhandler(HttpError)
def handle_errors(err: HttpError) -> Response:
    resp = jsonify(err.to_dict())
    resp.status_code = err.status_code
    return resp


class Upload(NamedTuple):
    secure_filename: str
    fileobj: Any


def check_upload(rq_files: werkzeug.datastructures.ImmutableMultiDict) -> Upload:
    if 'file' not in rq_files or not rq_files['file']:
        raise BadRequest('File part missing')
    file = rq_files['file']
    if not file.filename:
        raise BadRequest('File part has no name')
    secured_filename = werkzeug.utils.secure_filename(file.filename)
    if not filename_is_ok(secured_filename):
        raise BadRequest(f'File must have extension in {OK_EXTENSIONS!r}')
    return Upload(secured_filename, file)


@app.route('/jobs', methods=('POST',))
def post_job():
    """
    Make a new job
    """
    required_attributes = (
        'name',
        'usage',
    )
    raise BadRequest('wtf')
    for attr in required_attributes:
        if attr not in request.form:
            raise BadRequest(f'Form data is missing {attr}')
    want_files = ('stl',)
    if 'orig' in request.files:
        want_files += ('orig',)
    # note: this is intentionally not a genexp because these we need to
    #       allow all files an equal opportunity to raise an exception ASAP
    uploads = [check_upload(request.files) for f in want_files]
    for f in uploads:
        f.fileobj.save(Path(app.config['UPLOAD_PATH']) / f.secure_filename)

    with dbconn:
        dbconn.execute(
            'INSERT INTO jobs (name, owner, date, usage, '
            'origUrl, stlUrl) values (:name, :owner, :date, :usage, :origUrl, :stlUrl)',
            {
                'name': request.form['name'],
                'owner': 'a',
                'date': int(datetime.utcnow().timestamp()),
                'usage': 'idk',
                'origUrl': 'https://example.com/aa.stl',
                'stlUrl': 'https://example.com/bb.stl',
            }
        )
    return jsonify({'status': 'ok', 'message': f'uploaded {want_files!r} successfully'})
