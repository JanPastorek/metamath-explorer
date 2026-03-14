import os
import sys
import pytest

# Add src to path so we can import app modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from app.data.metamath import parse, Statement, Database

FIXTURE_PATH = os.path.join(os.path.dirname(__file__), 'fixtures', 'test.mm')


class TestMetamathParser:
    """Tests for the Metamath (.mm) file parser."""

    def test_parse_returns_database(self):
        db = parse(FIXTURE_PATH)
        assert isinstance(db, Database)

    def test_parse_finds_all_statements(self):
        db = parse(FIXTURE_PATH)
        expected_labels = {'wph', 'wps', 'wch', 'ax-1', 'ax-2', 'min', 'maj', 'ax-mp', 'a1i.1', 'a1i'}
        assert set(db.statements.keys()) == expected_labels

    def test_parse_finds_all_rules(self):
        db = parse(FIXTURE_PATH)
        assert 'ax-1' in db.rules
        assert 'ax-mp' in db.rules
        assert 'a1i' in db.rules

    def test_statement_tags(self):
        db = parse(FIXTURE_PATH)
        assert db.statements['wph'].tag == '$f'
        assert db.statements['ax-1'].tag == '$a'
        assert db.statements['min'].tag == '$e'
        assert db.statements['a1i'].tag == '$p'

    def test_statement_tokens(self):
        db = parse(FIXTURE_PATH)
        assert db.statements['wph'].tokens == ['wff', 'ph']
        assert db.statements['ax-1'].tokens[0] == '|-'

    def test_proposition_has_proof(self):
        db = parse(FIXTURE_PATH)
        stmt = db.statements['a1i']
        assert stmt.proof == ['(', 'ax-1', 'ax-mp', ')']

    def test_axiom_has_no_proof(self):
        db = parse(FIXTURE_PATH)
        stmt = db.statements['ax-1']
        assert stmt.proof == []

    def test_proved_from_extraction(self):
        db = parse(FIXTURE_PATH)
        stmt = db.statements['a1i']
        assert 'ax-1' in stmt.proved_from_statements
        assert 'ax-mp' in stmt.proved_from_statements

    def test_references_filled(self):
        db = parse(FIXTURE_PATH)
        # ax-1 is used in proof of a1i, so a1i should reference ax-1
        assert 'a1i' in db.statements['ax-1'].is_referenced_by
        assert 'a1i' in db.statements['ax-mp'].is_referenced_by

    def test_comments_associated(self):
        db = parse(FIXTURE_PATH)
        assert 'Simplification theorem' in db.statements['ax-1'].comment
        assert 'Modus Ponens' in db.statements['ax-mp'].comment

    def test_statement_str(self):
        db = parse(FIXTURE_PATH)
        s = str(db.statements['ax-1'])
        assert 'ax-1' in s
        assert '$a' in s

    def test_parse_nonexistent_file_raises(self):
        with pytest.raises(FileNotFoundError):
            parse('/nonexistent/file.mm')

    def test_parse_max_rules(self):
        db = parse(FIXTURE_PATH, max_rules=3)
        assert len(db.rules) <= 3


class TestStatement:
    """Tests for the Statement class."""

    def test_init(self):
        stmt = Statement('test', '$a', ['|-', 'ph'], [])
        assert stmt.label == 'test'
        assert stmt.tag == '$a'
        assert stmt.tokens == ['|-', 'ph']
        assert stmt.proof == []
        assert stmt.comment == ''

    def test_extract_statements_from_parentheses(self):
        stmt = Statement('test', '$p', ['|-', 'ph'], ['(', 'ax-1', 'ax-2', ')'])
        stmt.extract_statements_from()
        assert stmt.proved_from_statements == ['ax-1', 'ax-2']

    def test_extract_statements_no_parentheses(self):
        stmt = Statement('test', '$a', ['|-', 'ph'], ['ax-1', 'ax-2'])
        stmt.extract_statements_from()
        # No parentheses, so proved_from_statements should remain empty
        assert stmt.proved_from_statements == []

    def test_put_statement_in_ref(self):
        stmt = Statement('test', '$a', [], [])
        stmt.put_statement_in_ref('other')
        assert 'other' in stmt.is_referenced_by

    def test_get_statements(self):
        stmt = Statement('test', '$p', [], ['(', 'a', 'b', ')'])
        stmt.extract_statements_from()
        assert stmt.get_statements() == ['a', 'b']
