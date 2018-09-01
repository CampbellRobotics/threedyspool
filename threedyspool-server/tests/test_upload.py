from io import BytesIO
from json import dumps, loads
import os
from pathlib import Path
import tempfile
from typing import Generator
import shutil
import sqlite3

from flask.testing import FlaskClient
from werkzeug.test import Client

import pytest
import threedyspool


@pytest.fixture
def client() -> Generator[FlaskClient, None, None]:
    threedyspool.app.config['DB_PATH'] = ':memory:'
    test_upload_path = tempfile.mkdtemp()
    threedyspool.app.config['UPLOAD_PATH'] = test_upload_path
    threedyspool.app.config['TESTING'] = True
    client = threedyspool.app.test_client()

    yield client
    shutil.rmtree(test_upload_path)


def test_no_jobs(client: FlaskClient):
    no_jobs = client.get('/jobs')
    assert loads(no_jobs.data) == {'status': 'ok', 'message': 'success', 'data': {'jobs': []}}


def test_new_job(client: FlaskClient):
    threedyspool.dbconn.execute("INSERT INTO users (id, email, displayName, privlevel) VALUES ('a', 'a@example.com', 'A A', 1)")
    resp = client.post('/jobs')
    assert loads(resp.data) == {'data': None, 'message': 'Form data is missing name', 'status': 'BadRequest'}
    testdata = {
        'name': 'a',
        'usage': '1234',
    }

    resp = client.post('/jobs', data=testdata)
    assert loads(resp.data) == {'data': None, 'message': 'Job must be uploaded with STL file', 'status': 'BadRequest'}
    testfiles = {
        'stl': (BytesIO(b'aa'), 'obj.stl'),
        'orig': (BytesIO(b'bb'), 'obj.stl'),
    }
    testdata2 = testdata.copy()
    testdata2.update(testfiles)
    resp = client.post('/jobs', data=testdata2)
    assert loads(resp.data) ==  {'message': 'Duplicate filenames in request', 'status': 'BadRequest', 'data': None}
    testfiles = {
        'stl': (BytesIO(b'aa'), 'obj.notok'),
        'orig': (BytesIO(b'bb'), 'obj.bad'),
    }
    testdata2 = testdata.copy()
    testdata2.update(testfiles)
    resp = client.post('/jobs', data=testdata2)
    assert loads(resp.data) == {
        'message': "File must have extension in ['f3d', 'rfa', 'rvt', 'sat', 'stl', 'stp']",
        'status': 'BadRequest', 'data': None}
    testfiles = {
        'stl': (BytesIO(b'aa'), 'obj.stl'),
        'orig': (BytesIO(b'bb'), 'obj.stp'),
    }
    testdata2 = testdata.copy()
    testdata2.update(testfiles)
    resp = client.post('/jobs', data=testdata2)
    data = loads(resp.data)
    assert data['message'] == "Files uploaded successfully"
    assert data['status'] == "ok"

    curs: sqlite3.Cursor = threedyspool.dbconn.execute("SELECT * FROM jobs")
    jobs = curs.fetchall()
    # if it isn't, that implies that some bad request got through
    assert len(jobs) == 1
    upload_dir = Path(threedyspool.app.config['UPLOAD_PATH'])
    test_stl = (upload_dir / '1' / 'obj.stl')
    test_stp = (upload_dir / '1' / 'obj.stp')
    assert test_stl.exists()
    assert test_stp.exists()
    with test_stl.open('rb') as h:
        assert h.read() == b'aa'
    with test_stp.open('rb') as h:
        assert h.read() == b'bb'
