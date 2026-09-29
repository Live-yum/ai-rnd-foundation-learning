"""One-shot reviewed source normalization; removed before final source archive."""
from pathlib import Path

path = Path('workbench/retrieval.py')
text = path.read_text(encoding='utf-8')
assert text.count('with sqlite3.connect(') == 5
text = text.replace('import tempfile\n', 'import tempfile\nfrom contextlib import closing\n')
text = text.replace('with sqlite3.connect(target) as db:', 'with closing(sqlite3.connect(target)) as db:')
text = text.replace('with sqlite3.connect(temporary) as db:', 'with closing(sqlite3.connect(temporary)) as db, db:')
text = text.replace('with sqlite3.connect(target) as old_db:', 'with closing(sqlite3.connect(target)) as old_db:')
text = text.replace('with sqlite3.connect(Path(index_dir) / "search.sqlite3") as db:', 'with closing(sqlite3.connect(Path(index_dir) / "search.sqlite3")) as db, db:')
assert 'with sqlite3.connect(' not in text
path.write_text(text, encoding='utf-8')
Path(__file__).unlink()
