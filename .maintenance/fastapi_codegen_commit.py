"""Reuse the reviewed transaction fix for the native generator, not sleeps or retries."""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
changes = {}


def edit(name, old, new):
    source = changes.get(name, (root / name).read_text(encoding="utf-8"))
    if source.count(old) != 1:
        raise ValueError("Reviewed context changed: " + name)
    changes[name] = source.replace(old, new)


name = "workbench/native_compatibility.py"
source = (root / name).read_text(encoding="utf-8")
if "def prepare_fastapi_transactions" in source:
    raise ValueError("Transaction setup already present")
changes[name] = source + '''

def prepare_fastapi_transactions(backend: Path) -> list[dict]:
    """Commit native role grants AND codegen metadata before acknowledging success.

    The generator imports, updates and mounts metadata across consecutive HTTP requests.
    Its request-scoped yield otherwise allows an immediate list/export/login to race a commit.
    No retry hides an import failure; preserve native auth, CRUD and transaction handling.
    """
    receipts = []
    for relative in (
        "app/modules/system/role/controller.py",
        "app/modules/generator/gencode/controller.py",
    ):
        receipt = commit_before_response(Path(backend) / relative)
        receipt["path"] = relative
        receipts.append(receipt)
    return receipts
'''
edit("workbench/native_lab.py", "from workbench.native_compatibility import commit_before_response", "from workbench.native_compatibility import prepare_fastapi_transactions")
edit("workbench/native_lab.py", '''            # The native grant endpoint also uses a yielded transaction. Commit it
            # before returning success, not after a new login snapshots permissions.
            role_controller = backend / "app/modules/system/role/controller.py"
            receipt = commit_before_response(role_controller)
            receipt["path"] = role_controller.relative_to(backend).as_posix()
            write_json(reports / "native-compatibility.json", [receipt])''', '''            write_json(
                reports / "native-compatibility.json", prepare_fastapi_transactions(backend)
            )''')
edit("tests/test_native_transaction.py", "from workbench.native_compatibility import commit_before_response", "from workbench.native_compatibility import commit_before_response, prepare_fastapi_transactions")
changes["tests/test_native_transaction.py"] += '''

def test_native_role_and_codegen_both_commit_before_their_success_response(tmp_path):
    paths = [
        "app/modules/system/role/controller.py",
        "app/modules/generator/gencode/controller.py",
    ]
    source = (
        "from fastapi import Depends, Security\\n"
        "async def operation(auth=Security(native_auth), db=Depends(db_getter)):\\n"
        "    return await native_service(db)\\n"
    )
    for relative in paths:
        path = tmp_path / relative
        path.parent.mkdir(parents=True)
        path.write_text(source, encoding="utf-8")
    receipts = prepare_fastapi_transactions(tmp_path)
    assert [r["path"] for r in receipts] == paths
    assert all(r["before_sha256"] != r["after_sha256"] for r in receipts)
    for relative in paths:
        actual = (tmp_path / relative).read_text(encoding="utf-8")
        assert actual == source.replace("Depends(db_getter)", 'Depends(db_getter, scope="function")')
        ast.parse(actual)
'''
edit("docs/native-baseline.md", "### 19.11 兼容规则与排错\n", '''### 19.11 兼容规则与排错

FastapiAdmin 的工作副本在启动前，对原生角色控制器与代码生成控制器的 `db_getter` 依赖设置 `scope="function"`，保留原有认证、权限、CRUD 和事务实现。这样导入表结构、更新生成配置、挂载菜单及授予角色权限都会先提交事务再返回成功，避免下一次列表/导出/登录请求早于提交产生偶发缺失。生成业务控制器沿用同样的提交边界，修改记录写入 `native-compatibility.json` 和生成回执；不是靠固定等待或盲目重试掩盖失败。
''')
for name, content in changes.items():
    (root / name).write_text(content, encoding="utf-8", newline="\n")
print("Applied native generator transaction fix, recorded receipts, regression and handbook")
