import os
from pathlib import Path
from datetime import datetime
import dataclasses
from dataclasses import dataclass
import runpy
import sqlite3
from threading import RLock
from typing import Any, ClassVar, Dict, List, NamedTuple, Optional, Type
import tempfile
from urllib.parse import quote, urljoin


from flask import Flask, jsonify, request, Response  # type: ignore
import flask.json  # type: ignore
from yoyo import default_migration_table, get_backend, read_migrations  # type: ignore
import yoyo.connections  # type: ignore
import yoyo.backends  # type: ignore
import werkzeug


app = Flask(__name__)
app.config.from_object('threedyspool.default_settings')
if 'THREEDYSPOOL_CONFIG' in os.environ:
    app.config.from_envvar('THREEDYSPOOL_CONFIG')
if not app.config.get('UPLOAD_PATH'):
    app.config['UPLOAD_PATH'] = tempfile.mkdtemp()


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
    detect_types=sqlite3.PARSE_DECLTYPES,
    check_same_thread=False
)
db_lock = RLock()
with db_lock:
    apply_migrations(dbconn)
    dbconn.execute('PRAGMA foreign_keys = ON')
dbconn.row_factory = sqlite3.Row


class JSONEncoder(flask.json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if dataclasses.is_dataclass(o):
            d: dict = dataclasses.asdict(o)
            if hasattr(o, 'dict_properties'):
                for prop in o.dict_properties:
                    d[prop] = getattr(o, prop)
            return d
        return super().default(self, o)

app.json_encoder = JSONEncoder


class HttpError(Exception):
    status_code = 500

    def __init__(self, message: str, status_code: int = None, payload: Any = None) -> None:
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self) -> Dict[str, str]:
        return {
            'status': self.__class__.__name__,
            'message': self.message,
            'data': self.payload
        }


class BadRequest(HttpError):
    status_code = 400


@dataclass
class User:
    id: str
    email: str
    displayName: str
    privlevel: int


@dataclass
class Job:
    id: int
    name: str
    date: int
    usage: str
    thumbUrl: str
    owner: Optional[User] = None
    dict_properties: ClassVar[List[str]] = ['files']

    @property
    def files(self):
        jobfiles_dir = get_upload_dir(self.id)
        if not jobfiles_dir.exists():
            return []
        return [get_url_for_model(self.id, name.name) for name in jobfiles_dir.iterdir()]


def db_make_obj(klass: Any, row: sqlite3.Row) -> Any:
    obj = klass(**row)
    if klass == Job:
        with db_lock:
            u = dbconn.execute("""SELECT * FROM users WHERE id = ?""", (row['owner'],)).fetchone()
        assert u
        obj.owner = db_make_obj(User, u)
    return obj


@app.errorhandler(HttpError)
def handle_errors(err: HttpError) -> Response:
    resp = jsonify(err.to_dict())
    resp.status_code = err.status_code
    return resp


OK_EXTENSIONS = set(['stl', 'stp', 'rvt', 'rfa', 'f3d', 'sat'])


def filename_is_ok(name: str) -> bool:
    return '.' in name and name.rsplit('.', 1)[1].lower() in OK_EXTENSIONS


class Upload(NamedTuple):
    secure_filename: str
    fileobj: werkzeug.datastructures.FileStorage


def check_upload(file: werkzeug.datastructures.FileStorage, which: str) -> Upload:
    assert file
    if not file.filename:
        raise BadRequest('File part has no name')
    secured_filename = werkzeug.utils.secure_filename(file.filename)
    if not filename_is_ok(secured_filename):
        raise BadRequest(f'File must have extension in {sorted(OK_EXTENSIONS)!r}')
    return Upload(secured_filename, file)


def get_url_for_model(job_id: int, model_name: str) -> str:
    return flask.url_for('job_file', job_id=job_id, filename=model_name)


def get_upload_dir(job_id: int) -> Path:
    return Path(app.config['UPLOAD_PATH']) / str(job_id)


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
    with db_lock:
        jobs = dbconn.execute("""SELECT * FROM jobs""")
        resp['data'] = {
            'jobs': [db_make_obj(Job, job) for job in jobs]
        }
    return jsonify(resp)


@app.route('/jobs/<int:job_id>')
def job(job_id: int) -> Response:
    """
    Get the details of a specific job
    """
    resp = OK_RESP.copy()
    with db_lock:
        job = dbconn.execute("""SELECT * FROM jobs WHERE id = ?""", job_id)
        resp['data'] = {
            'job': db_make_obj(Job, job)
        }


@app.route('/jobs/<int:job_id>/files/<filename>')
def job_file(job_id: int, filename: str) -> Response:
    return flask.send_from_directory(
        Path(app.config['UPLOAD_PATH']) / str(job_id),
        filename
    )


@app.route('/jobs', methods=('POST',))
def post_job():
    """
    Make a new job
    """
    required_attributes = (
        'name',
        'usage',
    )
    for attr in required_attributes:
        if attr not in request.form:
            raise BadRequest(f'Form data is missing {attr}')

    if len(request.files) > app.config['JOB_FILES_LIMIT']:
        # we can handle more but why?
        raise BadRequest(f'Too many files, limit is {app.config["JOB_FILES_LIMIT"]}')

    # note: this is intentionally not a genexp because these we need to
    #       allow all files an equal opportunity to raise an exception ASAP
    uploads = [check_upload(v, f) for f, v in request.files.items()]
    for f in uploads:
        if f.secure_filename.endswith('.stl'):
            break
    else:
        raise BadRequest('Job must be uploaded with STL file')

    deduped = set(u.secure_filename for u in uploads)
    if len(deduped) != len(uploads):
        raise BadRequest('Duplicate filenames in request')

    with db_lock, dbconn:
        dbdata = {
            'name': request.form['name'],
            'owner': 'a',
            'date': int(datetime.utcnow().timestamp()),
            'usage': request.form['usage'],
        }
        cursor = dbconn.execute(
            'INSERT INTO jobs (name, owner, date, usage)'
            'values (:name, :owner, :date, :usage)',
            dbdata
        )
        job_upload_dir = get_upload_dir(cursor.lastrowid)
        job_upload_dir.mkdir(parents=True, exist_ok=False)
        for f in uploads:
            path = job_upload_dir / f.secure_filename
            f.fileobj.save(str(path))
            if os.stat(path).st_size == 0:
                raise BadRequest('File has 0 size!')
        dbdata['id'] = cursor.lastrowid
    return jsonify({'status': 'ok', 'message': f'Files uploaded successfully', 'data': dbdata})
