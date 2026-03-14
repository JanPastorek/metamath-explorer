import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from app.DataHandler import DataHandler

FIXTURE_PATH = os.path.join(os.path.dirname(__file__), 'fixtures', 'test.mm')


@pytest.fixture
def handler():
    dh = DataHandler()
    dh.parse_database(FIXTURE_PATH)
    return dh


class TestDataHandler:
    """Tests for the DataHandler class."""

    def test_parse_database_success(self):
        dh = DataHandler()
        result = dh.parse_database(FIXTURE_PATH)
        assert 'parsed successfully' in result

    def test_parse_database_invalid_path(self):
        dh = DataHandler()
        result = dh.parse_database('/nonexistent/file.mm')
        assert 'Error' in result

    def test_get_statement_exists(self, handler):
        stmt = handler.get_statement('ax-1')
        assert stmt.label == 'ax-1'
        assert stmt.tag == '$a'

    def test_get_statement_not_found(self, handler):
        result = handler.get_statement('nonexistent')
        assert isinstance(result, str)
        assert 'not found' in result

    def test_get_statement_no_database(self):
        dh = DataHandler()
        result = dh.get_statement('ax-1')
        assert isinstance(result, str)
        assert 'Error' in result

    def test_search_index_built(self, handler):
        assert len(handler.search_index) > 0

    def test_find_statements_by_label(self, handler):
        results = handler.findStatements('ax-1')
        assert len(results) > 0
        assert results[0]['label'] == 'ax-1'

    def test_find_statements_by_keyword(self, handler):
        results = handler.findStatements('theorem')
        assert len(results) > 0

    def test_find_statements_empty_query(self, handler):
        results = handler.findStatements('')
        assert results == []

    def test_find_statements_no_database(self):
        dh = DataHandler()
        results = dh.findStatements('test')
        assert results == []

    def test_find_statements_returns_max_10(self, handler):
        results = handler.findStatements('a')
        assert len(results) <= 10
