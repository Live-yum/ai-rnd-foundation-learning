"""Reviewed compatibility for pinned Vben 1b14e889; no routes or type checks removed."""

from pathlib import Path

from workbench.filesystem import atomic_text, sha, write_json


def prepare_vben_source(root, reports):
    root = Path(root).resolve()
    originals = {}
    changed = {}

    def edit(relative, old, new, count=1):
        name = "apps/web-antd/src/views/" + relative
        path = root / name
        if name not in originals:
            originals[name] = path.read_text(encoding="utf-8")
        source = changed.get(name, originals[name])
        if source.count(old) != count:
            raise ValueError("Pinned Vben compatibility contract changed: " + name)
        changed[name] = source.replace(old, new)

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
    edit(name, "cursor.lastUpdateTime > highWater.lastUpdateTime", "last.updateTime > highWater.lastUpdateTime")
    edit(name, "cursor.lastUpdateTime === highWater.lastUpdateTime", "last.updateTime === highWater.lastUpdateTime")
    edit(name, "cursor.lastId > (highWater.lastId ?? 0)", "last.id > (highWater.lastId ?? 0)")
    edit(name, "highWater.lastUpdateTime = cursor.lastUpdateTime;", "highWater.lastUpdateTime = last.updateTime;")
    edit(name, "highWater.lastId = cursor.lastId;", "highWater.lastId = last.id;")
    edit(name, ".filter((id): id is number => id !== null);", ".filter((id): id is number => typeof id === 'number');")
    edit(name, "nextMinId === null", "nextMinId == null")
    edit(
        "system/area/data.ts",
        "z.string().ip({ message: '请输入正确的 IP 地址' })",
        "z.union([z.ipv4(), z.ipv6()], { error: '请输入正确的 IP 地址' })",
    )
    # Validate all 25 input shapes before changing the first file.
    receipts = []
    for name, content in changed.items():
        path = root / name
        before = sha(path)
        atomic_text(path, content)
        receipts.append({"path": name, "before_sha256": before, "after_sha256": sha(path)})
    write_json(Path(reports) / "vben-compatibility.json", {
        "upstream": "1b14e889f529e245fd620daa720dcea6de0cc5e7",
        "scope": "existing-component-imports-and-current-native-types",
        "routes_removed": False,
        "type_checks_disabled": False,
        "files": receipts,
    })
    return receipts
