# 中规模项目：库存采购协作台

我要一个内部小团队使用的库存采购协作台，覆盖供应商、物料库存登记和采购审批/收货协作。使用 python-basic、simple-admin 前端、SQLite 数据库。只允许 suppliers、items、purchase_orders 三个实体及表内字段。全部业务数据 shared，由明确的角色和行权限控制。账号由管理员在系统中创建，不开放自助注册，初始化管理员角色 manager；默认非管理角色 buyer。

界面中文。下表的英文实体、字段、角色、动作和枚举值是稳定接口契约，请严格保留；可为它们补充中文显示标签。经理维护供应商/物料并审批采购，采购员仅能处理本人创建的采购单，仓管查看采购并登记收货。收货时间由状态动作写入，普通编辑不能伪造状态和时间。库存数量是手工库存台账：仓管核验收货后在物料编辑页更新 stock；本版不要求收货动作自动记库存、不要求金额计算、跨单据自动核销或外部供应商接入。

## 字段清单

未特别标注的文本字段最大长度为 200；未声明的 searchable、filterable、date_range 均为 false。所有普通 required 字段必须提交；负责人、状态及状态时间遵守业务专用操作。系统 id、创建者、创建时间等由模板提供，不加入业务字段清单。

| 实体 | 字段 | 约束 |
| --- | --- | --- |
| suppliers | name | text；必填；最大长度 200；关键词搜索 |
| suppliers | contact | text；必填；最大长度 200 |
| items | name | text；必填；最大长度 200；关键词搜索 |
| items | sku | text；必填；最大长度 60 |
| items | supplier_id | text；必填 |
| items | stock | integer；必填；最小值 0；最大值 100000 |
| purchase_orders | title | text；必填；最大长度 200；关键词搜索 |
| purchase_orders | item_id | text；必填 |
| purchase_orders | quantity | integer；必填；最小值 1；最大值 100000 |
| purchase_orders | state | enum；必填；枚举 draft, approved, received；精确筛选 |
| purchase_orders | ordered_on | date；必填 |
| purchase_orders | received_at | datetime；可空 |

## 明确的业务契约

以下 JSON 是本次用户需求中的可执行业务约束，不是审批结果或模型答案。请由需求分析记录并由设计生成完整 Plan.business，保留全部条目；可补充各处必需的中文 label。权限是完整的 grant-only 授权表：没有列出的角色/实体/动作一律拒绝，不取多个角色权限的并集。所有实体启用 archive、notes、audit；archive 保留关联和历史。日期时间使用带时区的 ISO 8601；统计时间为 UTC，时长单位 seconds。无需额外扩展代码。

```json
{
  "roles": [{"name": "manager"},{"name": "buyer"},{"name": "warehouse"}],
  "registration": {"enabled": false,"default_role": "buyer"},
  "bootstrap_role": "manager",
  "role_admin_roles": ["manager"],
  "resources": [
    {"entity": "suppliers","assignee_field": null,"archive": true,"notes": true,"audit": true},
    {"entity": "items","assignee_field": null,"archive": true,"notes": true,"audit": true},
    {"entity": "purchase_orders","assignee_field": null,"archive": true,"notes": true,"audit": true}
  ],
  "relations": [
    {"entity": "items","field": "supplier_id","target_entity": "suppliers","on_delete": "restrict"},
    {"entity": "purchase_orders","field": "item_id","target_entity": "items","on_delete": "restrict"}
  ],
  "permissions": [
    {
      "role": "manager",
      "entity": "suppliers",
      "actions": ["create","read","update","archive","add_note","read_history","read_audit"],
      "scope": "all"
    },
    {
      "role": "manager",
      "entity": "items",
      "actions": ["create","read","update","archive","add_note","read_history","read_audit","read_metrics"],
      "scope": "all"
    },
    {
      "role": "manager",
      "entity": "purchase_orders",
      "actions": ["create","read","update","archive","transition","add_note","read_history","read_audit","read_metrics"],
      "scope": "all"
    },
    {"role": "buyer","entity": "suppliers","actions": ["read"],"scope": "all"},
    {"role": "buyer","entity": "items","actions": ["read"],"scope": "all"},
    {"role": "buyer","entity": "purchase_orders","actions": ["create","read","update","add_note","read_history"],"scope": "own"},
    {"role": "warehouse","entity": "suppliers","actions": ["read"],"scope": "all"},
    {"role": "warehouse","entity": "items","actions": ["read","update"],"scope": "all"},
    {"role": "warehouse","entity": "purchase_orders","actions": ["read","transition","add_note","read_history"],"scope": "all"}
  ],
  "workflows": [
    {
      "entity": "purchase_orders",
      "status_field": "state",
      "initial": "draft",
      "transitions": [
        {"name": "approve","from_states": ["draft"],"to_state": "approved","roles": ["manager"],"set_timestamp": null},
        {"name": "receive","from_states": ["approved"],"to_state": "received","roles": ["manager","warehouse"],"set_timestamp": "received_at"}
      ]
    }
  ],
  "notifications": [
    {"entity": "purchase_orders","event": "transitioned","recipient": "creator","transition": "approve","due_field": null,"channel": "in_app"},
    {"entity": "purchase_orders","event": "transitioned","recipient": "creator","transition": "receive","due_field": null,"channel": "in_app"}
  ],
  "metrics": [
    {"name": "item_count","entity": "items","kind": "count"},
    {"name": "purchases_by_state","entity": "purchase_orders","kind": "group_count","group_by": "state"}
  ]
}
```

## 可执行验收

- 管理员创建供应商和物料，采购员基于可见物料创建采购单；关联必须指向真实、可见记录，不能只保存无效字符串。物料 stock 不能小于 0，采购 quantity 必须为正整数。
- 采购状态默认 draft，经理 approve 后为 approved，经理或仓管 receive 后为 received，同时写入 received_at；不能从 draft 直接收货，也不能通过普通编辑伪造状态或收货时间。采购员没有审批或收货权限。
- 两个采购员只能读取和修改自己创建的采购单；仓管能查看全部采购单和更新物料 stock，不能管理账号或删除主数据。
- 收货后，仓管手动把库存从 5 登记为 17，刷新后采购状态和库存分别正确保存，不把手工操作冒充自动库存核算。
- 每次业务变更保留服务端操作人和时间的历史。审批及收货给采购单创建人发送站内提醒。
- 经理可查看物料数量和采购状态分组统计；采购员无统计授权。实际浏览器检查三模块、角色权限与状态操作。ZIP 独立启动且重启后业务数据仍然正确。

## 生成方式

通过当前平台正常的需求分析、设计、生成、独立验收和交付关卡（模型审阅为可选项）执行。未明确的展示细节可采用合理默认并记录；不得删改上述业务义务、增加不必要的功能或编造测试通过。
