import os
import tempfile
from json import loads
from typing import Generator


from flask.testing import FlaskClient

import pytest
import threedyspool


@pytest.fixture
def client() -> Generator[FlaskClient, None, None]:
    db_fd, threedyspool.app.config['DB_PATH'] = tempfile.mkstemp()
    threedyspool.app.config['TESTING'] = True
    client = threedyspool.app.test_client()

    yield client
    os.close(db_fd)
    os.unlink(threedyspool.app.config['DB_PATH'])


def test_no_jobs(client: FlaskClient):
    no_jobs = client.get('/jobs')
    assert loads(no_jobs.data) == {'status': 'ok', 'message': 'success', 'data': {'jobs': []}}


def test_new_job(client: FlaskClient):
    resp = client.post('/jobs', data={
        'name': 'a',
        'usage': '1234',
    })
    assert loads(resp.data) == {}
