"""Match the pinned YuDao PostgreSQL schema, not a guessed cross-framework audit type."""
from pathlib import Path

path = Path('workbench/native_modules.py')
source = path.read_text(encoding='utf-8')
before = 'Column("deleted", Boolean, nullable=False, server_default=text("false"))'
after = 'Column("deleted", SmallInteger, nullable=False, server_default=text("0"))'
if before in source:
    assert source.count(before) == 1
    source = source.replace('    Integer,\n', '    Integer,\n    SmallInteger,\n', 1)
    source = source.replace(before, after, 1)
else:
    assert after in source
path.write_text(source, encoding='utf-8', newline='\n')
path = Path('tests/test_native_modules.py')
source = path.read_text(encoding='utf-8')
if 'def test_yudao_logic_delete_matches_pinned_postgres_seed' not in source:
    source += '''

def test_yudao_logic_delete_matches_pinned_postgres_seed():
    from sqlalchemy import SmallInteger
    _, tables, _ = native_metadata('yudao-vben', acceptance_spec(), URL, 'logic-delete')
    assert isinstance(tables[0].c.deleted.type, SmallInteger)
    assert str(tables[0].c.deleted.server_default.arg) == '0'
    assert 'deleted SMALLINT' in str(CreateTable(tables[0]).compile(dialect=postgresql.dialect()))
'''
path.write_text(source, encoding='utf-8', newline='\n')
print('Native logic delete PostgreSQL metadata corrected')
