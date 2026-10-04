# workbench/native_vben.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：Vben兼容适配与生成表单类型保持。** checked_replacement要求精确匹配数量，防止套用到未知源码。原有视图保留；生成表单处理DTO泛型、未使用导入、整数控件及布尔选项，使0和false不变成字符串或空值。

**对应关系：** native_environment/native_modules → Vben完整源码；test_native_vben及真实Chromium。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.filesystem`、`workbench.tools`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `checked_replacement`（L12–L15）：接收`source`、`old`、`new`、`count`、`name`。 控制顺序：L13按`source.count(old) != count`分支；L14抛异常，停止当前正常路径。 调用`source.count`、`ValueError`、`source.replace`。 返回路径：L15的`source.replace(old, new)`。
- `initialize_vben_boundary`（L18–L23）：接收`root`。 源码说明：Create a new local scan boundary, with no upstream history/remotes/hooks.。 控制顺序：L21按`(root / ".git").exists() or (root / ".git").is_symlink()`分支；L22抛异常，停止当前正常路径。 调用`Path(root).resolve`、`Path`、`(root / ".git").exists`、`(root / ".git").is_symlink`、`ValueError`、`run_command`、`str`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `prepare_vben_source`（L26–L183）：接收`root`、`reports`。 控制顺序：L39遍历`[ "fms/config/subject/modules/form.vue", "fms/config/initial-bala…`；L45遍历`[ ("ai/model/model/data.ts", 1), ("mall/product/property/data.ts"…`；L66遍历`modals.items()`；L167遍历`changed.items()`。 调用`Path(root).resolve`、`Path`、`edit`、`modals.items`、`initialize_vben_boundary`、`changed.items`、`sha`、`atomic_text`、`receipts.append`等。 返回路径：L183的`receipts`。
- `prepare_vben_source.edit`（L31–L37）：接收`relative`、`old`、`new`、`count`。 控制顺序：L34按`name not in originals`分支。 调用`path.read_text`、`changed.get`、`checked_replacement`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `adapt_generated_form`（L186–L208）：接收`source`、`class_name`。 源码说明：Move the native generator's legacy getter generic onto the modal hook. Create opens with no record and edit opens with an ID, so the payload is Partial<DTO>. The original codegen ZIP remains unchanged。 控制顺序：L192按`not class_name.isidentifier() or not class_name.startswith("Wb")`分支；L193抛异常，停止当前正常路径。 调用`class_name.isidentifier`、`class_name.startswith`、`ValueError`、`checked_replacement`。 返回路径：L202的`checked_replacement( source, f"modalApi.getData<{dto}>()", "modalApi.getData()", 1, "gener…`。
- `prune_generated_import`（L211–L220）：接收`source`、`identifier`、`declaration`。 源码说明：Remove only an exact unused single import emitted by the pinned generator.。 控制顺序：L213按`declaration not in source`分支；L215按`source.count(declaration) != 1`分支；L216抛异常，停止当前正常路径；L218按`re.search(r"\b" + re.escape(identifier) + r"\b", remaining)`分支。 调用`source.count`、`ValueError`、`source.replace`、`re.search`、`re.escape`。 返回路径：L214的`source`；L219的`source`；L220的`remaining`。
- `adapt_generated_schema`（L223–L268）：接收`source`、`fields`。 源码说明：Preserve declared value kinds in both generated edit and search forms.。 控制顺序：L228遍历`fields`；L232按`field.kind not in {"integer", "boolean"}`分支；L241按`not 1 <= len(list(pattern.finditer(source))) <= 2`分支；L242抛异常，停止当前正常路径。 调用`prune_generated_import`、`field.name.split`、`"".join`、`piece[:1].upper`、`re.compile`、`re.escape`、`len`、`list`、`pattern.finditer`等。 返回路径：L268的`source`。
- `adapt_generated_schema.transform`（L244–L265）：接收`match`。 控制顺序：L246按`field.kind == "integer"`分支；L253按`"component: 'Select'," in block`分支；L257按`block.count("component: 'RadioGroup',") != 1`分支；L258抛异常，停止当前正常路径。 调用`match.group`、`checked_replacement`、`block.count`、`ValueError`。 返回路径：L250的`checked_replacement( block, "componentProps: {", "componentProps: {\n precision: 0,", 1, n…`；L259的`checked_replacement( block, "options: [],", "options: [{ label: '是', value: true }, { labe…`。
- `configure_vben_backend_proxy`（L271–L280）：接收`root`。 源码说明：Preserve relative native APIs while routing preview to the leased backend.。 控制顺序：L277按`source.count(new) == 1 and old not in source`分支。 调用`Path`、`path.read_text`、`source.count`、`checked_replacement`、`atomic_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `workbench/native_vben.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L280。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`13806`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/native_vben.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "e13e6ea877325bdbba0b2bba1d003e5a44a6a3fbbd26cecffb1f1693e30379a9"} -->
````python
# workbench/native_vben.py
"""Reviewed compatibility for pinned Vben 1b14e889; no routes or type checks removed."""

import re
from collections.abc import Sequence
from pathlib import Path

from workbench.domain import FieldSpec
from workbench.filesystem import atomic_text, sha, write_json
from workbench.tools import run_command


def checked_replacement(source: str, old: str, new: str, count: int, name: str) -> str:
    if source.count(old) != count:
        raise ValueError("Pinned Vben compatibility contract changed: " + name)
    return source.replace(old, new)


def initialize_vben_boundary(root: Path) -> None:
    """Create a new local scan boundary, with no upstream history/remotes/hooks."""
    root = Path(root).resolve()
    if (root / ".git").exists() or (root / ".git").is_symlink():
        raise ValueError("Vben compatibility requires a fresh source copy without .git")
    run_command(["git", "init", "--quiet", "--template=", str(root)], root, 30)


def prepare_vben_source(root: Path, reports: Path):
    root = Path(root).resolve()
    originals = {}
    changed = {}

    def edit(relative, old, new, count=1):
        name = "apps/web-antd/src/views/" + relative
        path = root / name
        if name not in originals:
            originals[name] = path.read_text(encoding="utf-8")
        source = changed.get(name, originals[name])
        changed[name] = checked_replacement(source, old, new, count, name)

    for name in [
        "fms/config/subject/modules/form.vue",
        "fms/config/initial-balance/modules/assist-form.vue",
        "fms/ledger/auxiliary-balance/index.vue",
    ]:
        edit(name, "auxiliary-select-modal.vue", "auxiliary-item-select.vue")
    for name, count in [
        ("ai/model/model/data.ts", 1),
        ("mall/product/property/data.ts", 1),
        ("system/dict/data.ts", 2),
    ]:
        edit(name, "componentProps: (values) => {", "componentProps: ({ rootValues }) => {", count)
        edit(name, "disabled: !!values.id", "disabled: !!rootValues?.id", count)
    # Data is declared on useVbenModal<T>; getData() remains possibly undefined.
    modals = {
        "bpm/components/bpmn-process-designer/package/penal/task/task-components/HttpHeaderEditor.vue": "{ headers?: string }",
        "bpm/components/simple-process-design/components/nodes-config/modules/condition-dialog.vue": "typeof conditionData.value",
        "bpm/form/modules/detail.vue": "{ id: number }",
        "crm/customer/detail/modules/distribute-form.vue": "{ id: number; ownerUserId?: number }",
        "crm/permission/modules/form.vue": "CrmPermissionApi.Permission",
        "mall/promotion/coupon/components/send-form.vue": "{ userIds: number[] }",
        "mall/trade/brokerage/user/modules/order-list-modal.vue": "{ id: number }",
        "mall/trade/brokerage/user/modules/user-list-modal.vue": "{ id: number }",
        "system/dept/components/select-modal.vue": "{ selectedList?: SystemDeptApi.Dept[] }",
        "system/social/user/modules/detail.vue": "{ id: number }",
        "system/user/components/select-modal.vue": "{ userIds?: number[] }",
    }
    for name, typ in modals.items():
        edit(name, "= useVbenModal({", f"= useVbenModal<{typ}>({{")
    edit(
        "bpm/components/bpmn-process-designer/package/penal/task/task-components/HttpHeaderEditor.vue",
        "const { headers } = modalApi.getData();",
        "const headers = modalApi.getData()?.headers ?? '';",
    )
    edit(
        "bpm/components/bpmn-process-designer/package/penal/time-event-config/TimeEventConfig.vue",
        "onConfirm: () => helpModalApi.close(),",
        "onConfirm: (): void => {\n    helpModalApi.close();\n  },",
    )
    edit(
        "bpm/components/simple-process-design/components/simple-process-designer.vue",
        "const [ErrorModal, errorModalApi] = useVbenModal({",
        "const [ErrorModal, errorModalApi] = useVbenModal<SimpleFlowNode[]>({",
    )
    edit(
        "mall/promotion/coupon/components/send-form.vue",
        "  modalApi.lock();\n  try {",
        "  const data = modalApi.getData();\n  if (!data?.userIds.length) return;\n  modalApi.lock();\n  try {",
    )
    edit(
        "mall/promotion/coupon/components/send-form.vue",
        "userIds: modalApi.getData().userIds",
        "userIds: data.userIds",
    )
    edit(
        "mall/trade/brokerage/user/modules/user-list-modal.vue",
        "query: async ({ page }, formValues) => {\n          return",
        "query: async ({ page }, formValues) => {\n          const data = modalApi.getData();\n          if (!data) return { list: [], total: 0 };\n          return",
    )
    edit(
        "mall/trade/brokerage/user/modules/user-list-modal.vue",
        "bindUserId: modalApi.getData().id",
        "bindUserId: data.id",
    )
    # Actions callbacks belong to the dependency resolver, not schema context.
    edit(
        "crm/contact/data.ts",
        "      componentProps: (_values, form) => ({\n        api: getCustomerSimpleList,\n        labelField: 'name',\n        valueField: 'id',\n        placeholder: '请选择客户',\n        onChange: () => form.setFieldValue('parentId', undefined),\n      }),",
        "      dependencies: {\n        triggerFields: ['customerId'],\n        componentProps: (_values, form) => ({\n          api: getCustomerSimpleList,\n          labelField: 'name',\n          valueField: 'id',\n          placeholder: '请选择客户',\n          onChange: () => form.setFieldValue('parentId', undefined),\n        }),\n      },",
    )
    edit(
        "crm/receivable/data.ts",
        "      componentProps: (_values, form) => ({\n        api: getCustomerSimpleList,\n        labelField: 'name',\n        valueField: 'id',\n        placeholder: '请选择客户',\n        onChange: () => {\n          form.setFieldValue('contractId', undefined);\n          form.setFieldValue('planId', undefined);\n          form.setFieldValue('price', undefined);\n          form.setFieldValue('returnTime', undefined);\n          form.setFieldValue('returnType', undefined);\n        },\n      }),\n      dependencies: {\n        triggerFields: ['id'],\n        disabled: (values) => values.id,\n      },",
        "      dependencies: {\n        triggerFields: ['id', 'customerId'],\n        disabled: (values) => values.id,\n        componentProps: (_values, form) => ({\n          api: getCustomerSimpleList,\n          labelField: 'name',\n          valueField: 'id',\n          placeholder: '请选择客户',\n          onChange: () => {\n            form.setFieldValue('contractId', undefined);\n            form.setFieldValue('planId', undefined);\n            form.setFieldValue('price', undefined);\n            form.setFieldValue('returnTime', undefined);\n            form.setFieldValue('returnType', undefined);\n          },\n        }),\n      },",
    )
    edit(
        "im/utils/constants.ts",
        "const ImContentTypeNormals: number[] = new Set([",
        "const ImContentTypeNormals: ReadonlySet<number> = new Set([",
    )
    edit(
        "im/utils/constants.ts",
        "const ImContentTypeMedia: number[] = new Set([",
        "const ImContentTypeMedia: ReadonlySet<number> = new Set([",
    )
    edit("im/utils/message.ts", "[...mentions].toSort(", "mentions.toSorted(")
    # Optional cursor fields can be undefined as well as null.
    name = "im/utils/pull.ts"
    edit(name, "let cursor =", "let cursor: PullCursor =")
    edit(name, "storedCursor.lastUpdateTime === null", "storedCursor.lastUpdateTime == null")
    edit(name, "last.updateTime === null", "last.updateTime == null")
    edit(name, "highWater.lastUpdateTime === null", "highWater.lastUpdateTime == null")
    edit(
        name,
        "cursor.lastUpdateTime > highWater.lastUpdateTime",
        "last.updateTime > highWater.lastUpdateTime",
    )
    edit(
        name,
        "cursor.lastUpdateTime === highWater.lastUpdateTime",
        "last.updateTime === highWater.lastUpdateTime",
    )
    edit(name, "cursor.lastId > (highWater.lastId ?? 0)", "last.id > (highWater.lastId ?? 0)")
    edit(
        name,
        "highWater.lastUpdateTime = cursor.lastUpdateTime;",
        "highWater.lastUpdateTime = last.updateTime;",
    )
    edit(name, "highWater.lastId = cursor.lastId;", "highWater.lastId = last.id;")
    edit(
        name,
        ".filter((id): id is number => id !== null);",
        ".filter((id): id is number => typeof id === 'number');",
    )
    edit(name, "nextMinId === null", "nextMinId == null")
    edit(
        "system/area/data.ts",
        "z.string().ip({ message: '请输入正确的 IP 地址' })",
        "z.union([z.ipv4(), z.ipv6()], { error: '请输入正确的 IP 地址' })",
    )
    edit(
        "system/dept/components/select-modal.vue",
        ".filter((id: number) => id !== undefined)",
        ".filter((id): id is number => typeof id === 'number')",
    )
    # Validate every input shape before creating the boundary or changing any file.
    initialize_vben_boundary(root)
    receipts = []
    for name, content in changed.items():
        path = root / name
        before = sha(path)
        atomic_text(path, content)
        receipts.append({"path": name, "before_sha256": before, "after_sha256": sha(path)})
    write_json(
        Path(reports) / "vben-compatibility.json",
        {
            "upstream": "1b14e889f529e245fd620daa720dcea6de0cc5e7",
            "scope": "existing-component-imports-and-current-native-types",
            "independent_git_boundary": True,
            "routes_removed": False,
            "type_checks_disabled": False,
            "files": receipts,
        },
    )
    return receipts


def adapt_generated_form(source: str, class_name: str) -> str:
    """Move the native generator's legacy getter generic onto the modal hook.

    Create opens with no record and edit opens with an ID, so the payload is Partial<DTO>.
    The original codegen ZIP remains unchanged; mounting records before/after hashes.
    """
    if not class_name.isidentifier() or not class_name.startswith("Wb"):
        raise ValueError("Invalid generated Vben class name")
    dto = f"Infra{class_name}Api.{class_name}"
    source = checked_replacement(
        source,
        "= useVbenModal({",
        f"= useVbenModal<Partial<{dto}>>({{",
        1,
        "generated modal hook",
    )
    return checked_replacement(
        source,
        f"modalApi.getData<{dto}>()",
        "modalApi.getData()",
        1,
        "generated modal getter",
    )


def prune_generated_import(source: str, identifier: str, declaration: str) -> str:
    """Remove only an exact unused single import emitted by the pinned generator."""
    if declaration not in source:
        return source
    if source.count(declaration) != 1:
        raise ValueError("Duplicate generated import: " + identifier)
    remaining = source.replace(declaration, "", 1)
    if re.search(r"\b" + re.escape(identifier) + r"\b", remaining):
        return source
    return remaining


def adapt_generated_schema(source: str, fields: Sequence[FieldSpec]) -> str:
    """Preserve declared value kinds in both generated edit and search forms."""
    source = prune_generated_import(
        source, "getDictOptions", "import { getDictOptions } from '@vben/hooks';\n"
    )
    for field in fields:
        # This compatibility shim only repairs the pinned integer/boolean controls.
        # Business enum/date/datetime widgets are mounted later by businessFormSchema;
        # treating them as booleans corrupts the genuine generated source before that hook.
        if field.kind not in {"integer", "boolean"}:
            continue
        first, *rest = field.name.split("_")
        name = first + "".join(piece[:1].upper() + piece[1:] for piece in rest)
        # Guard the pinned template; never consume the next field on shape drift.
        pattern = re.compile(
            r"    \{\n      fieldName: '" + re.escape(name) + r"',\n(?:(?!fieldName:).)*?\n    \},",
            re.DOTALL,
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
                    block, "componentProps: {", "componentProps: {\n        precision: 0,", 1, name
                )
            if "component: 'Select'," in block:
                block = checked_replacement(
                    block, "component: 'Select',", "component: 'RadioGroup',", 1, name
                )
            elif block.count("component: 'RadioGroup',") != 1:
                raise ValueError("Unsupported generated boolean control: " + name)
            return checked_replacement(
                block,
                "options: [],",
                "options: [{ label: '是', value: true }, { label: '否', value: false }],",
                1,
                name,
            )

        source = pattern.sub(transform, source)
    return source


def configure_vben_backend_proxy(root):
    """Preserve relative native APIs while routing preview to the leased backend."""
    path = Path(root) / "apps/web-antd/vite.config.ts"
    source = path.read_text(encoding="utf-8")
    old = "target: 'http://localhost:48080/admin-api',"
    new = "target: `${process.env.VITE_BASE_URL ?? 'http://localhost:48080'}/admin-api`,"
    if source.count(new) == 1 and old not in source:
        return
    changed = checked_replacement(source, old, new, 1, "native backend preview proxy")
    atomic_text(path, changed)
````
