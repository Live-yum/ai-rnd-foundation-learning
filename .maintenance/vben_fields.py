"""Exact reviewed generated-source corrections, plus real form submission evidence."""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
changes = {}


def edit(name, old, new):
    source = changes.get(name, (root / name).read_text(encoding="utf-8"))
    if source.count(old) != 1:
        raise ValueError("Reviewed context changed: " + name)
    changes[name] = source.replace(old, new)


edit("workbench/native_vben.py", "from pathlib import Path", "import re\nfrom collections.abc import Sequence\nfrom pathlib import Path\n\nfrom workbench.domain import FieldSpec")
changes["workbench/native_vben.py"] += '''

def prune_generated_import(source: str, identifier: str, declaration: str) -> str:
    """Remove only an exact unused single import emitted by the pinned generator."""
    if declaration not in source:
        return source
    if source.count(declaration) != 1:
        raise ValueError("Duplicate generated import: " + identifier)
    remaining = source.replace(declaration, "", 1)
    if re.search(r"\\b" + re.escape(identifier) + r"\\b", remaining):
        return source
    return remaining


def adapt_generated_schema(source: str, fields: Sequence[FieldSpec]) -> str:
    """Preserve declared value kinds in both generated edit and search forms."""
    source = prune_generated_import(
        source, "getDictOptions", "import { getDictOptions } from '@vben/hooks';\\n"
    )
    for field in fields:
        if field.kind == "text":
            continue
        first, *rest = field.name.split("_")
        name = first + "".join(piece[:1].upper() + piece[1:] for piece in rest)
        # Guard the pinned template; never consume the next field on shape drift.
        pattern = re.compile(
            r"    \\{\\n      fieldName: '" + re.escape(name)
            + r"',\\n(?:(?!fieldName:).)*?\\n    \\},", re.DOTALL
        )
        if not 1 <= len(list(pattern.finditer(source))) <= 2:
            raise ValueError("Unsupported generated form field shape: " + name)

        def transform(match):
            block = match.group(0)
            if field.kind == "integer":
                block = checked_replacement(
                    block, "component: 'Input',", "component: 'InputNumber',", 1, name
                )
                return checked_replacement(
                    block, "componentProps: {", "componentProps: {\\n        precision: 0,", 1, name
                )
            if "component: 'Select'," in block:
                block = checked_replacement(
                    block, "component: 'Select',", "component: 'RadioGroup',", 1, name
                )
            elif block.count("component: 'RadioGroup',") != 1:
                raise ValueError("Unsupported generated boolean control: " + name)
            return checked_replacement(
                block, "options: [],",
                "options: [{ label: '是', value: true }, { label: '否', value: false }],",
                1, name,
            )

        source = pattern.sub(transform, source)
    return source
'''
edit("workbench/native_modules.py", "from workbench.native_vben import adapt_generated_form", "from workbench.native_vben import adapt_generated_form, adapt_generated_schema, prune_generated_import")
edit("workbench/native_modules.py", "                    body = adapt_generated_form(body, class_name)", '''                    body = adapt_generated_form(body, class_name)
                elif relative == f"views/infra/{slug}/data.ts":
                    body = adapt_generated_schema(body, entity.fields)
                elif relative == f"api/infra/{slug}/index.ts":
                    body = prune_generated_import(
                        body, "Dayjs", "import type { Dayjs } from 'dayjs';\\n"
                    )''')
edit("tests/test_native_vben.py", "from workbench.filesystem import manifest", "from workbench.domain import FieldSpec\nfrom workbench.filesystem import manifest")
edit("tests/test_native_vben.py", "    adapt_generated_form,", "    adapt_generated_form,\n    adapt_generated_schema,\n    prune_generated_import,")
changes["tests/test_native_vben.py"] += '''

@pytest.mark.parametrize("identifier,line", [
    ("Dayjs", "import type { Dayjs } from 'dayjs';\\n"),
    ("getDictOptions", "import { getDictOptions } from '@vben/hooks';\\n"),
])
def test_pruning_never_removes_an_import_still_used(identifier, line):
    assert prune_generated_import(line + "const unrelated = 1;", identifier, line) == "const unrelated = 1;"
    used = line + f"const value = {identifier};"
    assert prune_generated_import(used, identifier, line) == used
    with pytest.raises(ValueError, match="Duplicate"):
        prune_generated_import(line + line, identifier, line)


def schema_field(name, component, options=False):
    return (
        "    {\\n" + f"      fieldName: '{name}',\\n      label: '{name}',\\n"
        + f"      component: '{component}',\\n      componentProps: {{\\n"
        + ("        options: [],\\n" if options else "        placeholder: 'value',\\n")
        + "      },\\n    },"
    )


def test_generated_schema_preserves_zero_false_and_all_fields():
    source = (
        schema_field("itemCount", "Input") + "\\n"
        + schema_field("enabled", "RadioGroup", True) + "\\n"
        + schema_field("itemCount", "Input") + "\\n"
        + schema_field("enabled", "Select", True)
    )
    result = adapt_generated_schema(source, [
        FieldSpec(name="item_count", kind="integer"),
        FieldSpec(name="enabled", kind="boolean"),
    ])
    assert result.count("fieldName:") == source.count("fieldName:") == 4
    assert result.count("component: 'InputNumber'") == 2
    assert result.count("precision: 0") == 2
    assert result.count("component: 'RadioGroup'") == 2
    assert result.count("value: false") == result.count("value: true") == 2
    assert "value: 'false'" not in result
    assert "options: []" in source and "options: []" not in result


@pytest.mark.parametrize("source", ["", schema_field("enabled", "Switch", True)])
def test_unknown_generated_boolean_shape_fails_closed(source):
    with pytest.raises(ValueError, match="Unsupported generated"):
        adapt_generated_schema(source, [FieldSpec(name="enabled", kind="boolean")])
'''
edit("workbench/native_lab.py", '            write_json(reports / "browser-targets.json", targets)', '''            for target, entity in zip(targets, plan.entities, strict=True):
                target["fields"] = [field.model_dump() for field in entity.fields]
            write_json(reports / "browser-targets.json", targets)''')
edit("scripts/native_browser.cjs", "      report.pages.push({ route: target.route, real_list_request: true, rendered: true });", '''      const pageResult = { route: target.route, real_list_request: true, rendered: true };
      if (!fastapi && target.fields) {
        // Submit through the real generated UI; zero/false must not become strings or disappear.
        await page.getByRole('button', { name: /^新增|^创建/ }).first().click();
        const dialog = page.getByRole('dialog').last();
        await dialog.waitFor({ state: 'visible' });
        const expected = {};
        let booleanIndex = 0;
        for (const field of target.fields) {
          const key = field.name.replace(/_([a-z])/g, (_, c) => c.toUpperCase());
          if (field.kind === 'boolean') {
            await dialog.getByRole('radio', { name: '否', exact: true }).nth(booleanIndex++).check();
            expected[key] = false;
          } else {
            const value = field.kind === 'integer' ? 0 : (target.entity + '-browser').slice(0, field.max_length);
            await dialog.getByPlaceholder('请输入' + field.name, { exact: true }).fill(String(value));
            expected[key] = value;
          }
        }
        const created = observe(target.api + '/create', 'POST');
        const refreshed = observe(target.list);
        await dialog.getByRole('button', { name: /^确\\s*认$|^确\\s*定$/ }).click();
        const captured = await created;
        if (captured.error) throw captured.error;
        const sent = captured.response.request().postDataJSON();
        for (const [key, value] of Object.entries(expected)) assert.equal(sent[key], value, 'Generated form kind: ' + key);
        await checked(Promise.resolve(captured));
        const listed = await checked(refreshed);
        assert(listed.list.some(row => Object.entries(expected).every(([key, value]) => row[key] === value)), 'Submitted record was not returned by real list API');
        await dialog.waitFor({ state: 'hidden' });
        const text = Object.values(expected).find(value => typeof value === 'string');
        if (text) await page.getByText(text, { exact: true }).first().waitFor({ state: 'visible' });
        await page.screenshot({ path: path.join(reportDir, target.entity + '-created.png'), fullPage: true });
        pageResult.real_form_create = true;
        pageResult.typed_values_preserved = true;
      }
      report.pages.push(pageResult);''')
edit("docs/native-baseline.md", "原始生成 ZIP 不改写，`generation.json` 同时记录原始文件与实际挂载文件的哈希。", "原始生成 ZIP 不改写，`generation.json` 同时记录原始文件与实际挂载文件的哈希。未使用的 `Dayjs`、`getDictOptions` 导入仅在确认没有引用时删除，不关闭编译器的未使用检查。整数编辑/查询控件使用 `InputNumber` 并限定零位小数；布尔编辑/查询控件使用有真实 `true/false` 选项的 `RadioGroup`，不提交字符串代替布尔值。Chromium 还会从两个生成页面实际新增记录，检查整数 `0`、布尔 `false` 的请求值和数据库返回值，并保存新增后的页面截图。")
for name, content in changes.items():
    (root / name).write_text(content, encoding="utf-8", newline="\n")
print("Applied generated-field compatibility and strict real UI submission checks")
