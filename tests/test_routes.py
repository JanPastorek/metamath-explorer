import os
import sys
import json
import tempfile
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from app import create_app
from app import routes as routes_module

FIXTURE_PATH = os.path.join(os.path.dirname(__file__), 'fixtures', 'test.mm')


@pytest.fixture
def app(tmp_path):
    app = create_app()
    app.config['TESTING'] = True
    # Use a temporary directory for uploads during tests
    routes_module.UPLOAD_FOLDER = str(tmp_path)
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def parsed_client(client):
    """A client with a pre-parsed test database."""
    with open(FIXTURE_PATH, 'rb') as f:
        response = client.post(
            '/parse_database',
            data={'file': (f, 'test.mm')},
            content_type='multipart/form-data'
        )
    assert response.status_code == 200
    return client


class TestRoutes:
    """Tests for the Flask API routes."""

    def test_home(self, client):
        response = client.get('/')
        assert response.status_code == 200

    def test_theory_page(self, client):
        response = client.get('/theory')
        assert response.status_code == 200

    def test_graph_page(self, client):
        response = client.get('/graph')
        assert response.status_code == 200


class TestParseDatabase:
    """Tests for the /parse_database endpoint."""

    def test_parse_valid_file(self, client):
        with open(FIXTURE_PATH, 'rb') as f:
            response = client.post(
                '/parse_database',
                data={'file': (f, 'test.mm')},
                content_type='multipart/form-data'
            )
        assert response.status_code == 200
        data = response.get_json()
        assert 'parsed successfully' in data['message']

    def test_parse_no_file(self, client):
        response = client.post('/parse_database')
        assert response.status_code == 400
        data = response.get_json()
        assert 'No file provided' in data['message']

    def test_parse_empty_filename(self, client):
        from io import BytesIO
        response = client.post(
            '/parse_database',
            data={'file': (BytesIO(b''), '')},
            content_type='multipart/form-data'
        )
        assert response.status_code == 400

    def test_parse_invalid_extension(self, client):
        from io import BytesIO
        response = client.post(
            '/parse_database',
            data={'file': (BytesIO(b'data'), 'test.txt')},
            content_type='multipart/form-data'
        )
        assert response.status_code == 400
        data = response.get_json()
        assert 'Invalid file format' in data['message']


class TestGetStatement:
    """Tests for the /statement/<label> endpoint."""

    def test_get_existing_statement(self, parsed_client):
        response = parsed_client.get('/statement/ax-1')
        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == 'ax-1'
        assert data['type'] == '$a'
        assert 'Simplification' in data['description']

    def test_get_proposition(self, parsed_client):
        response = parsed_client.get('/statement/a1i')
        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == 'a1i'
        assert data['type'] == '$p'
        assert 'ax-1' in data['provedFrom']

    def test_get_nonexistent_statement(self, parsed_client):
        response = parsed_client.get('/statement/nonexistent')
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data


class TestGetStatementsBatch:
    """Tests for the /statements/batch endpoint."""

    def test_batch_existing_labels(self, parsed_client):
        response = parsed_client.post(
            '/statements/batch',
            data=json.dumps({'labels': ['ax-1', 'ax-2']}),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = response.get_json()
        assert 'ax-1' in data
        assert 'ax-2' in data

    def test_batch_no_labels(self, parsed_client):
        response = parsed_client.post(
            '/statements/batch',
            data=json.dumps({}),
            content_type='application/json'
        )
        assert response.status_code == 400

    def test_batch_labels_not_list(self, parsed_client):
        response = parsed_client.post(
            '/statements/batch',
            data=json.dumps({'labels': 'ax-1'}),
            content_type='application/json'
        )
        assert response.status_code == 400

    def test_batch_missing_labels_ignored(self, parsed_client):
        response = parsed_client.post(
            '/statements/batch',
            data=json.dumps({'labels': ['ax-1', 'nonexistent']}),
            content_type='application/json'
        )
        assert response.status_code == 200
        data = response.get_json()
        assert 'ax-1' in data
        assert 'nonexistent' not in data


class TestSearch:
    """Tests for the /search/<query> endpoint."""

    def test_search_existing(self, parsed_client):
        response = parsed_client.get('/search/axiom')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert isinstance(data['results'], list)

    def test_search_no_database(self, client):
        response = client.get('/search/anything')
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['results'] == []
