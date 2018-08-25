from io import BytesIO
from json import dumps, loads
import os
import tempfile
from typing import Generator
import shutil

from flask.testing import FlaskClient
from werkzeug.test import Client

import pytest
import threedyspool


@pytest.fixture
def client() -> Generator[FlaskClient, None, None]:
    db_fd, threedyspool.app.config['DB_PATH'] = tempfile.mkstemp()
    test_upload_path = tempfile.mkdtemp()
    threedyspool.app.config['UPLOAD_PATH'] = test_upload_path
    threedyspool.app.config['TESTING'] = True
    client = threedyspool.app.test_client()

    yield client
    os.close(db_fd)
    shutil.rmtree(test_upload_path)
    os.unlink(threedyspool.app.config['DB_PATH'])


def test_no_jobs(client: FlaskClient):
    no_jobs = client.get('/jobs')
    assert loads(no_jobs.data) == {'status': 'ok', 'message': 'success', 'data': {'jobs': []}}


def test_new_job(client: FlaskClient):
    testdata = {
        'name': 'a',
        'usage': '1234',
    }
    resp = client.post('/jobs', data=testdata)
    assert loads(resp.data) == {'data': None, 'message': 'Missing stl file', 'status': 'BadRequest'}
    testfiles = {
        'stl': (BytesIO(b'aa'), 'obj.stl'),
        'orig': (BytesIO(b'bb'), 'obj.stp'),
    }
    testdata2 = testdata.copy()
    testdata2.update(testfiles)
    print(testdata2)
    resp = client.post('/jobs', data=testdata2)
    assert loads(resp.data) == {'message': "uploaded ('stl', 'orig') successfully", 'status': 'ok'}
