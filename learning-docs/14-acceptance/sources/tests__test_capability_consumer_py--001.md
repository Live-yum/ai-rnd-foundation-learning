# tests/test_capability_consumer.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts.capability_fixture`、`workbench.capability_consumer`、`workbench.capability_stack`、`workbench.capability_verification`、`workbench.catalog`、`workbench.domain`、`workbench.filesystem`、`workbench.generator`、`workbench.settings`、`workbench.tools`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `fixture_plan`（L39–L49）：接收`port`。 调用`make_plan`、`Selection(template="python-basic").model_dump`、`Selection`、`str`。 返回路径：L49的`value`。
- `product_fixture`（L52–L69）：接收`tmp_path`、`custom`、`port`。 控制顺序：L56按`custom`分支。 调用`generate_basic`、`fixture_baseline`、`fixture_plan`、`prepare_consumer`、`(product / "app.py").write_text`、`APP.replace( " # CUSTOM_ACCESS", " from access import readable\n …`、`APP.replace`、`(product / "access.py").write_text`。 返回路径：L69的`product, plan`。
- `extract_consumer`（L72–L81）：接收`product`、`tmp_path`。 控制顺序：L75遍历`files(product)`；L79断言`manifest(clean) == manifest(product)`；L80断言`not list(clean.rglob("*.db"))`。 调用`zipfile.ZipFile`、`files`、`handle.write`、`unpack`、`manifest`、`list`、`clean.rglob`。 返回路径：L81的`clean`。
- `free_port`（L84–L90）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L85在`True`成立时循环；L89按`port not in {2280, 55432, 55433}`分支。 调用`socket.socket`、`sock.bind`、`sock.getsockname`。 返回路径：L90的`port`。
- `running_consumer`（L94–L124）：接收`product`、`tmp_path`、`port`、`env`、`extra_args`。 源码说明：Only called on the audited, authored fixture above or golden template.。 控制顺序：L112在`time.monotonic() < deadline`成立时循环；L113断言`process.poll() is None`；L115按`client.get("/health").status_code == 200`分支。 调用`log_path.open`、`subprocess.Popen`、`str`、`clean_env`、`process_options`、`httpx.Client`、`time.monotonic`、`process.poll`、`log_path.read_text`等。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `invoke_start`（L127–L137）：接收`product`、`tmp_path`、`env`、`*args`。 调用`subprocess.run`、`str`、`clean_env`。 返回路径：L128的`subprocess.run( [sys.executable, str(product / "start.py"), "--no-install", *args], cwd=tm…`。
- `test_authored_downloaded_zip_custom_cold_bootstrap_and_data_preserving_restart`（L140–L181）：接收`tmp_path`。 控制顺序：L145断言`contract["initialization"] == "application-startup"`；L146断言`contract["existing_schema_migration"] == "unverified"`；L152断言`client.post("/users", json=account).status_code == 201`；L156断言`saved.status_code == 201`；L158断言`client.get(f"/entries/{identifier}").status_code == 401`；L160断言`database.is_file()`；L161断言`not unrelated.exists()`；L162断言`not (clean / ".data/product.db").exists()`。后续分支沿下方源码相同行号继续阅读。 调用`free_port`、`product_fixture`、`extract_consumer`、`inspect_consumer`、`unrelated.as_posix`、`manifest`、`running_consumer`、`client.post`、`client.post("/login", json=account).json`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_custom_product_uses_explicit_canonical_url_and_overwrites_ambient_alias`（L184–L196）：接收`tmp_path`。 控制顺序：L194断言`client.get("/health").json() == {"ok": True}`；L195断言`database.exists()`；L196断言`not (clean / plan.runtime.database_path).exists()`。 调用`free_port`、`product_fixture`、`extract_consumer`、`database.as_posix`、`running_consumer`、`client.get("/health").json`、`client.get`、`database.exists`、`(clean / plan.runtime.database_path).exists`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_standard_template_zip_applies_versioned_migration_preserving_existing_data`（L199–L235）：接收`tmp_path`。 控制顺序：L203断言`initialized.returncode == 0`；L208断言`connection.execute("SELECT version_num FROM alembic_version").fetchone() == ("0001",)`；L217遍历`range(2)`；L219断言`migrated.returncode == 0`；L221断言`connection.execute("SELECT version_num FROM alembic_version").fetchone() == ("0002",)`；L222断言`connection.execute("SELECT id,owner_id,title,note FROM entries").fetchone() == ( "e",…`；L228断言`connection.execute("SELECT password FROM users WHERE id='u'").fetchone() == ( "preser…`；L235断言`connection.execute("SELECT title FROM entries").fetchone() == ("existing record",)`。 调用`product_fixture`、`extract_consumer`、`invoke_start`、`sqlite3.connect`、`connection.execute`、`connection.execute("SELECT version_num FROM alembic_version").fet…`、`(clean / "migrations/versions/0002_consumer_fixture.py").write_te…`、`range`、`connection.execute("SELECT id,owner_id,title,note FROM entries").…`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_inspection_reads_data_only_and_shared_runtime_is_exact`（L238–L250）：接收`tmp_path`。 控制顺序：L242断言`observed == expected_consumer(plan)`；L243断言`prepare_consumer(product, plan) == observed`；L245断言`command.cwd == "."`；L246断言`command.argv[1:] == ["start.py", "--no-install", "--host", "0.0.0.0", "--port", "8123…`；L247断言`command.argv[0] == "/opt/rnd/runtime/python-basic/.venv/bin/python"`；L249断言`environment["PRODUCT_DATABASE_URL"] == environment["DATABASE_URL"]`；L250断言`environment["DATABASE_URL"].endswith("/product/" + plan.runtime.database_path)`。 调用`product_fixture`、`(product / "app.py").write_text`、`inspect_consumer`、`expected_consumer`、`prepare_consumer`、`consumer_start_command`、`database_environment`、`environment["DATABASE_URL"].endswith`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_consumer_contract_must_be_source_and_plan_bound`（L266–L289）：接收`tmp_path`、`case`。 控制顺序：L270按`case == "missing"`分支；L272断言`inspect_consumer(product, plan) is None`；L273按`case == "stale-plan"`分支；L275按`case == "extra-field"`分支；L277按`case == "boolean-schema"`分支；L279按`case == "launcher"`分支；L281按`case == "selection"`分支；L283按`case == "oversized"`分支。后续分支沿下方源码相同行号继续阅读。 调用`product_fixture`、`json.loads`、`path.read_text`、`path.unlink`、`inspect_consumer`、`write_json`、`(product / "start.py").write_text`、`Selection(template="fastapiadmin").model_dump`、`Selection`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_invalid_consumer_database_paths_fail_before_execution`（L305–L309）：接收`tmp_path`、`database_path`。 调用`product_fixture`、`pytest.raises`、`prepare_consumer`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_custom_launcher_rejects_unsupported_database_and_init_only`（L322–L330）：接收`tmp_path`、`url`。 控制顺序：L325断言`rejected.returncode != 0`；L326断言`"local persistent SQLite file" in rejected.stderr`；L328断言`no_migration.returncode != 0`；L329断言`"separately verified migration" in no_migration.stderr`；L330断言`not list(product.rglob("*.db"))`。 调用`product_fixture`、`invoke_start`、`list`、`product.rglob`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_profile_cannot_reuse_python_consumer_proof`（L333–L337）：接收`tmp_path`。 调用`product_fixture`、`Selection`、`pytest.raises`、`prepare_consumer`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_downloaded_launcher_rejects_noncanonical_metadata_before_app_execution`（L352–L358）：接收`tmp_path`、`change`。 控制顺序：L356断言`rejected.returncode != 0`；L357断言`"Invalid consumer" in rejected.stderr`；L358断言`not list(product.rglob("*.db"))`。 调用`product_fixture`、`write_json`、`expected_consumer`、`invoke_start`、`list`、`product.rglob`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `observed_consumer_fixture`（L361–L378）：接收`product`、`plan`。 源码说明：Synthetic receipt for gate unit tests only, not actual sandbox proof.。 调用`inspect_consumer`、`digest`、`manifest`、`plan.model_dump`。 返回路径：L364的`{ "passed": True, "scope": "aggregate", "restarted": True, "source_digest": digest(manifes…`。
- `test_consumer_gate_requires_observations_but_never_claims_migration`（L381–L386）：接收`tmp_path`。 控制顺序：L385断言`observed is proof["consumer"]`；L386断言`observed["existing_schema_migration"] == "unverified"`。 调用`product_fixture`、`observed_consumer_fixture`、`require_consumer_evidence`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_consumer_gate_rejects_unobserved_stale_and_overstated_receipts`（L410–L446）：接收`tmp_path`、`case`。 控制顺序：L413按`case == "missing"`分支；L415按`case == "cold"`分支；L417按`case == "restart"`分支；L419按`case == "integer-true"`分支；L421按`case == "migration-claim"`分支；L423按`case == "old-source"`分支；L425按`case == "old-plan"`分支；L427按`case == "failed-proof"`分支。后续分支沿下方源码相同行号继续阅读。 调用`product_fixture`、`observed_consumer_fixture`、`proof.pop`、`(product / "app.py").write_text`、`(product / CONSUMER_FILE).unlink`、`pytest.raises`、`require_consumer_evidence`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_standard_postgres_auto_compose_keeps_server_and_database_ports_separate`（L449–L488）：接收`tmp_path`、`monkeypatch`。 控制顺序：L486断言`calls[-1][0][-4:] == ["manage.py", "start", "--port", "8421"]`；L487断言`":5549/product" in calls[-1][1]["env"]["PRODUCT_DATABASE_URL"]`；L488断言`json.loads((tmp_path / ".data/deployment.json").read_text())["port"] == 5549`。 调用`runpy.run_path`、`str`、`write_json`、`Selection(template="python-basic", database="postgresql").model_d…`、`Selection`、`monkeypatch.setattr`、`calls.append`、`launch`、`json.loads`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_standard_postgres_auto_compose_keeps_server_and_database_ports_separate.AuthoredSocket`（L471–L482）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_standard_postgres_auto_compose_keeps_server_and_database_ports_separate.AuthoredSocket.__enter__`（L472–L473）：不接收显式业务参数，从已配置对象/模块读取依赖。 返回路径：L473的`self`。
- `test_standard_postgres_auto_compose_keeps_server_and_database_ports_separate.AuthoredSocket.__exit__`（L475–L476）：接收`*_`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_standard_postgres_auto_compose_keeps_server_and_database_ports_separate.AuthoredSocket.bind`（L478–L479）：接收`address`。 控制顺序：L479断言`address == ("127.0.0.1", 0)`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_standard_postgres_auto_compose_keeps_server_and_database_ports_separate.AuthoredSocket.getsockname`（L481–L482）：不接收显式业务参数，从已配置对象/模块读取依赖。 返回路径：L482的`("127.0.0.1", 5549)`。
- `test_live_authored_fixture_requires_consumer_and_pre_replay_obligations`（L491–L503）：接收`tmp_path`。 控制顺序：L498断言`inspect_consumer(product, plan, required=True)`；L499断言`len(plan.obligations) == 1`；L500断言`plan.complete_source_ids == []`；L501断言`coverage_errors(plan, scope_sources([GOAL])) == []`。 调用`fixed_application`、`inspect_consumer`、`len`、`coverage_errors`、`scope_sources`、`pytest.raises`、`require_atomic_consumer_evidence`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_capability_consumer.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L503。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`19413`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_capability_consumer.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "53ee62592a5e6f91dcd12c3ccdee8703995d276ebdc561941a58b76fd99654e7"} -->
````python
# tests/test_capability_consumer.py
"""Authored ZIPs exercise the consumer command, never arbitrary generated source.

Python custom bootstrap/restart and baseline Alembic migration are deliberately
separate tests. Neither is native/FastapiAdmin or paid-provider evidence.
"""

import json
import runpy
import socket
import sqlite3
import subprocess
import sys
import time
import zipfile
from contextlib import contextmanager

import httpx
import pytest

from scripts.capability_fixture import APP, SHARED_ROUTES, fixture_baseline, make_plan
from workbench.capability_consumer import (
    CONSUMER_FILE,
    consumer_start_command,
    expected_consumer,
    inspect_consumer,
    prepare_consumer,
    require_consumer_evidence,
)
from workbench.capability_stack import database_environment
from workbench.capability_verification import CheckFailure
from workbench.catalog import Selection
from workbench.domain import digest
from workbench.filesystem import files, manifest, unpack, write_json
from workbench.generator import generate_basic
from workbench.settings import ROOT
from workbench.tools import clean_env, process_options, stop_process


def fixture_plan(port=8123):
    value = make_plan(
        {
            "selection": Selection(template="python-basic").model_dump(),
            "source_digest": "a" * 64,
            "source_units": [{"id": "source-0-0"}],
        }
    )
    value.runtime.port = port
    value.runtime.start.argv[-1] = str(port)
    return value


def product_fixture(tmp_path, *, custom=True, port=8123):
    product = tmp_path / "authored"
    generate_basic(fixture_baseline(), product)
    plan = fixture_plan(port)
    if custom:
        prepare_consumer(product, plan)
        (product / "app.py").write_text(
            APP.replace(
                "    # CUSTOM_ACCESS",
                "    from access import readable\n    allowed = readable(row['owner'],name,member)",
            ).replace("# CUSTOM_ROUTES", SHARED_ROUTES),
            encoding="utf-8",
        )
        (product / "access.py").write_text(
            "def readable(owner, actor, member):\n    return owner == actor or member\n",
            encoding="utf-8",
        )
    return product, plan


def extract_consumer(product, tmp_path):
    archive = tmp_path / "downloaded.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as handle:
        for name, path in files(product):
            handle.write(path, name)
    clean = tmp_path / "unzipped"
    unpack(archive, clean, template="python-basic")
    assert manifest(clean) == manifest(product)
    assert not list(clean.rglob("*.db"))
    return clean


def free_port():
    while True:
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        if port not in {2280, 55432, 55433}:
            return port


@contextmanager
def running_consumer(product, tmp_path, port, *, env=None, extra_args=()):
    """Only called on the audited, authored fixture above or golden template."""
    log_path = tmp_path / "consumer.log"
    with log_path.open("w", encoding="utf-8") as log:
        process = subprocess.Popen(
            [sys.executable, str(product / "start.py"), "--no-install", *extra_args],
            # Prove that a caller's cwd does not change DB paths or imports.
            cwd=tmp_path,
            env=clean_env(env or {}),
            stdout=log,
            stderr=subprocess.STDOUT,
            **process_options(),
        )
        try:
            with httpx.Client(
                base_url=f"http://127.0.0.1:{port}", timeout=1, trust_env=False
            ) as client:
                deadline = time.monotonic() + 20
                while time.monotonic() < deadline:
                    assert process.poll() is None, log_path.read_text(encoding="utf-8")
                    try:
                        if client.get("/health").status_code == 200:
                            break
                    except httpx.HTTPError:
                        pass
                    time.sleep(0.05)
                else:
                    pytest.fail("Authored consumer failed startup: " + log_path.read_text())
                yield client
        finally:
            stop_process(process)


def invoke_start(product, tmp_path, *args, env=None):
    return subprocess.run(
        [sys.executable, str(product / "start.py"), "--no-install", *args],
        cwd=tmp_path,
        env=clean_env(env or {}),
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
        check=False,
    )


def test_authored_downloaded_zip_custom_cold_bootstrap_and_data_preserving_restart(tmp_path):
    port = free_port()
    product, plan = product_fixture(tmp_path, port=port)
    clean = extract_consumer(product, tmp_path)
    contract = inspect_consumer(clean, plan, required=True)
    assert contract["initialization"] == "application-startup"
    assert contract["existing_schema_migration"] == "unverified"
    unrelated = tmp_path / "must-not-use-platform.db"
    env = {"DATABASE_URL": "sqlite:///" + unrelated.as_posix()}
    before = manifest(clean)
    with running_consumer(clean, tmp_path, port, env=env) as client:
        account = {"name": "owner", "password": "authored-fixture-password"}
        assert client.post("/users", json=account).status_code == 201
        token = client.post("/login", json=account).json()["token"]
        headers = {"Authorization": "Bearer " + token}
        saved = client.post("/entries", json={"title": "kept across restart"}, headers=headers)
        assert saved.status_code == 201
        identifier = saved.json()["id"]
        assert client.get(f"/entries/{identifier}").status_code == 401
    database = clean / plan.runtime.database_path
    assert database.is_file()
    assert not unrelated.exists()
    assert not (clean / ".data/product.db").exists()
    with sqlite3.connect(database) as connection:
        assert [row[1] for row in connection.execute("PRAGMA table_info(users)")] == [
            "name",
            "salt",
            "hash",
        ]
        assert (
            connection.execute(
                "SELECT name FROM sqlite_master WHERE name='alembic_version'"
            ).fetchone()
            is None
        ), "Custom app must not run incompatible baseline migrations"
    with running_consumer(clean, tmp_path, port, env=env) as client:
        assert client.get(f"/entries/{identifier}", headers=headers).json() == {
            "id": identifier,
            "title": "kept across restart",
        }
        assert client.post("/login", json=account).status_code == 200
    assert manifest(clean) == before


def test_custom_product_uses_explicit_canonical_url_and_overwrites_ambient_alias(tmp_path):
    port = free_port()
    product, plan = product_fixture(tmp_path, port=port)
    clean = extract_consumer(product, tmp_path)
    database = tmp_path / "existing-local" / "custom.db"
    env = {
        "PRODUCT_DATABASE_URL": "sqlite:///" + database.as_posix(),
        "DATABASE_URL": "postgresql://must-never-be-used.invalid/platform",
    }
    with running_consumer(clean, tmp_path, port, env=env) as client:
        assert client.get("/health").json() == {"ok": True}
    assert database.exists()
    assert not (clean / plan.runtime.database_path).exists()


def test_standard_template_zip_applies_versioned_migration_preserving_existing_data(tmp_path):
    product, _ = product_fixture(tmp_path, custom=False)
    clean = extract_consumer(product, tmp_path)
    initialized = invoke_start(clean, tmp_path, "--init-only")
    assert initialized.returncode == 0, initialized.stdout + initialized.stderr
    database = clean / ".data/product.db"
    with sqlite3.connect(database) as connection:
        connection.execute("INSERT INTO users VALUES('u','existing-user','preserved-hash')")
        connection.execute("INSERT INTO entries VALUES('e','u','existing record')")
        assert connection.execute("SELECT version_num FROM alembic_version").fetchone() == ("0001",)
    # Explicit authored old-to-new migration, separate from the custom fixture.
    (clean / "migrations/versions/0002_consumer_fixture.py").write_text(
        'from alembic import op\nimport sqlalchemy as sa\nrevision = "0002"\n'
        'down_revision = "0001"\ndef upgrade():\n'
        '    op.add_column("entries", sa.Column("note", sa.String(100), nullable=True))\n'
        'def downgrade():\n    raise RuntimeError("fixture has no downgrade")\n',
        encoding="utf-8",
    )
    for _ in range(2):
        migrated = invoke_start(clean, tmp_path, "--init-only")
        assert migrated.returncode == 0, migrated.stdout + migrated.stderr
    with sqlite3.connect(database) as connection:
        assert connection.execute("SELECT version_num FROM alembic_version").fetchone() == ("0002",)
        assert connection.execute("SELECT id,owner_id,title,note FROM entries").fetchone() == (
            "e",
            "u",
            "existing record",
            None,
        )
        assert connection.execute("SELECT password FROM users WHERE id='u'").fetchone() == (
            "preserved-hash",
        )
    port = free_port()
    with running_consumer(clean, tmp_path, port, extra_args=("--port", str(port))):
        pass
    with sqlite3.connect(database) as connection:
        assert connection.execute("SELECT title FROM entries").fetchone() == ("existing record",)


def test_inspection_reads_data_only_and_shared_runtime_is_exact(tmp_path):
    product, plan = product_fixture(tmp_path)
    (product / "app.py").write_text("raise AssertionError('never import candidate')\n")
    observed = inspect_consumer(product, plan, required=True)
    assert observed == expected_consumer(plan)
    assert prepare_consumer(product, plan) == observed
    command = consumer_start_command(plan)
    assert command.cwd == "."
    assert command.argv[1:] == ["start.py", "--no-install", "--host", "0.0.0.0", "--port", "8123"]
    assert command.argv[0] == "/opt/rnd/runtime/python-basic/.venv/bin/python"
    environment = database_environment(plan)
    assert environment["PRODUCT_DATABASE_URL"] == environment["DATABASE_URL"]
    assert environment["DATABASE_URL"].endswith("/product/" + plan.runtime.database_path)


@pytest.mark.parametrize(
    "case",
    [
        "missing",
        "stale-plan",
        "extra-field",
        "boolean-schema",
        "launcher",
        "selection",
        "oversized",
        "data-source",
    ],
)
def test_consumer_contract_must_be_source_and_plan_bound(tmp_path, case):
    product, plan = product_fixture(tmp_path)
    path = product / CONSUMER_FILE
    value = json.loads(path.read_text())
    if case == "missing":
        path.unlink()
        assert inspect_consumer(product, plan) is None
    elif case == "stale-plan":
        plan.runtime.database_path = "other/new.db"
    elif case == "extra-field":
        write_json(path, {**value, "command": ["sh", "-c", "false"]})
    elif case == "boolean-schema":
        write_json(path, {**value, "schema": True})
    elif case == "launcher":
        (product / "start.py").write_text("# replaced startup\n")
    elif case == "selection":
        write_json(product / "selection.json", Selection(template="fastapiadmin").model_dump())
    elif case == "oversized":
        path.write_text(" " * 4097)
    elif case == "data-source":
        (product / "data").mkdir()
        (product / "data/imported.py").write_text("# source hidden under database directory\n")
    with pytest.raises(CheckFailure):
        inspect_consumer(product, plan, required=True)


@pytest.mark.parametrize(
    "database_path",
    [
        "app.db",
        "../data/app.db",
        "data/../app.db",
        "data/source.py",
        "data/.hidden/app.db",
        "data//app.db",
        "node_modules/app.db",
        "data/a?b.db",
    ],
)
def test_invalid_consumer_database_paths_fail_before_execution(tmp_path, database_path):
    product, plan = product_fixture(tmp_path)
    plan.runtime.database_path = database_path
    with pytest.raises(CheckFailure):
        prepare_consumer(product, plan)


@pytest.mark.parametrize(
    "url",
    [
        "sqlite:///:memory:",
        "sqlite:///file:other.db",
        "sqlite://///server/share.db",
        "sqlite:///local.db?mode=ro",
        "postgresql://localhost/app",
    ],
)
def test_custom_launcher_rejects_unsupported_database_and_init_only(tmp_path, url):
    product, _ = product_fixture(tmp_path)
    rejected = invoke_start(product, tmp_path, env={"PRODUCT_DATABASE_URL": url})
    assert rejected.returncode != 0
    assert "local persistent SQLite file" in rejected.stderr
    no_migration = invoke_start(product, tmp_path, "--init-only")
    assert no_migration.returncode != 0
    assert "separately verified migration" in no_migration.stderr
    assert not list(product.rglob("*.db"))


def test_native_profile_cannot_reuse_python_consumer_proof(tmp_path):
    product, plan = product_fixture(tmp_path)
    plan.selection = Selection(template="fastapiadmin")
    with pytest.raises(CheckFailure, match="尚无"):
        prepare_consumer(product, plan)


@pytest.mark.parametrize(
    "change",
    [
        {"schema": True},
        {"entrypoint": "app:app --reload"},
        {"command": ["sh", "-c", "false"]},
        {"database_path": "../outside.db"},
        {"database_path": "data/a?b.db"},
        {"existing_schema_migration": "verified"},
        {"database_environment": ["DATABASE_URL"]},
    ],
)
def test_downloaded_launcher_rejects_noncanonical_metadata_before_app_execution(tmp_path, change):
    product, plan = product_fixture(tmp_path)
    write_json(product / CONSUMER_FILE, {**expected_consumer(plan), **change})
    rejected = invoke_start(product, tmp_path)
    assert rejected.returncode != 0
    assert "Invalid consumer" in rejected.stderr
    assert not list(product.rglob("*.db"))


def observed_consumer_fixture(product, plan):
    """Synthetic receipt for gate unit tests only, not actual sandbox proof."""
    contract = inspect_consumer(product, plan, required=True)
    return {
        "passed": True,
        "scope": "aggregate",
        "restarted": True,
        "source_digest": digest(manifest(product)),
        "plan_digest": digest(plan.model_dump()),
        "consumer": {
            "contract": contract,
            "contract_sha256": digest(contract),
            "entrypoint": "start.py",
            "cold_start": True,
            "restart": True,
            "existing_schema_migration": "unverified",
        },
    }


def test_consumer_gate_requires_observations_but_never_claims_migration(tmp_path):
    product, plan = product_fixture(tmp_path)
    proof = observed_consumer_fixture(product, plan)
    observed = require_consumer_evidence(product, plan, proof)
    assert observed is proof["consumer"]
    assert observed["existing_schema_migration"] == "unverified"


@pytest.mark.parametrize(
    "case",
    [
        "missing",
        "cold",
        "restart",
        "integer-true",
        "migration-claim",
        "old-source",
        "old-plan",
        "failed-proof",
        "node-proof",
        "not-restarted",
        "changed-contract",
        "changed-digest",
        "wrong-launcher",
        "unexpected-field",
        "changed-source",
        "no-contract",
    ],
)
def test_consumer_gate_rejects_unobserved_stale_and_overstated_receipts(tmp_path, case):
    product, plan = product_fixture(tmp_path)
    proof = observed_consumer_fixture(product, plan)
    if case == "missing":
        proof.pop("consumer")
    elif case == "cold":
        proof["consumer"]["cold_start"] = False
    elif case == "restart":
        proof["consumer"]["restart"] = False
    elif case == "integer-true":
        proof["consumer"]["cold_start"] = 1
    elif case == "migration-claim":
        proof["consumer"]["existing_schema_migration"] = "verified"
    elif case == "old-source":
        proof["source_digest"] = "b" * 64
    elif case == "old-plan":
        proof["plan_digest"] = "b" * 64
    elif case == "failed-proof":
        proof["passed"] = False
    elif case == "node-proof":
        proof["scope"] = "node"
    elif case == "not-restarted":
        proof["restarted"] = False
    elif case == "changed-contract":
        proof["consumer"]["contract"]["entrypoint"] = "another:app"
    elif case == "changed-digest":
        proof["consumer"]["contract_sha256"] = "b" * 64
    elif case == "wrong-launcher":
        proof["consumer"]["entrypoint"] = "uvicorn"
    elif case == "unexpected-field":
        proof["consumer"]["native_verified"] = True
    elif case == "changed-source":
        (product / "app.py").write_text(APP + "\n# changed after verification\n")
    elif case == "no-contract":
        (product / CONSUMER_FILE).unlink()
    with pytest.raises(CheckFailure):
        require_consumer_evidence(product, plan, proof)


def test_standard_postgres_auto_compose_keeps_server_and_database_ports_separate(
    tmp_path, monkeypatch
):
    # Load only the repository's audited launcher, with Docker/child execution
    # stubbed. This is a launcher regression, not PostgreSQL integration proof.
    launch = runpy.run_path(str(ROOT / "templates/product/start.py"))["main"]
    namespace = launch.__globals__
    namespace["ROOT"] = tmp_path
    write_json(
        tmp_path / "selection.json",
        Selection(template="python-basic", database="postgresql").model_dump(),
    )
    monkeypatch.setattr(namespace["sys"], "argv", ["start.py", "--no-install", "--port", "8421"])
    monkeypatch.setattr(namespace["os"], "environ", {})
    monkeypatch.setattr(namespace["shutil"], "which", lambda command: "/authored/docker")
    monkeypatch.setattr(namespace["secrets"], "token_urlsafe", lambda size: "fixture-password")
    monkeypatch.setattr(namespace["secrets"], "token_hex", lambda size: "fixture-project")
    calls = []
    monkeypatch.setattr(
        namespace["subprocess"], "run", lambda argv, **kwargs: calls.append((argv, kwargs))
    )

    class AuthoredSocket:
        def __enter__(self):
            return self

        def __exit__(self, *_):
            pass

        def bind(self, address):
            assert address == ("127.0.0.1", 0)

        def getsockname(self):
            return ("127.0.0.1", 5549)

    monkeypatch.setattr(namespace["socket"], "socket", AuthoredSocket)
    launch()
    assert calls[-1][0][-4:] == ["manage.py", "start", "--port", "8421"]
    assert ":5549/product" in calls[-1][1]["env"]["PRODUCT_DATABASE_URL"]
    assert json.loads((tmp_path / ".data/deployment.json").read_text())["port"] == 5549


def test_live_authored_fixture_requires_consumer_and_pre_replay_obligations(tmp_path):
    from scripts.capability_fixture import GOAL
    from scripts.ci_capability_profile import fixed_application, require_atomic_consumer_evidence
    from workbench.capability_contracts import coverage_errors, scope_sources

    product = tmp_path / "live-authored-fixture"
    plan = fixed_application(product, atomic_consumer=True)
    assert inspect_consumer(product, plan, required=True)
    assert len(plan.obligations) == 1
    assert plan.complete_source_ids == []
    assert coverage_errors(plan, scope_sources([GOAL])) == []
    with pytest.raises(CheckFailure):
        require_atomic_consumer_evidence(product, plan, {"passed": True})
````
