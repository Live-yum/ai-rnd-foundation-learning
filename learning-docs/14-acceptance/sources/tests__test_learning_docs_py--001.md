# tests/test_learning_docs.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `fingerprint`（L21–L22）：接收`data`。 调用`hashlib.sha256(data).hexdigest`、`hashlib.sha256`。 返回路径：L22的`hashlib.sha256(data).hexdigest()`。
- `assert_exact_bytes`（L25–L30）：接收`actual`、`expected`、`name`。 控制顺序：L26按`actual != expected`分支。 调用`pytest.fail`、`len`、`fingerprint`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `assert_exact_inventory`（L33–L38）：接收`actual`、`expected`。 控制顺序：L36断言`not missing and not extra`；L37遍历`expected.items()`。 调用`sorted`、`expected.keys`、`actual.keys`、`expected.items`、`assert_exact_bytes`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `source_block`（L41–L64）：接收`name`、`data`、`part`、`parts`、`language`、`encoding`。 调用`fingerprint`、`base64.b64encode(data).decode`、`base64.b64encode`、`data.decode`、`max`、`len`、`re.findall`、`json.dumps`、`reader.comment_line`等。 返回路径：L51的`"<!-- learning-source: " + json.dumps(metadata) + " -->\n" + fence + language + "\n" + rea…`。
- `make_bundle`（L67–L104）：接收`folder`、`entries`。 源码说明：An independent tiny publisher: do not use the production generator for parser tests.。 控制顺序：L69按`entries is None`分支；L73遍历`enumerate(entries)`；L75遍历`enumerate(chunks, 1)`。 调用`folder.mkdir`、`enumerate`、`page.parent.mkdir`、`page.write_text`、`source_block`、`len`、`documents.append`、`b"".join`、`rows.append`等。 返回路径：L104的`manifest`。
- `write_manifest`（L107–L108）：接收`folder`、`manifest`。 调用`(folder / "manifest.json").write_text`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `replace_metadata`（L111–L117）：接收`folder`、`manifest`、`mutation`。 调用`path.read_text`、`text.split`、`json.loads`、`len`、`mutation`、`path.write_text`、`json.dumps`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `assert_rejected_before_writing`（L120–L123）：接收`folder`、`destination`。 控制顺序：L123断言`not destination.exists()`。 调用`pytest.raises`、`reader.restore`、`destination.exists`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_every_language_has_a_path_annotation_in_the_actual_first_line`（L148–L150）：接收`language`、`name`。 控制顺序：L150断言`reader.check_fences(text) == 1`。 调用`reader.comment_line`、`reader.check_fences`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_missing_or_invalid_annotation_in_any_markdown_fence_is_rejected`（L173–L175）：接收`text`。 调用`pytest.raises`、`reader.check_fences`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_nested_fences_are_payload_not_extra_fences`（L178–L180）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L180断言`reader.check_fences(text) == 1`。 调用`reader.check_fences`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_exact_empty_file_and_final_newline_bytes`（L184–L190）：接收`data`、`tmp_path`。 控制顺序：L187断言`reader.read_bundle(folder) == {"sample.py": data}`；L189断言`reader.restore(folder, destination) == 1`；L190断言`(destination / "sample.py").read_bytes() == data`。 调用`make_bundle`、`reader.read_bundle`、`reader.restore`、`(destination / "sample.py").read_bytes`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_unicode_multipart_json_and_binary_strip_only_the_instructional_comment`（L193–L204）：接收`tmp_path`。 控制顺序：L203断言`result == {"config/settings.json": json_data, "docs/images/test.png": png}`；L204断言`json.loads(result["config/settings.json"])["count"] == 0`。 调用`'{"客户": "中文", "count": 0, "enabled": false}\n'.encode`、`bytes`、`range`、`make_bundle`、`reader.read_bundle`、`json.loads`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_nested_literal_source_marker_is_source_data`（L207–L216）：接收`tmp_path`。 控制顺序：L216断言`reader.read_bundle(folder) == {"docs/nested.md": content}`。 调用`( "Nested source examples are ordinary Markdown.\n" + reader.MARK…`、`make_bundle`、`reader.read_bundle`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_unknown_manifest_version_never_restores`（L220–L225）：接收`version`、`tmp_path`。 调用`make_bundle`、`write_manifest`、`assert_rejected_before_writing`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_non_object_manifest_is_a_validation_error`（L229–L233）：接收`document`、`tmp_path`。 调用`make_bundle`、`write_manifest`、`assert_rejected_before_writing`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_manifest_byte_count_cannot_use_boolean_in_place_of_one`（L236–L241）：接收`tmp_path`。 调用`make_bundle`、`write_manifest`、`assert_rejected_before_writing`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_non_object_source_metadata_is_a_validation_error`（L245–L251）：接收`metadata`、`tmp_path`。 调用`make_bundle`、`page.read_text(encoding="utf-8").split`、`page.read_text`、`page.write_text`、`json.dumps`、`assert_rejected_before_writing`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_malformed_manifest_is_a_validation_error_before_any_write`（L273–L278）：接收`mutation`、`tmp_path`。 调用`make_bundle`、`mutation`、`write_manifest`、`assert_rejected_before_writing`、`pytest.mark.parametrize`、`m.pop`、`m.update`、`m["files"][0].pop`、`m["files"][0].update`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_wrong_part_identity_or_hash_rejects_before_writing`（L294–L298）：接收`changes`、`tmp_path`。 调用`make_bundle`、`replace_metadata`、`meta.update`、`assert_rejected_before_writing`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_unsafe_or_reserved_source_paths_are_rejected`（L317–L322）：接收`name`、`tmp_path`。 调用`make_bundle`、`write_manifest`、`assert_rejected_before_writing`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_source_and_annotation_paths_must_agree`（L325–L330）：接收`tmp_path`。 调用`make_bundle`、`page.write_text`、`page.read_text().replace`、`page.read_text`、`assert_rejected_before_writing`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_missing_duplicate_and_unlisted_source_documents_fail_atomically`（L336–L351）：接收`damage`、`tmp_path`。 控制顺序：L341按`damage == "missing"`分支；L343按`damage == "duplicate"`分支；L345按`damage == "truncated"`分支；L347按`damage == "extra"`分支。 调用`make_bundle`、`page.read_text`、`page.unlink`、`page.write_text`、`text.rsplit`、`(page.parent / "unlisted.md").write_text`、`(folder / "unlisted.md").write_text`、`assert_rejected_before_writing`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_corrupt_later_stage_prevents_even_early_stage_write`（L354–L366）：接收`tmp_path`。 控制顺序：L366断言`not (tmp_path / "student").exists()`。 调用`make_bundle`、`(folder / manifest["files"][1]["parts"][0]).unlink`、`pytest.raises`、`reader.restore`、`(tmp_path / "student").exists`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_binary_corruption_fails_before_writing`（L369–L378）：接收`tmp_path`。 调用`make_bundle`、`page.write_text`、`page.read_text().replace`、`page.read_text`、`base64.b64encode(b"\x89PNG\x00\xff").decode`、`base64.b64encode`、`assert_rejected_before_writing`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_progress_ledger_cannot_also_be_a_source_directory`（L381–L387）：接收`tmp_path`。 调用`make_bundle`、`assert_rejected_before_writing`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_source_file_ancestor_conflict_is_rejected_before_any_write`（L390–L399）：接收`tmp_path`。 调用`make_bundle`、`assert_rejected_before_writing`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `link_or_skip`（L402–L406）：接收`path`、`target`、`directory`。 调用`path.symlink_to`、`pytest.skip`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_symlink_roots_ancestors_and_source_entries_are_rejected`（L412–L436）：接收`kind`、`tmp_path`。 控制顺序：L418按`kind == "destination"`分支；L420按`kind == "ancestor"`分支；L423按`kind == "bundle-ancestor"`分支；L434断言`not (outside / "example.py").exists()`；L435按`kind != "destination"`分支；L436断言`not destination.exists()`。 调用`make_bundle`、`outside.mkdir`、`link_or_skip`、`page.rename`、`pytest.raises`、`reader.restore`、`(outside / "example.py").exists`、`destination.exists`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_nonempty_destination_is_untouched_without_explicit_advance`（L439–L447）：接收`tmp_path`。 控制顺序：L447断言`{p.name: p.read_bytes() for p in destination.iterdir()} == {"mine.txt": b"keep me"}`。 调用`make_bundle`、`destination.mkdir`、`(destination / "mine.txt").write_bytes`、`pytest.raises`、`reader.restore`、`p.read_bytes`、`destination.iterdir`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `two_stage_bundle`（L450–L457）：接收`folder`。 调用`make_bundle`。 返回路径：L451的`make_bundle( folder, [ ("early.py", [b"early\n"], "00-environment", "python", "utf-8"), ("…`。
- `test_advancement_is_cumulative_and_preserves_unrelated_student_notes`（L460–L471）：接收`tmp_path`。 控制顺序：L463断言`reader.restore(folder, destination, through="00") == 1`；L464断言`not (destination / "late.py").exists()`；L466断言`reader.restore(folder, destination, through="01-contracts", advance=True) == 2`；L467断言`(destination / "early.py").read_bytes() == b"early\n"`；L468断言`(destination / "late.py").read_bytes() == b"late\n"`；L469断言`(destination / "my-notes.txt").read_bytes() == b"personal notes"`。 调用`two_stage_bundle`、`reader.restore`、`(destination / "late.py").exists`、`(destination / "my-notes.txt").write_bytes`、`(destination / "early.py").read_bytes`、`(destination / "late.py").read_bytes`、`(destination / "my-notes.txt").read_bytes`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_advancement_never_overwrites_an_edited_prior_stage`（L474–L482）：接收`tmp_path`。 控制顺序：L481断言`(destination / "early.py").read_bytes() == b"my change\n"`；L482断言`not (destination / "late.py").exists()`。 调用`two_stage_bundle`、`reader.restore`、`(destination / "early.py").write_bytes`、`pytest.raises`、`(destination / "early.py").read_bytes`、`(destination / "late.py").exists`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_invalid_progress_ledger_never_advances_or_overwrites`（L486–L494）：接收`document`、`tmp_path`。 控制顺序：L493断言`(destination / "early.py").read_bytes() == b"early\n"`；L494断言`not (destination / "late.py").exists()`。 调用`two_stage_bundle`、`reader.restore`、`(destination / reader.LEDGER).write_text`、`json.dumps`、`pytest.raises`、`(destination / "early.py").read_bytes`、`(destination / "late.py").exists`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_future_target_symlink_cannot_be_followed_during_advancement`（L497–L506）：接收`tmp_path`。 控制顺序：L506断言`outside.read_bytes() == b"untouched"`。 调用`two_stage_bundle`、`reader.restore`、`outside.write_bytes`、`link_or_skip`、`pytest.raises`、`outside.read_bytes`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_unknown_stage_is_rejected_before_any_write`（L509–L514）：接收`tmp_path`。 控制顺序：L514断言`not (tmp_path / "student").exists()`。 调用`make_bundle`、`pytest.raises`、`reader.restore`、`(tmp_path / "student").exists`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_published_learning_docs_match_deterministic_render`（L517–L535）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L533遍历`expected.items()`；L534按`name.endswith(".md")`分支。 调用`builder.render`、`path.relative_to(builder.OUTPUT).as_posix`、`path.relative_to`、`path.read_bytes`、`builder.OUTPUT.rglob`、`path.is_file`、`assert_exact_inventory`、`isinstance`、`content.encode`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `prose_outside_fences`（L538–L553）：接收`text`。 源码说明：Independent CommonMark-style scanner so nested source links are never followed.。 控制顺序：L541遍历`text.splitlines()`；L542按`opened is not None`分支；L544按`re.fullmatch(r" {0,3}" + re.escape(character) + "{" + str(width) + r",}\s*", line)`分支；L548按`match and not (match[1][0] == "`" and "`" in match[2])`分支；L552断言`opened is None`。 调用`text.splitlines`、`re.fullmatch`、`re.escape`、`str`、`len`、`result.append`、`"\n".join`。 返回路径：L553的`"\n".join(result)`。
- `prose_outside_inline_code`（L556–L570）：接收`text`。 控制顺序：L559在`opening := runs.search(text, position)`成立时循环；L563按`closing is None`分支。 调用`re.compile`、`runs.search`、`re.compile(r"(?<!`)" + re.escape(opening[0]) + r"(?!`)").search`、`re.escape`、`opening.end`、`result.append`、`opening.start`、`closing.end`、`"".join`。 返回路径：L570的`"".join(result)`。
- `test_all_local_links_outside_source_fences_resolve_inside_the_bundle`（L573–L587）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L578遍历`sorted(builder.OUTPUT.rglob("*.md"))`；L580遍历`re.findall(r"\[[^\]\n]*\]\(([^)\n]+)\)", prose)`；L582按`url.scheme or url.netloc or not url.path`分支；L585按`not path.is_relative_to(root) or not path.is_file()`分支；L587断言`not failures`。 调用`builder.OUTPUT.resolve`、`sorted`、`builder.OUTPUT.rglob`、`prose_outside_inline_code`、`prose_outside_fences`、`page.read_text`、`re.findall`、`urlsplit`、`target.strip().removeprefix("<").removesuffix`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_manifest_covers_owned_tracked_sources_independently_of_generator_groups`（L590–L624）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L602按`not (ROOT / ".git").exists()`分支；L617断言`not owned - rows.keys()`；L618断言`not rows.keys() & excluded`；L619断言`not any(name.startswith("learning-docs/") for name in rows)`；L620断言`"tests/test_learning_docs.py" in rows`；L621断言`"scripts/rebuild_learning_docs.py" in rows`；L622断言`"scripts/build_learning_docs.py" in rows`；L623断言`"uv.lock" in rows and "tools/node/package-lock.json" in rows`。后续分支沿下方源码相同行号继续阅读。 调用`reader.read_bundle`、`isinstance`、`content.encode`、`builder.sources`、`assert_exact_inventory`、`(ROOT / ".git").exists`、`set`、`subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT) .dec…`、`subprocess.check_output`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_docs_only_bootstrap_runs_isolated_with_original_tree_reads_forbidden`（L627–L668）：接收`tmp_path`。 控制顺序：L664断言`result.returncode == 0`；L665遍历`reader.read_bundle(docs).items()`；L667断言`not (destination / ".git").exists()`；L668断言`not list((destination / "templates/vendor").glob("*.zip"))`。 调用`shutil.copytree`、`assert_exact_bytes`、`(docs / "rebuild.py").read_bytes`、`(ROOT / "scripts/rebuild_learning_docs.py").read_bytes`、`launch.write_text`、`subprocess.run`、`str`、`os.environ.items`、`reader.read_bundle(docs).items`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_multi_part_navigation_has_no_dangling_separator_or_trailing_space`（L671–L690）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L679断言`len(record["parts"]) == 3`；L680遍历`enumerate(record["parts"])`；L686断言`len(navigation) == 1`；L688断言`line == line.rstrip()`；L689断言`not line.endswith(" ·")`；L690断言`line.count("](") == (2 if index == 1 else 1)`。 调用`"".join`、`range`、`builder.source_pages`、`len`、`enumerate`、`prose_outside_fences(pages[name]).splitlines`、`prose_outside_fences`、`line.startswith`、`line.rstrip`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_repacked_vendor_manifest_blocks_advance_but_clean_full_restore_is_safe`（L693–L729）：接收`tmp_path`。 控制顺序：L717遍历`("name", "sha", "source_digest", "files")`；L718断言`repacked["sources"][0][key] == original["sources"][0][key]`；L724断言`vendor.read_bytes() == changed`；L725断言`not (old / "later.py").exists()`；L726断言`reader.restore(book, complete) == 2`；L727断言`(complete / "templates/vendor/manifest.json").read_bytes() == encoded`；L728断言`(complete / "later.py").read_bytes() == b"answer = 42\n"`；L729断言`vendor.read_bytes() == changed`。 调用`(json.dumps(original) + "\n").encode`、`json.dumps`、`make_bundle`、`reader.restore`、`json.loads`、`(json.dumps(repacked) + "\n").encode`、`vendor.write_bytes`、`pytest.raises`、`vendor.read_bytes`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_learning_docs.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L729。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`27786`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_learning_docs.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "d2b371cbb8d9abf4ddb18944fe82ef9b7845accac60c146282daa45c88ef02e6"} -->
``````python
# tests/test_learning_docs.py
"""Independent source coverage, byte-exact reconstruction, and fail-before-write contracts."""

import base64
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

import pytest

from scripts import rebuild_learning_docs as reader

ROOT = Path(__file__).resolve().parents[1]


def fingerprint(data):
    return hashlib.sha256(data).hexdigest()


def assert_exact_bytes(actual, expected, name):
    if actual != expected:
        pytest.fail(
            f"Byte mismatch: {name}; expected {len(expected)} bytes / {fingerprint(expected)}, "
            f"got {len(actual)} bytes / {fingerprint(actual)}"
        )


def assert_exact_inventory(actual, expected):
    missing = sorted(expected.keys() - actual.keys())
    extra = sorted(actual.keys() - expected.keys())
    assert not missing and not extra, f"Missing files: {missing}; unexpected files: {extra}"
    for name, data in expected.items():
        assert_exact_bytes(actual[name], data, name)


def source_block(name, data, *, part=1, parts=1, language="python", encoding="utf-8"):
    metadata = {
        "path": name,
        "part": part,
        "parts": parts,
        "encoding": encoding,
        "sha256": fingerprint(data),
    }
    payload = base64.b64encode(data).decode("ascii") if encoding == "base64" else data.decode()
    fence = "`" * max(4, max((len(run) for run in re.findall(r"`+", payload)), default=0) + 1)
    return (
        "<!-- learning-source: "
        + json.dumps(metadata)
        + " -->\n"
        + fence
        + language
        + "\n"
        + reader.comment_line(name, language)
        + "\n"
        + payload
        + ("" if payload.endswith("\n") else "\n")
        + fence
        + "\n"
    )


def make_bundle(folder, entries=None):
    """An independent tiny publisher: do not use the production generator for parser tests."""
    if entries is None:
        entries = [("example.py", [b"answer = 42\n"], "00-environment", "python", "utf-8")]
    folder.mkdir(parents=True, exist_ok=True)
    rows = []
    for index, (name, chunks, stage, language, encoding) in enumerate(entries):
        documents = []
        for part, chunk in enumerate(chunks, 1):
            relative = f"{stage}/sources/{index}-{part}.md"
            page = folder / relative
            page.parent.mkdir(parents=True, exist_ok=True)
            page.write_text(
                source_block(
                    name,
                    chunk,
                    part=part,
                    parts=len(chunks),
                    language=language,
                    encoding=encoding,
                ),
                encoding="utf-8",
                newline="\n",
            )
            documents.append(relative)
        data = b"".join(chunks)
        rows.append(
            {
                "path": name,
                "sha256": fingerprint(data),
                "bytes": len(data),
                "stage": stage,
                "parts": documents,
            }
        )
    manifest = {"format": 1, "files": rows}
    write_manifest(folder, manifest)
    return manifest


def write_manifest(folder, manifest):
    (folder / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")


def replace_metadata(folder, manifest, mutation):
    path = folder / manifest["files"][0]["parts"][0]
    text = path.read_text(encoding="utf-8")
    marker, rest = text.split("\n", 1)
    metadata = json.loads(marker[len(reader.MARKER) : -4])
    mutation(metadata)
    path.write_text(reader.MARKER + json.dumps(metadata) + " -->\n" + rest, encoding="utf-8")


def assert_rejected_before_writing(folder, destination):
    with pytest.raises(ValueError):
        reader.restore(folder, destination)
    assert not destination.exists(), "A corrupt bundle must fail before creating any target files"


@pytest.mark.parametrize(
    "language,name",
    [
        ("python", "scripts/example.py"),
        ("bash", "commands/install.sh"),
        ("powershell", "commands/install.ps1"),
        ("json", "config/example.json"),
        ("markdown", "docs/example.md"),
        ("base64", "docs/images/example.png"),
        ("toml", "uv.lock"),
        ("yaml", ".github/workflows/test.yml"),
        ("javascript", "tools/example.cjs"),
        ("typescript", "tools/example.ts"),
        ("java", "examples/Example.java"),
        ("vue", "templates/Example.vue"),
        ("html", "workbench/web/index.html"),
        ("css", "workbench/web/style.css"),
        ("sql", "migrations/example.sql"),
        ("ini", "alembic.ini"),
        ("text", ".python-version"),
    ],
)
def test_every_language_has_a_path_annotation_in_the_actual_first_line(language, name):
    text = f"```{language}\n{reader.comment_line(name, language)}\ncontent\n```\n"
    assert reader.check_fences(text) == 1


@pytest.mark.parametrize(
    "text",
    [
        "```python\nprint(42)\n```\n",
        "```json\n{}\n```\n",
        "```markdown\n# Ordinary heading\n```\n",
        "```base64\neA==\n```\n",
        "```bash\necho ready\n```\n",
        "```python\n\n# example.py\n```\n",
        "```python\n# ../outside.py\nx = 1\n```\n",
        "```python\n# /absolute.py\nx = 1\n```\n",
        "```python\n# .git/config\nx = 1\n```\n",
        "```python\n# C:drive.py\nx = 1\n```\n",
        "```json\n# config.json\n{}\n```\n",
        "```python\n# example.py\nx = 1\n",
        "```\n```\n",
        " ```python\nprint(42)\n ```\n",
        "```python title=example\nprint(42)\n```\n",
    ],
)
def test_missing_or_invalid_annotation_in_any_markdown_fence_is_rejected(text):
    with pytest.raises(ValueError):
        reader.check_fences(text)


def test_nested_fences_are_payload_not_extra_fences():
    text = "`````markdown\n<!-- docs/example.md -->\n```python\nprint(42)\n```\n`````\n"
    assert reader.check_fences(text) == 1


@pytest.mark.parametrize("data", [b"", b"\n", b"answer = 42", b"answer = 42\n", b"x\n\n\n"])
def test_exact_empty_file_and_final_newline_bytes(data, tmp_path):
    folder = tmp_path / "book"
    make_bundle(folder, [("sample.py", [data], "00-environment", "python", "utf-8")])
    assert reader.read_bundle(folder) == {"sample.py": data}
    destination = tmp_path / "student"
    assert reader.restore(folder, destination) == 1
    assert (destination / "sample.py").read_bytes() == data


def test_unicode_multipart_json_and_binary_strip_only_the_instructional_comment(tmp_path):
    folder = tmp_path / "book"
    json_data = '{"客户": "中文", "count": 0, "enabled": false}\n'.encode()
    png = b"\x89PNG\r\n\x1a\n\x00\xff" + bytes(range(256))
    entries = [
        ("config/settings.json", [json_data[:2], json_data[2:]], "00-environment", "json", "utf-8"),
        ("docs/images/test.png", [png[:7], png[7:]], "01-contracts", "base64", "base64"),
    ]
    make_bundle(folder, entries)
    result = reader.read_bundle(folder)
    assert result == {"config/settings.json": json_data, "docs/images/test.png": png}
    assert json.loads(result["config/settings.json"])["count"] == 0


def test_nested_literal_source_marker_is_source_data(tmp_path):
    folder = tmp_path / "book"
    content = (
        "Nested source examples are ordinary Markdown.\n"
        + reader.MARKER
        + '{"path": "not-a-real-entry.py"} -->\n'
        + "```python\nprint('nested example')\n```\n"
    ).encode()
    make_bundle(folder, [("docs/nested.md", [content], "00-environment", "markdown", "utf-8")])
    assert reader.read_bundle(folder) == {"docs/nested.md": content}


@pytest.mark.parametrize("version", [0, 2, "1", True, None])
def test_unknown_manifest_version_never_restores(version, tmp_path):
    folder = tmp_path / "book"
    manifest = make_bundle(folder)
    manifest["format"] = version
    write_manifest(folder, manifest)
    assert_rejected_before_writing(folder, tmp_path / "student")


@pytest.mark.parametrize("document", [[], None, 1, "manifest"])
def test_non_object_manifest_is_a_validation_error(document, tmp_path):
    folder = tmp_path / "book"
    make_bundle(folder)
    write_manifest(folder, document)
    assert_rejected_before_writing(folder, tmp_path / "student")


def test_manifest_byte_count_cannot_use_boolean_in_place_of_one(tmp_path):
    folder = tmp_path / "book"
    manifest = make_bundle(folder, [("one.txt", [b"x"], "00-environment", "text", "utf-8")])
    manifest["files"][0]["bytes"] = True
    write_manifest(folder, manifest)
    assert_rejected_before_writing(folder, tmp_path / "student")


@pytest.mark.parametrize("metadata", [[], None, 1, "metadata"])
def test_non_object_source_metadata_is_a_validation_error(metadata, tmp_path):
    folder = tmp_path / "book"
    manifest = make_bundle(folder)
    page = folder / manifest["files"][0]["parts"][0]
    _, rest = page.read_text(encoding="utf-8").split("\n", 1)
    page.write_text(reader.MARKER + json.dumps(metadata) + " -->\n" + rest, encoding="utf-8")
    assert_rejected_before_writing(folder, tmp_path / "student")


@pytest.mark.parametrize(
    "mutation",
    [
        lambda m: m.pop("files"),
        lambda m: m.update(files=[]),
        lambda m: m.update(files="not a list"),
        lambda m: m.update(files=[None]),
        lambda m: m["files"][0].pop("path"),
        lambda m: m["files"][0].update(path=None),
        lambda m: m["files"][0].update(stage=0),
        lambda m: m["files"][0].update(stage="not-a-stage"),
        lambda m: m["files"][0].update(bytes=999),
        lambda m: m["files"][0].update(sha256="0" * 64),
        lambda m: m["files"][0].update(parts=[]),
        lambda m: m["files"][0].update(parts="a.md"),
        lambda m: m["files"][0].update(parts=["../outside.md"]),
        lambda m: m["files"].append(dict(m["files"][0])),
    ],
)
def test_malformed_manifest_is_a_validation_error_before_any_write(mutation, tmp_path):
    folder = tmp_path / "book"
    manifest = make_bundle(folder)
    mutation(manifest)
    write_manifest(folder, manifest)
    assert_rejected_before_writing(folder, tmp_path / "student")


@pytest.mark.parametrize(
    "changes",
    [
        {"path": "other.py"},
        {"part": 0},
        {"part": 2},
        {"part": True},
        {"parts": 2},
        {"parts": True},
        {"encoding": "unknown"},
        {"sha256": "0" * 64},
    ],
)
def test_wrong_part_identity_or_hash_rejects_before_writing(changes, tmp_path):
    folder = tmp_path / "book"
    manifest = make_bundle(folder)
    replace_metadata(folder, manifest, lambda meta: meta.update(changes))
    assert_rejected_before_writing(folder, tmp_path / "student")


@pytest.mark.parametrize(
    "name",
    [
        "../escape.py",
        "/absolute.py",
        "a//alias.py",
        "./alias.py",
        ".",
        ".git/config",
        "nested/.git/config",
        "C:drive.py",
        "folder\\file.py",
        "bad\x00name.py",
        reader.LEDGER,
    ],
)
def test_unsafe_or_reserved_source_paths_are_rejected(name, tmp_path):
    folder = tmp_path / "book"
    manifest = make_bundle(folder)
    manifest["files"][0]["path"] = name
    write_manifest(folder, manifest)
    assert_rejected_before_writing(folder, tmp_path / "student")


def test_source_and_annotation_paths_must_agree(tmp_path):
    folder = tmp_path / "book"
    manifest = make_bundle(folder)
    page = folder / manifest["files"][0]["parts"][0]
    page.write_text(page.read_text().replace("# example.py\n", "# other.py\n"))
    assert_rejected_before_writing(folder, tmp_path / "student")


@pytest.mark.parametrize(
    "damage", ["missing", "duplicate", "truncated", "extra", "unlisted-marker"]
)
def test_missing_duplicate_and_unlisted_source_documents_fail_atomically(damage, tmp_path):
    folder = tmp_path / "book"
    manifest = make_bundle(folder)
    page = folder / manifest["files"][0]["parts"][0]
    text = page.read_text(encoding="utf-8")
    if damage == "missing":
        page.unlink()
    elif damage == "duplicate":
        page.write_text(text + text)
    elif damage == "truncated":
        page.write_text(text.rsplit("````", 1)[0])
    elif damage == "extra":
        (page.parent / "unlisted.md").write_text(text)
    else:
        (folder / "unlisted.md").write_text(text)
    assert_rejected_before_writing(folder, tmp_path / "student")


def test_corrupt_later_stage_prevents_even_early_stage_write(tmp_path):
    folder = tmp_path / "book"
    manifest = make_bundle(
        folder,
        [
            ("early.py", [b"early\n"], "00-environment", "python", "utf-8"),
            ("late.py", [b"late\n"], "01-contracts", "python", "utf-8"),
        ],
    )
    (folder / manifest["files"][1]["parts"][0]).unlink()
    with pytest.raises(ValueError):
        reader.restore(folder, tmp_path / "student", through="00")
    assert not (tmp_path / "student").exists()


def test_binary_corruption_fails_before_writing(tmp_path):
    folder = tmp_path / "book"
    manifest = make_bundle(
        folder, [("image.png", [b"\x89PNG\x00\xff"], "00-environment", "base64", "base64")]
    )
    page = folder / manifest["files"][0]["parts"][0]
    page.write_text(
        page.read_text().replace(base64.b64encode(b"\x89PNG\x00\xff").decode(), "!bad!")
    )
    assert_rejected_before_writing(folder, tmp_path / "student")


def test_progress_ledger_cannot_also_be_a_source_directory(tmp_path):
    folder = tmp_path / "book"
    make_bundle(
        folder,
        [(reader.LEDGER + "/child.py", [b"x = 1\n"], "00-environment", "python", "utf-8")],
    )
    assert_rejected_before_writing(folder, tmp_path / "student")


def test_source_file_ancestor_conflict_is_rejected_before_any_write(tmp_path):
    folder = tmp_path / "book"
    make_bundle(
        folder,
        [
            ("conflict", [b"first\n"], "00-environment", "text", "utf-8"),
            ("conflict/child.py", [b"second\n"], "00-environment", "python", "utf-8"),
        ],
    )
    assert_rejected_before_writing(folder, tmp_path / "student")


def link_or_skip(path, target, *, directory=False):
    try:
        path.symlink_to(target, target_is_directory=directory)
    except (OSError, NotImplementedError) as error:
        pytest.skip(f"Symlink creation unavailable on this runner: {error}")


@pytest.mark.parametrize(
    "kind", ["destination", "ancestor", "manifest", "source", "bundle-ancestor"]
)
def test_symlink_roots_ancestors_and_source_entries_are_rejected(kind, tmp_path):
    folder = tmp_path / "book"
    manifest = make_bundle(folder)
    outside = tmp_path / "outside"
    outside.mkdir()
    destination = tmp_path / "student"
    if kind == "destination":
        link_or_skip(destination, outside, directory=True)
    elif kind == "ancestor":
        link_or_skip(tmp_path / "alias", outside, directory=True)
        destination = tmp_path / "alias/student"
    elif kind == "bundle-ancestor":
        link_or_skip(tmp_path / "alias", tmp_path, directory=True)
        folder = tmp_path / "alias/book"
    else:
        relative = "manifest.json" if kind == "manifest" else manifest["files"][0]["parts"][0]
        page = folder / relative
        external = outside / "original"
        page.rename(external)
        link_or_skip(page, external)
    with pytest.raises(ValueError):
        reader.restore(folder, destination)
    assert not (outside / "example.py").exists()
    if kind != "destination":
        assert not destination.exists()


def test_nonempty_destination_is_untouched_without_explicit_advance(tmp_path):
    folder = tmp_path / "book"
    make_bundle(folder)
    destination = tmp_path / "student"
    destination.mkdir()
    (destination / "mine.txt").write_bytes(b"keep me")
    with pytest.raises(ValueError):
        reader.restore(folder, destination)
    assert {p.name: p.read_bytes() for p in destination.iterdir()} == {"mine.txt": b"keep me"}


def two_stage_bundle(folder):
    return make_bundle(
        folder,
        [
            ("early.py", [b"early\n"], "00-environment", "python", "utf-8"),
            ("late.py", [b"late\n"], "01-contracts", "python", "utf-8"),
        ],
    )


def test_advancement_is_cumulative_and_preserves_unrelated_student_notes(tmp_path):
    folder, destination = tmp_path / "book", tmp_path / "student"
    two_stage_bundle(folder)
    assert reader.restore(folder, destination, through="00") == 1
    assert not (destination / "late.py").exists()
    (destination / "my-notes.txt").write_bytes(b"personal notes")
    assert reader.restore(folder, destination, through="01-contracts", advance=True) == 2
    assert (destination / "early.py").read_bytes() == b"early\n"
    assert (destination / "late.py").read_bytes() == b"late\n"
    assert (destination / "my-notes.txt").read_bytes() == b"personal notes"
    with pytest.raises(ValueError):
        reader.restore(folder, destination, through="00", advance=True)


def test_advancement_never_overwrites_an_edited_prior_stage(tmp_path):
    folder, destination = tmp_path / "book", tmp_path / "student"
    two_stage_bundle(folder)
    reader.restore(folder, destination, through="00")
    (destination / "early.py").write_bytes(b"my change\n")
    with pytest.raises(ValueError):
        reader.restore(folder, destination, through="01", advance=True)
    assert (destination / "early.py").read_bytes() == b"my change\n"
    assert not (destination / "late.py").exists()


@pytest.mark.parametrize("document", [[], None, 1, {"format": 1, "files": []}])
def test_invalid_progress_ledger_never_advances_or_overwrites(document, tmp_path):
    folder, destination = tmp_path / "book", tmp_path / "student"
    two_stage_bundle(folder)
    reader.restore(folder, destination, through="00")
    (destination / reader.LEDGER).write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(ValueError):
        reader.restore(folder, destination, through="01", advance=True)
    assert (destination / "early.py").read_bytes() == b"early\n"
    assert not (destination / "late.py").exists()


def test_future_target_symlink_cannot_be_followed_during_advancement(tmp_path):
    folder, destination = tmp_path / "book", tmp_path / "student"
    two_stage_bundle(folder)
    reader.restore(folder, destination, through="00")
    outside = tmp_path / "outside.py"
    outside.write_bytes(b"untouched")
    link_or_skip(destination / "late.py", outside)
    with pytest.raises(ValueError):
        reader.restore(folder, destination, through="01", advance=True)
    assert outside.read_bytes() == b"untouched"


def test_unknown_stage_is_rejected_before_any_write(tmp_path):
    folder = tmp_path / "book"
    make_bundle(folder)
    with pytest.raises(ValueError):
        reader.restore(folder, tmp_path / "student", through="99")
    assert not (tmp_path / "student").exists()


def test_published_learning_docs_match_deterministic_render():
    from scripts import build_learning_docs as builder

    expected = builder.render()
    actual = {
        path.relative_to(builder.OUTPUT).as_posix(): path.read_bytes()
        for path in builder.OUTPUT.rglob("*")
        if path.is_file()
    }
    assert_exact_inventory(
        actual,
        {
            name: content.encode("utf-8") if isinstance(content, str) else content
            for name, content in expected.items()
        },
    )
    for name, content in expected.items():
        if name.endswith(".md"):
            reader.check_fences(content if isinstance(content, str) else content.decode("utf-8"))


def prose_outside_fences(text):
    """Independent CommonMark-style scanner so nested source links are never followed."""
    result, opened = [], None
    for line in text.splitlines():
        if opened is not None:
            character, width = opened
            if re.fullmatch(r" {0,3}" + re.escape(character) + "{" + str(width) + r",}\s*", line):
                opened = None
            continue
        match = re.fullmatch(r" {0,3}(`{3,}|~{3,})(.*)", line)
        if match and not (match[1][0] == "`" and "`" in match[2]):
            opened = match[1][0], len(match[1])
        else:
            result.append(line)
    assert opened is None, "Unclosed fence in generated documentation"
    return "\n".join(result)


def prose_outside_inline_code(text):
    result, position = [], 0
    runs = re.compile(r"(?<!`)(`+)(?!`)")
    while opening := runs.search(text, position):
        closing = re.compile(r"(?<!`)" + re.escape(opening[0]) + r"(?!`)").search(
            text, opening.end()
        )
        if closing is None:
            result.append(text[position : opening.end()])
            position = opening.end()
            continue
        result.append(text[position : opening.start()])
        position = closing.end()
    result.append(text[position:])
    return "".join(result)


def test_all_local_links_outside_source_fences_resolve_inside_the_bundle():
    from scripts import build_learning_docs as builder

    root = builder.OUTPUT.resolve()
    failures = []
    for page in sorted(builder.OUTPUT.rglob("*.md")):
        prose = prose_outside_inline_code(prose_outside_fences(page.read_text(encoding="utf-8")))
        for target in re.findall(r"\[[^\]\n]*\]\(([^)\n]+)\)", prose):
            url = urlsplit(target.strip().removeprefix("<").removesuffix(">"))
            if url.scheme or url.netloc or not url.path:
                continue
            path = (page.parent / unquote(url.path)).resolve()
            if not path.is_relative_to(root) or not path.is_file():
                failures.append(f"{page.relative_to(root)} -> {target}")
    assert not failures, "Broken local documentation links:\n" + "\n".join(failures)


def test_manifest_covers_owned_tracked_sources_independently_of_generator_groups():
    from scripts import build_learning_docs as builder

    # Restored projects intentionally have no .git; use this independent VCS comparison
    # in a checkout and keep exact builder-source coverage active in both environments.
    rows = reader.read_bundle(builder.OUTPUT)
    expected = {
        name: content.encode("utf-8") if isinstance(content, str) else content
        for _, files in builder.sources()
        for name, content in files
    }
    assert_exact_inventory(rows, expected)
    if not (ROOT / ".git").exists():
        return
    tracked = set(
        subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
        .decode()
        .strip("\0")
        .split("\0")
    )
    excluded = {
        "从零实现AI研发平台_逐步实操手册_完整版.md",
        "templates/vendor/fastapiadmin.zip",
        "templates/vendor/yudao-backend.zip",
        "templates/vendor/yudao-frontend.zip",
    }
    owned = {name for name in tracked if not name.startswith("learning-docs/")} - excluded
    assert not owned - rows.keys(), f"Owned tracked source omitted: {sorted(owned - rows.keys())}"
    assert not rows.keys() & excluded
    assert not any(name.startswith("learning-docs/") for name in rows)
    assert "tests/test_learning_docs.py" in rows
    assert "scripts/rebuild_learning_docs.py" in rows
    assert "scripts/build_learning_docs.py" in rows
    assert "uv.lock" in rows and "tools/node/package-lock.json" in rows
    assert any(name.endswith(".png") for name in rows)


def test_docs_only_bootstrap_runs_isolated_with_original_tree_reads_forbidden(tmp_path):
    from scripts import build_learning_docs as builder

    docs, destination = tmp_path / "only-book", tmp_path / "student"
    shutil.copytree(builder.OUTPUT, docs)
    assert_exact_bytes(
        (docs / "rebuild.py").read_bytes(),
        (ROOT / "scripts/rebuild_learning_docs.py").read_bytes(),
        "rebuild.py",
    )
    launch = tmp_path / "isolated-bootstrap.py"
    launch.write_text(
        "import pathlib, runpy, sys\n"
        "forbidden = pathlib.Path(sys.argv[1]).resolve()\n"
        "def guard(event, args):\n"
        "    if event == 'open' and isinstance(args[0], (str, bytes)):\n"
        "        path = pathlib.Path(args[0].decode() if isinstance(args[0], bytes) else args[0]).resolve()\n"
        "        if path.is_relative_to(forbidden):\n"
        "            raise RuntimeError('Original project access is forbidden: ' + str(path))\n"
        "sys.addaudithook(guard)\n"
        "bootstrap, destination = sys.argv[2:]\n"
        "sys.argv = [bootstrap, destination]\n"
        "runpy.run_path(bootstrap, run_name='__main__')\n"
        "sys.path.insert(0, destination)\n"
        "import workbench\n"
        "assert pathlib.Path(workbench.__file__).resolve().is_relative_to(pathlib.Path(destination))\n",
        encoding="utf-8",
    )
    result = subprocess.run(
        [sys.executable, "-I", str(launch), str(ROOT), str(docs / "rebuild.py"), str(destination)],
        cwd=tmp_path,
        env={key: value for key, value in os.environ.items() if key != "PYTHONPATH"},
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=120,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    for name, data in reader.read_bundle(docs).items():
        assert_exact_bytes((destination / name).read_bytes(), data, name)
    assert not (destination / ".git").exists()
    assert not list((destination / "templates/vendor").glob("*.zip"))


def test_multi_part_navigation_has_no_dangling_separator_or_trailing_space():
    from scripts import build_learning_docs as builder

    source = "".join(
        f"def example_{number}():\n    pass\n" + "# retained source line\n" * 700
        for number in range(3)
    )
    pages, record = builder.source_pages("example.py", source, 0)
    assert len(record["parts"]) == 3
    for index, name in enumerate(record["parts"]):
        navigation = [
            line
            for line in prose_outside_fences(pages[name]).splitlines()
            if line.startswith(("[上一段]", "[下一段]"))
        ]
        assert len(navigation) == 1
        line = navigation[0]
        assert line == line.rstrip(), name
        assert not line.endswith(" ·"), name
        assert line.count("](") == (2 if index == 1 else 1)


def test_repacked_vendor_manifest_blocks_advance_but_clean_full_restore_is_safe(tmp_path):
    original = {
        "sources": [
            {
                "name": "example",
                "sha": "a" * 40,
                "source_digest": "b" * 64,
                "files": 1,
                "archive_sha256": "c" * 64,
            }
        ]
    }
    encoded = (json.dumps(original) + "\n").encode()
    book, old, complete = tmp_path / "book", tmp_path / "original", tmp_path / "complete"
    make_bundle(
        book,
        [
            ("templates/vendor/manifest.json", [encoded], "09-native", "json", "utf-8"),
            ("later.py", [b"answer = 42\n"], "10-business", "python", "utf-8"),
        ],
    )
    reader.restore(book, old, through="09")
    repacked = json.loads(encoded)
    repacked["sources"][0]["archive_sha256"] = "d" * 64
    for key in ("name", "sha", "source_digest", "files"):
        assert repacked["sources"][0][key] == original["sources"][0][key]
    changed = (json.dumps(repacked) + "\n").encode()
    vendor = old / "templates/vendor/manifest.json"
    vendor.write_bytes(changed)
    with pytest.raises(ValueError, match="previously restored file changed"):
        reader.restore(book, old, through="10", advance=True)
    assert vendor.read_bytes() == changed
    assert not (old / "later.py").exists()
    assert reader.restore(book, complete) == 2
    assert (complete / "templates/vendor/manifest.json").read_bytes() == encoded
    assert (complete / "later.py").read_bytes() == b"answer = 42\n"
    assert vendor.read_bytes() == changed  # The user's original directory stays untouched.
``````
