# ui/src/presentation.ts · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：Vue 3 / Ant Design本机操作台源码。** 把已验证的运行阶段、消息事件与关卡身份投影为显示状态，失败草稿和完成结果采用不同呈现。页面文案不能替代后台状态判断。

**对应关系：** ui/src及锁文件 → npm ci/test/build → workbench/web → FastAPI本机页面；与生成产品的前端模板是两套不同界面。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `ui/src/presentation.ts`；**本文件共有 1 段**。本段覆盖源文件 L1–L279。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`9141`。本段原文以LF换行结束。

<!-- learning-source: {"path": "ui/src/presentation.ts", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "6594b2bf84937c46f3254c0865e75bf43b5698e47507675d4d05f4602829576e"} -->
````typescript
// ui/src/presentation.ts
import type { Gate, Run, RunEvent, ChatMessage } from './types'
export const stages = [
  {
    key: 'requirements',
    label: '需求澄清',
    description: '补充角色、范围与目标',
    steps: ['analyse', 'requirements', 'source_context'],
  },
  {
    key: 'plan',
    label: '开发计划',
    description: '拆解任务与验收标准',
    steps: ['plan', 'extension_plan'],
  },
  {
    key: 'design',
    label: '设计评审',
    description: '确认架构与数据模型',
    steps: ['design', 'extension_design'],
  },
  {
    key: 'code',
    label: '生成与编码',
    description: '按已批准方案串行执行',
    steps: ['generate', 'code', 'extension_generate', 'extension_code'],
  },
  {
    key: 'verify',
    label: '验证与修复',
    description: '验证、修复与环境检查',
    steps: [
      'verify',
      'repair',
      'sandbox',
      'model_review',
      'extension_verify',
      'extension_repair',
      'extension_aggregate',
      'extension_integration_repair',
    ],
  },
  {
    key: 'delivery',
    label: '交付确认',
    description: '审核证据后开放下载',
    steps: ['package', 'delivery', 'extension_scope', 'extension_package', 'extension_delivery'],
  },
]
export const statusLabels: Record<string, string> = {
  QUEUED: '已排队',
  RUNNING: '执行中',
  WAITING_CLARIFICATION: '等待回答',
  WAITING_REQUIREMENTS: '等待需求确认',
  WAITING_PLAN: '等待计划确认',
  WAITING_DESIGN: '等待设计确认',
  WAITING_DELIVERY: '等待交付确认',
  WAITING_EXTENSION_DESIGN: '等待模块设计确认',
  WAITING_EXTENSION_SCOPE: '等待交付范围确认',
  WAITING_EXTENSION_DELIVERY: '等待模块交付确认',
  BLOCKED: '存在阻塞',
  FAILED: '运行失败',
  PAUSED_LIMIT: '预算暂停',
  READY: '运行级交付',
  SOURCE_READY: '源码级交付',
  REJECTED: '已拒绝',
}
export const statusLabel = (status?: string) =>
  status ? statusLabels[status] || status : '尚未运行'
export function statusColor(status?: string) {
  if (status === 'READY') return 'green'
  if (status === 'SOURCE_READY') return 'cyan'
  if (['FAILED', 'REJECTED'].includes(status || '')) return 'red'
  if (status?.startsWith('WAITING') || ['BLOCKED', 'PAUSED_LIMIT'].includes(status || ''))
    return 'gold'
  return 'blue'
}
export const formatDate = (value?: string) =>
  value
    ? new Intl.DateTimeFormat('zh-CN', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      }).format(new Date(value))
    : '—'
export const shortId = (id?: string) => (id ? id.slice(0, 8) : '—')
export const terminal = (run?: Run | null) =>
  !!run && ['READY', 'SOURCE_READY', 'REJECTED'].includes(run.status)
export function canAct(run: Run | null, action: string) {
  const gate = run?.pending
  return (
    !!gate &&
    gate.actions?.includes(action) &&
    (action !== 'approve' || gate.can_approve === true) &&
    !!gate.gate_id &&
    !!gate.digest &&
    gate.version !== undefined
  )
}
export function gateIdentity(gate?: Gate | null) {
  return gate ? `${gate.gate_id}:${gate.version}:${gate.digest}` : ''
}
export function activeStage(run: Run | null, events: RunEvent[]) {
  if (!run) return 0
  if (['READY', 'SOURCE_READY'].includes(run.status)) return 5
  const newest = [...events].reverse()
  // Model lifecycle events do not supersede the authoritative workflow node.
  const workflow = newest.find((event) => event.kind === 'stage' && event.data?.name)
  const legacyStep = newest.find((event) => event.kind === 'step' && event.data?.name)
  const model = newest.find((event) => event.kind.startsWith('assistant_') && event.data?.stage)
  const raw =
    run.pending?.stage ||
    run.current_step ||
    workflow?.data.name ||
    legacyStep?.data.name ||
    model?.data.stage ||
    'requirements'
  const aliases: Record<string, string> = {
    planning: 'plan',
    coding: 'code',
    review: 'model_review',
    clarification: 'requirements',
  }
  const stage = aliases[raw] || raw
  return Math.max(
    0,
    stages.findIndex(
      (item) =>
        item.key === stage ||
        item.steps.some((step) => stage === step || stage.startsWith(step + ':')),
    ),
  )
}

export function applyMessageEvent(messages: ChatMessage[], event: RunEvent) {
  if (!event.kind.startsWith('assistant_')) return
  const data = event.data,
    id = data.message_id
  if (!id) return
  let message = messages.find((m) => (m.message_id || m.id) === id)
  if (!message) {
    message = {
      message_id: id,
      id,
      role: 'assistant',
      content: '',
      validation: 'pending',
      created_at: event.created_at,
    }
    messages.push(message)
  }
  if (event.kind === 'assistant_delta')
    message.content = (message.content || '') + (data.text || '')
  if (event.kind === 'assistant_completed') {
    if (typeof data.content === 'string') message.content = data.content
    message.status = data.status || 'completed'
  }
  if (event.kind === 'assistant_failed') {
    if (typeof data.content === 'string') message.content = data.content
    message.status = data.status || 'failed'
  }
  if (event.kind === 'assistant_start') message.status = 'streaming'
  for (const key of ['stage', 'validation', 'transport', 'response_id', 'code', 'diagnostic'])
    if (data[key] !== undefined) message[key] = data[key]
}
export function gatePayload(gate: Gate, action: string, text = '', answers?: unknown[]) {
  return {
    gate_id: gate.gate_id,
    version: gate.version,
    digest: gate.digest,
    action,
    ...(['answer', 'revise'].includes(action) ? { text } : {}),
    ...(['approve', 'reject', 'recommend'].includes(action)
      ? { approved: action !== 'reject' }
      : {}),
    ...(answers ? { answers } : {}),
  }
}
export const fieldLabels: Record<string, string> = {
  summary: '产品目标',
  title: '方案名称',
  users: '使用角色',
  data_scope: '数据范围',
  features: '第一版范围',
  acceptance: '验收标准',
  assumptions: '待核对假设',
  unsupported: '阻塞项',
  limitations: '能力边界',
  recommendations: '建议',
  facts: '已确认信息',
  field_requirements: '字段要求',
  entity_requirements: '实体要求',
  additional_entities: '允许新增实体',
  tasks: '开发任务',
  entities: '数据模型',
  fields: '字段',
  name: '名称',
  label: '名称',
  kind: '类型',
  required: '必填',
  description: '说明',
  modules: '模块',
  architecture: '架构',
  endpoints: '接口设计',
  routes: '路由',
  dependencies: '依赖',
  constraints: '约束',
  risks: '风险',
  changes: '变更',
  checks: '检查项',
  passed: '通过',
  failed: '失败',
  status: '状态',
  mode: '验收模式',
  package: '交付文件',
  sha256: 'SHA-256',
  requirements: '需求',
  plan: '开发计划',
  design: '设计',
  verification: '验证结果',
  delivery: '交付说明',
  options: '技术选型',
  frontend: '前端',
  backend: '后端',
  database: '数据库',
  path: '路径',
  method: '方法',
  permissions: '权限',
  roles: '角色',
  relations: '关联',
  business: '业务合同',
  acceptance_results: '验收结果',
  max_length: '最大长度',
  min_length: '最小长度',
  choices: '允许选项',
  choice_labels: '选项显示名称',
  searchable: '关键词搜索',
  filterable: '精确筛选',
  date_range: '日期范围筛选',
  validation_level: '验收等级',
  coverage_level: '覆盖证明范围',
  full_request_complete: '全部原始需求是否独立证明',
  atomic_review: '原子义务与完整分解审阅',
  obligations: '原子业务义务',
  assertion: '必须满足的业务断言',
  complete_source_ids: '拟确认完整覆盖的原文来源',
  remaining_source_ids: '仍未完成的原文来源',
  remaining_obligations: '仍未完成的义务',
  natural_language_semantics_proven: '任意自然语言语义是否已证明',
  delivery_kind: '交付范围类型',
  readiness: '依赖、迁移与外部前提',
  unverified_prerequisites: '尚未独立验证的外部前提',
  existing_schema_migration: '已有数据库迁移证据',
  source_units: '原始需求来源',
  acceptance_policy: '独立验收策略',
  acceptance_contract_digest: '已批准验收合同摘要',
  custom_rules: '自定义业务规则',
  accept_examples: '应通过的示例',
  reject_examples: '应拒绝的示例',
  file_count: '交付文件数',
  model_review: '模型复核结果',
  review_conflicts: '尚未解决的复核遗漏项',
  requires_source_rereview: '需要重新审阅来源完整性',
  pre_review_complete_source_ids: '复核前曾声明完整的来源',
  observations: '复核观察',
  uncovered_requirements: '尚未覆盖的需求',
  duration_seconds: '耗时（秒）',
  returncode: '进程返回码',
  created_at: '记录时间',
  updated_at: '更新时间',
  exit_code: '退出状态',
  artifact_path: '产物路径',
  result: '结果',
  enabled: '已启用',
  source: '来源',
  backend_tests: '后端测试',
  frontend_build: '前端构建',
  output: '输出摘要',
}
````
