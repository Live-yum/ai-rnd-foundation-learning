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
