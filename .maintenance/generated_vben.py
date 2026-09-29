"""Reviewed correction of native emitted form syntax; retain raw exports and both hashes."""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
changes = {}


def edit(name, old, new):
    source = changes.get(name, (root / name).read_text(encoding="utf-8"))
    if source.count(old) != 1:
        raise ValueError(f"Reviewed context changed: {name}")
    changes[name] = source.replace(old, new)


name = "workbench/native_vben.py"
source = (root / name).read_text(encoding="utf-8")
if "def adapt_generated_form(" in source:
    raise ValueError("Generated form correction already present")
changes[name] = source + '''

def adapt_generated_form(source: str, class_name: str) -> str:
    """Move the native generator's legacy getter generic onto the modal hook.

    Create opens with no record and edit opens with an ID, so the payload is Partial<DTO>.
    The original codegen ZIP remains unchanged; mounting records before/after hashes.
    """
    if not class_name.isidentifier() or not class_name.startswith("Wb"):
        raise ValueError("Invalid generated Vben class name")
    dto = f"Infra{class_name}Api.{class_name}"
    source = checked_replacement(
        source, "= useVbenModal({", f"= useVbenModal<Partial<{dto}>>({{", 1,
        "generated modal hook",
    )
    return checked_replacement(
        source, f"modalApi.getData<{dto}>()", "modalApi.getData()", 1,
        "generated modal getter",
    )
'''
edit("workbench/native_modules.py", "from workbench.native_environment import checked_database", "from workbench.native_environment import checked_database\nfrom workbench.native_vben import adapt_generated_form")
edit("workbench/native_modules.py", '''                        "Refusing to overwrite existing Vben feature: " + relative
                    )
            else:''', '''                        "Refusing to overwrite existing Vben feature: " + relative
                    )
                if relative == f"views/infra/{slug}/modules/form.vue":
                    class_name = "Wb" + "".join(p.title() for p in entity.name.split("_"))
                    body = adapt_generated_form(body, class_name)
            else:''')
edit("workbench/native_modules.py", '            writes.append({"source": name, "path": str(target), "sha256": sha(target)})', '''            writes.append({
                "source": name,
                "path": str(target),
                "source_sha256": sha(file),
                "sha256": sha(target),
                "compatibility_applied": sha(file) != sha(target),
            })''')
edit("tests/test_native_vben.py", "from workbench.native_vben import checked_replacement, initialize_vben_boundary", "from workbench.native_vben import adapt_generated_form, checked_replacement, initialize_vben_boundary")
name = "tests/test_native_vben.py"
changes[name] += '''

@pytest.mark.parametrize("class_name", ["WbDevice", "WbCategory", "WbAssetItem"])
def test_generated_modal_keeps_precise_dto_and_optional_create_payload(class_name):
    dto = f"Infra{class_name}Api.{class_name}"
    source = (
        "const [Modal, modalApi] = useVbenModal({\\n"
        f"const data = modalApi.getData<{dto}>();\\n"
        "if (!data || !data.id) return;\\n});"
    )
    result = adapt_generated_form(source, class_name)
    assert f"useVbenModal<Partial<{dto}>>(" in result
    assert "modalApi.getData()" in result
    assert "if (!data || !data.id) return;" in result
    assert "getData<" in source
    assert "@ts-ignore" not in result and "any" not in result


def test_generated_modal_contract_drift_is_not_silently_accepted():
    with pytest.raises(ValueError, match="compatibility contract changed"):
        adapt_generated_form("const [Modal, modalApi] = useVbenModal({});", "WbDevice")
'''
edit("docs/native-baseline.md", "任何输入片段不匹配都会报错，不盲目替换新版本源码。", "任何输入片段不匹配都会报错，不盲目替换新版本源码。生成器导出的新增表单也做精确兼容：将旧式 `modalApi.getData<DTO>()` 的泛型迁到 `useVbenModal<Partial<DTO>>`，保留新增时的空载荷和编辑时的 ID 检查。原始生成 ZIP 不改写，`generation.json` 同时记录原始文件与实际挂载文件的哈希。")
for name, content in changes.items():
    (root / name).write_text(content, encoding="utf-8", newline="\n")
print("Applied exact generated Vben form compatibility, receipts, tests and handbook text")
