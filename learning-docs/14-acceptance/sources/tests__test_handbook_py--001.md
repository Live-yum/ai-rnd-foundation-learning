# tests/test_handbook.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.build_handbook`、`scripts.rebuild_from_handbook`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_document_matches_every_source`（L8–L13）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L9断言`OUTPUT.read_text(encoding="utf-8") == render()`；L11遍历`sources()`；L12遍历`files`；L13断言`rows[name] == content`。 调用`OUTPUT.read_text`、`render`、`extract`、`sources`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_reconstruction_is_complete`（L16–L29）：接收`tmp_path`。 控制顺序：L29断言`(destination / OUTPUT.name).read_bytes() == OUTPUT.read_bytes()`。 调用`restore`、`subprocess.run`、`str`、`(destination / OUTPUT.name).read_bytes`、`OUTPUT.read_bytes`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `block`（L32–L36）：接收`name`、`content`。 调用`hashlib.sha256(content.encode()).hexdigest`、`hashlib.sha256`、`content.encode`。 返回路径：L36的`f"<!-- source-file: {name} sha256: {fingerprint} -->\n````python\n{content}````\n"`。
- `test_inline_marker_example_is_not_a_source_record`（L39–L43）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L41断言`extract(example + block("example.py", "answer = 42\n")) == { "example.py": "answer = …`。 调用`extract`、`block`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_reject_partial_duplicate_or_unsafe_source_before_writing`（L46–L73）：接收`tmp_path`。 控制顺序：L67遍历`enumerate(invalid)`；L73断言`not destination.exists()`。 调用`block`、`block("missing.py", "x = 1\n").removesuffix`、`block("corrupt.py", "x = 1\n").replace`、`enumerate`、`book.write_text`、`pytest.raises`、`restore`、`destination.exists`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_standalone_bootstrap_in_the_lesson_restores_all_files`（L76–L96）：接收`tmp_path`。 控制顺序：L93遍历`sources()`；L94遍历`files`；L96断言`(destination / name).read_bytes() == expected`。 调用`(ROOT / "docs/implementation.md").read_text`、`re.findall`、`next`、`script.write_text`、`subprocess.run`、`str`、`__import__`、`sources`、`isinstance`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_daytona_recipes_have_distinct_teaching_roles`（L99–L104）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L102断言`"Runner服务" in purpose("tools/daytona/runner.Dockerfile")[0]`；L103断言`"对象存储" in purpose("tools/daytona/minio.Dockerfile")[0]`；L104断言`"预热" in purpose("tools/daytona/Dockerfile")[0]`。 调用`purpose`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_handbook_ignores_nested_installed_dependencies`（L107–L118）：接收`tmp_path`、`monkeypatch`。 控制顺序：L113遍历`(".venv", "node_modules", ".git", ".data")`；L118断言`list(builder.sources()) == [("source", [("templates/product/app.py", "# source")])]`。 调用`source.mkdir`、`(source / "app.py").write_text`、`(source / cache).mkdir`、`(source / cache / "native.so").write_bytes`、`monkeypatch.setattr`、`list`、`builder.sources`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_roundtrip_preserves_empty_files_and_exact_trailing_newlines`（L121–L137）：接收`tmp_path`、`monkeypatch`。 控制顺序：L132遍历`original.items()`；L137断言`extract(builder.render()) == original`。 调用`original.items`、`(tmp_path / name).write_text`、`monkeypatch.setattr`、`list`、`extract`、`builder.render`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_binary_asset_roundtrip_preserves_exact_bytes_and_wrapping`（L140–L157）：接收`tmp_path`、`monkeypatch`。 控制顺序：L149断言`"encoding: base64" in text`；L150断言`"data:image" not in text`；L151断言`"<details>" in text`；L152断言`extract(text) == {"screenshot.png": data}`；L156断言`restore(book, destination) == 1`；L157断言`(destination / "screenshot.png").read_bytes() == data`。 调用`bytes`、`range`、`(tmp_path / "screenshot.png").write_bytes`、`monkeypatch.setattr`、`builder.render`、`extract`、`book.write_text`、`restore`、`(destination / "screenshot.png").read_bytes`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_reject_invalid_binary_before_writing`（L160–L188）：接收`tmp_path`。 控制顺序：L182遍历`enumerate(invalid)`；L188断言`not destination.exists()`。 调用`base64.b64encode(data).decode`、`base64.b64encode`、`hashlib.sha256(data).hexdigest`、`hashlib.sha256`、`valid.replace`、`base64.b64encode(b"changed").decode`、`valid.removesuffix`、`block`、`enumerate`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_chapter_images_are_rebased_only_in_readable_handbook`（L191–L203）：接收`tmp_path`、`monkeypatch`。 控制顺序：L202断言`text.startswith("![实际画面](docs/images/example.png)")`；L203断言`extract(text)["docs/lesson.md"] == source`。 调用`docs.mkdir`、`(docs / "lesson.md").write_text`、`monkeypatch.setattr`、`builder.render`、`text.startswith`、`extract`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_handbook.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L203。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`7523`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_handbook.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "792a5c8b2d0430482f84d4ee74245d2da076235b1e70e9cfd2081f7a0176a6c7"} -->
`````python
# tests/test_handbook.py
import subprocess
import sys

from scripts.build_handbook import OUTPUT, render, sources
from scripts.rebuild_from_handbook import extract, restore


def test_document_matches_every_source():
    assert OUTPUT.read_text(encoding="utf-8") == render()
    rows = extract(OUTPUT.read_text(encoding="utf-8"))
    for _, files in sources():
        for name, content in files:
            assert rows[name] == content


def test_reconstruction_is_complete(tmp_path):
    destination = tmp_path / "restored"
    restore(OUTPUT, destination)
    subprocess.run(
        [sys.executable, "-m", "compileall", "-q", str(destination / "workbench")], check=True
    )
    result = subprocess.run(
        [sys.executable, "-m", "scripts.build_handbook"],
        cwd=destination,
        text=True,
        capture_output=True,
        check=True,
    )
    assert (destination / OUTPUT.name).read_bytes() == OUTPUT.read_bytes(), result.stdout


def block(name, content):
    import hashlib

    fingerprint = hashlib.sha256(content.encode()).hexdigest()
    return f"<!-- source-file: {name} sha256: {fingerprint} -->\n````python\n{content}````\n"


def test_inline_marker_example_is_not_a_source_record():
    example = 'pattern = r"<!-- source-file: (.+?) sha256: ([0-9a-f]{64}) -->"\n'
    assert extract(example + block("example.py", "answer = 42\n")) == {
        "example.py": "answer = 42\n"
    }


def test_reject_partial_duplicate_or_unsafe_source_before_writing(tmp_path):
    import pytest

    valid = block("example.py", "answer = 42\n")
    invalid = [
        valid + valid,
        valid + block("missing.py", "x = 1\n").removesuffix("````\n"),
        valid + block("corrupt.py", "x = 1\n").replace("x = 1", "x = 2"),
    ]
    invalid += [
        block(name, "x = 1\n")
        for name in (
            "../escape.py",
            "/absolute.py",
            "a//alias.py",
            "./alias.py",
            ".",
            ".git/config",
            "C:drive.py",
        )
    ]
    for number, text in enumerate(invalid):
        book = tmp_path / f"bad-{number}.md"
        book.write_text(text)
        destination = tmp_path / f"must-stay-absent-{number}"
        with pytest.raises(ValueError):
            restore(book, destination)
        assert not destination.exists()


def test_standalone_bootstrap_in_the_lesson_restores_all_files(tmp_path):
    import re

    from scripts.build_handbook import ROOT

    lesson = (ROOT / "docs/implementation.md").read_text(encoding="utf-8")
    candidates = re.findall(r"```python\n(.*?)\n```", lesson, re.S)
    bootstrap = next(code for code in candidates if "rebuild_book.py" in code)
    script = tmp_path / "rebuild_book.py"
    script.write_text(bootstrap, encoding="utf-8")
    destination = tmp_path / "student-project"
    subprocess.run(
        [sys.executable, str(script), str(OUTPUT), str(destination)],
        check=True,
        env={**__import__("os").environ, "PYTHONIOENCODING": "cp1252"},
        capture_output=True,
    )
    for _, files in sources():
        for name, content in files:
            expected = content if isinstance(content, bytes) else content.encode("utf-8")
            assert (destination / name).read_bytes() == expected


def test_daytona_recipes_have_distinct_teaching_roles():
    from scripts.handbook_notes import purpose

    assert "Runner服务" in purpose("tools/daytona/runner.Dockerfile")[0]
    assert "对象存储" in purpose("tools/daytona/minio.Dockerfile")[0]
    assert "预热" in purpose("tools/daytona/Dockerfile")[0]


def test_handbook_ignores_nested_installed_dependencies(tmp_path, monkeypatch):
    import scripts.build_handbook as builder

    source = tmp_path / "templates/product"
    source.mkdir(parents=True)
    (source / "app.py").write_text("# source", encoding="utf-8")
    for cache in (".venv", "node_modules", ".git", ".data"):
        (source / cache).mkdir()
        (source / cache / "native.so").write_bytes(b"\xff\x00")
    monkeypatch.setattr(builder, "ROOT", tmp_path)
    monkeypatch.setattr(builder, "GROUPS", [("source", ["templates"])])
    assert list(builder.sources()) == [("source", [("templates/product/app.py", "# source")])]


def test_roundtrip_preserves_empty_files_and_exact_trailing_newlines(tmp_path, monkeypatch):
    import scripts.build_handbook as builder

    original = {
        "empty.py": "",
        "one-newline.txt": "\n",
        "no-newline.py": "answer = 42",
        "regular.py": "answer = 42\n",
        "trailing.py": "answer = 42\n\n\n",
        "nested.md": "````\ninside a code fence\n````\n",
    }
    for name, content in original.items():
        (tmp_path / name).write_text(content, encoding="utf-8")
    monkeypatch.setattr(builder, "ROOT", tmp_path)
    monkeypatch.setattr(builder, "GUIDES", [])
    monkeypatch.setattr(builder, "GROUPS", [("source", list(original))])
    assert extract(builder.render()) == original


def test_binary_asset_roundtrip_preserves_exact_bytes_and_wrapping(tmp_path, monkeypatch):
    import scripts.build_handbook as builder

    data = b"\x89PNG\r\n\x1a\n\x00\xff" + bytes(range(256))
    (tmp_path / "screenshot.png").write_bytes(data)
    monkeypatch.setattr(builder, "ROOT", tmp_path)
    monkeypatch.setattr(builder, "GUIDES", [])
    monkeypatch.setattr(builder, "GROUPS", [("assets", ["screenshot.png"])])
    text = builder.render()
    assert "encoding: base64" in text
    assert "data:image" not in text
    assert "<details>" in text
    assert extract(text) == {"screenshot.png": data}
    book = tmp_path / "book.md"
    book.write_text(text, encoding="utf-8")
    destination = tmp_path / "restored"
    assert restore(book, destination) == 1
    assert (destination / "screenshot.png").read_bytes() == data


def test_reject_invalid_binary_before_writing(tmp_path):
    import base64
    import hashlib

    import pytest

    data = b"\x89PNG\x00\xff"
    encoded = base64.b64encode(data).decode("ascii")
    fingerprint = hashlib.sha256(data).hexdigest()
    valid = (
        f"<!-- source-file: image.png sha256: {fingerprint} encoding: base64 -->\n"
        f"````base64\n{encoded}\n````\n"
    )
    invalid = [
        valid.replace(encoded, "!not-base64!"),
        valid.replace(encoded, base64.b64encode(b"changed").decode("ascii")),
        valid.replace("encoding: base64", "encoding: unknown"),
        valid.removesuffix("````\n"),
        valid + valid,
        valid + block("image.png", "duplicate path\n"),
        valid.replace("image.png", "../image.png"),
    ]
    for number, text in enumerate(invalid):
        book = tmp_path / f"binary-bad-{number}.md"
        book.write_text(block("safe.py", "answer = 42\n") + text, encoding="utf-8")
        destination = tmp_path / f"absent-{number}"
        with pytest.raises(ValueError):
            restore(book, destination)
        assert not destination.exists()


def test_chapter_images_are_rebased_only_in_readable_handbook(tmp_path, monkeypatch):
    import scripts.build_handbook as builder

    source = "![实际画面](images/example.png)\n"
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "lesson.md").write_text(source, encoding="utf-8")
    monkeypatch.setattr(builder, "ROOT", tmp_path)
    monkeypatch.setattr(builder, "GUIDES", ["docs/lesson.md"])
    monkeypatch.setattr(builder, "GROUPS", [("docs", ["docs/lesson.md"])])
    text = builder.render()
    assert text.startswith("![实际画面](docs/images/example.png)")
    assert extract(text)["docs/lesson.md"] == source
`````
