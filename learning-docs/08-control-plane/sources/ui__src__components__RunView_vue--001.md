# ui/src/components/RunView.vue · 1/2

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)

[下一段](ui__src__components__RunView_vue--002.md)

**作用：Vue 3 / Ant Design本机操作台源码。** 显示对话、流式草稿、审批内容、阶段进度与证据；根据当前运行状态开放实际可用的回答、批准、重试和下载操作。

**对应关系：** ui/src及锁文件 → npm ci/test/build → workbench/web → FastAPI本机页面；与生成产品的前端模板是两套不同界面。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `ui/src/components/RunView.vue`；**本文件共有 2 段**。本段覆盖源文件 L1–L375。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`13754`。本段原文以LF换行结束。

<!-- learning-source: {"path": "ui/src/components/RunView.vue", "part": 1, "parts": 2, "encoding": "utf-8", "sha256": "591fbfc7141fe3cd0d3df5dc52801a324246e8ecf86cb05bb2dd90bb3bc93e45"} -->
````vue
<!-- ui/src/components/RunView.vue -->
<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'
import { Modal } from 'ant-design-vue'
import {
  ApartmentOutlined,
  FileTextOutlined,
  MessageOutlined,
  ArrowUpOutlined,
  ArrowRightOutlined,
  CheckOutlined,
  ReloadOutlined,
  DownloadOutlined,
  SafetyCertificateOutlined,
  ThunderboltOutlined,
} from '@ant-design/icons-vue'
import {
  state,
  openRun,
  refreshRun,
  mutationKey,
  clearMutationKey,
  reportError,
  acknowledgeReview,
} from '../state'
import { api, ApiError, downloadRun } from '../api'
import {
  activeStage,
  canAct,
  formatDate,
  gateIdentity,
  gatePayload,
  shortId,
  stages,
  statusColor,
  statusLabel,
  terminal,
  milestoneStatus,
  runNextAction,
} from '../presentation'
import DataDocument from './DataDocument.vue'
import Questionnaire from './Questionnaire.vue'
import StageTimeline from './StageTimeline.vue'
const props = defineProps<{ view: string; runId: string }>()
const emit = defineEmits<{ navigate: [path: string] }>()
let mounted = true
let actionDialog: ReturnType<typeof Modal.confirm> | undefined
function cancelActionDialog() {
  actionDialog?.destroy()
  actionDialog = undefined
}
onBeforeUnmount(() => {
  mounted = false
  busyDraft.value = ''
  answer.value = ''
  cancelActionDialog()
})
watch(() => [props.runId, props.view], cancelActionDialog)
function sameTarget(id: string, hash: string) {
  return mounted && props.runId === id && state.run?.id === id && location.hash === hash
}
function jumpLatest() {
  autoScroll.value = true
  chatEnd.value?.scrollIntoView({ behavior: 'smooth' })
}
const busyDraft = ref('')
const answer = ref(''),
  submitting = ref(false),
  reviewed = ref(false),
  tab = ref('overview'),
  showDetails = ref(false),
  detailTab = ref('report'),
  activeReports = ref<string[]>([]),
  eventStage = ref('all'),
  eventKind = ref('all'),
  eventLimit = ref(30),
  expandedEvents = ref(new Set<number>()),
  chatEnd = ref<HTMLElement>(),
  autoScroll = ref(true)
const run = computed(() => state.run),
  gate = computed(() => run.value?.pending),
  project = computed(() => state.projects.find((p) => p.id === run.value?.project_id)),
  stageIndex = computed(() => activeStage(run.value, state.events))
const blocked = computed(() => {
  const b = gate.value?.data?.blocked || gate.value?.data?.requirement?.unsupported
  return Array.isArray(b) ? b : b ? [b] : []
})
const capabilityConflicts = computed(() => gate.value?.data?.capability_conflicts || [])
const capabilityAlternatives = computed(() => [
  ...new Set(capabilityConflicts.value.flatMap((item: any) => item.alternatives || [])),
])
const hasScopeChoices = computed(() =>
  gate.value?.data?.requirement?.question_items?.some(
    (item: any) => Array.isArray(item.options) && item.options.length > 0,
  ),
)
const canSubmit = computed(
  () => state.online && state.authenticated && !submitting.value && !state.stale,
)
const modelReady = computed(() => !!state.settings?.ready)
const modelFreeApproval = computed(() => gate.value?.needs_model?.approve === false)
const partialScope = computed(() => gate.value?.data?.delivery_kind === 'partial')
const scopeLabel = computed(() => (partialScope.value ? '部分交付范围' : '已审阅交付范围'))
const isQuestions = computed(() => gate.value?.actions.includes('answer'))
const completeCount = computed(
  () =>
    stages.filter((_, index) => milestoneStatus(index, run.value, state.events) === 'done').length,
)
const gateTitle = computed(() =>
  gate.value?.stage === 'requirements'
    ? '先对齐需求，再往前走'
    : ['design', 'extension_design'].includes(gate.value?.stage || '')
      ? '把方案摊开，一起检查'
      : gate.value?.stage === 'extension_scope'
        ? partialScope.value
          ? '明确部分成果和仍未完成的范围'
          : '核对验收范围再准备交付'
        : ['delivery', 'extension_delivery'].includes(gate.value?.stage || '')
          ? '先看验证证据，再确认交付'
          : '一起把需求说清楚',
)
function designData(key: string) {
  const d = gate.value?.data || {}
  const plan = d.extension?.baseline || d.plan || {}
  if (key === 'atomic') return { source_units: d.source_units, atomic_review: d.atomic_review }
  if (key === 'data') return plan.entities || plan
  if (key === 'tasks') return d.extension?.implementation?.tasks || d.tasks || {}
  if (key === 'interfaces')
    return (
      d.extension?.implementation?.scenarios || plan.endpoints || plan.api || plan.business || plan
    )
  return (
    d.extension || {
      ...plan,
      ...(d.native_normalization?.field_mappings?.length
        ? { native_normalization: d.native_normalization }
        : {}),
    }
  )
}
const reviewData = computed(() => {
  const d = gate.value?.data || {}
  if (gate.value?.stage === 'requirements' || gate.value?.stage === 'clarification')
    return d.requirement || d
  if (['design', 'extension_design'].includes(gate.value?.stage || '')) return designData(tab.value)
  return d
})
const downloadable = computed(() => ['READY', 'SOURCE_READY'].includes(run.value?.status || ''))
const evidence = computed(
  () => state.report['verification.json'] || state.report['daytona-verification.json'],
)
const delivery = computed(() =>
  ['delivery', 'extension_scope', 'extension_delivery'].includes(gate.value?.stage || '')
    ? gate.value?.data
    : state.report['delivery.json'] || run.value?.result || {},
)
const extensionCoverageNotice = computed(() => {
  if (delivery.value?.delivery_kind === 'partial')
    return '本次仅交付明确批准的部分成果。完整原始需求、外部服务和未验证迁移仍保留，下载不代表这些义务已完成。'
  const level =
    delivery.value?.coverage_level || state.report['extension-coverage.json']?.coverage_level
  if (level === 'reviewed-executable-contract')
    return '仅证明已审阅可执行合同通过运行验收，不代表全部原始需求的语义均已证明。请对照原始来源与验收合同查看覆盖范围。'
  if (level === 'bounded-business-slice')
    return '仅完成独立业务切片验收；完整原始需求与外部服务义务仍有未完成项，未经明确部分范围批准不能交付。'
  if (level === 'operator-reviewed-atomic-contracts')
    return '通过的是人工明确审阅的原子业务合同及独立物理读回，不保证任意自然语言需求的语义完整性。'
  return ''
})
const eventsReversed = computed(() =>
  [...state.events]
    .filter((event) => {
      if (event.kind === 'assistant_delta') return false
      const kind = ['stage', 'step'].includes(event.kind)
        ? 'stage'
        : event.kind.startsWith('assistant_')
          ? 'model'
          : 'status'
      if (eventKind.value !== 'all' && eventKind.value !== kind) return false
      if (eventStage.value === 'all') return true
      const name = event.data.name || event.data.stage || ''
      return stages
        .find((stage) => stage.key === eventStage.value)
        ?.steps.some((step) => name === step || name.startsWith(step + ':'))
    })
    .reverse(),
)
const visibleEvents = computed(() => eventsReversed.value.slice(0, eventLimit.value))
watch([eventStage, eventKind], () => {
  eventLimit.value = 30
  expandedEvents.value.clear()
})
function openReport(name: string) {
  detailTab.value = 'report'
  activeReports.value = [name]
  showDetails.value = true
}
function toggleEvent(id: number, event: Event) {
  if ((event.target as HTMLDetailsElement).open) expandedEvents.value.add(id)
  else expandedEvents.value.delete(id)
}
watch(
  () => gateIdentity(gate.value),
  () => {
    reviewed.value = false
    answer.value = ''
    tab.value = 'overview'
  },
)
watch(
  () => state.messages.map((m) => m.content).join('').length,
  () => {
    if (autoScroll.value)
      nextTick(() => chatEnd.value?.scrollIntoView({ block: 'end', behavior: 'smooth' }))
  },
)
const route = (view: string) => emit('navigate', `run/${props.runId}/${view}`)
function phaseLabel(phase: string) {
  return (
    ({ started: '开始执行', waiting: '等待确认', completed: '已完成', failed: '失败' } as any)[
      phase
    ] || phase
  )
}
function eventSummary(event: any) {
  const data = event.data || {}
  if (event.kind === 'stage')
    return `${data.name} · 第 ${data.round || 1} 轮 · ${phaseLabel(data.phase)}`
  if (event.kind === 'step') return `${data.name} 步骤已完成，产物已保存`
  if (event.kind === 'status')
    return `${statusLabel(data.status)}${data.error ? ' · ' + data.error : ''}`
  if (event.kind === 'delegation') return data.enabled ? '智能推荐持续委托已启用' : '已恢复人工确认'
  if (event.kind.startsWith('assistant_'))
    return `${data.stage || '模型'} · ${event.kind === 'assistant_completed' ? '响应已完成，' + (data.validation === 'validated' ? '结构校验通过' : '等待校验') : event.kind === 'assistant_failed' ? '响应未通过校验或请求失败' : '开始响应'}`
  return data.message || data.name || event.kind
}
async function decide(action: string, text = '', answers?: any[]) {
  if (!gate.value || !canSubmit.value || !canAct(run.value, action)) return
  if (
    !modelReady.value &&
    action !== 'reject' &&
    !(action === 'approve' && modelFreeApproval.value)
  )
    return
  if (action === 'approve' && !reviewed.value) return
  const current = structuredClone(JSON.parse(JSON.stringify(gate.value))),
    body = gatePayload(current, action, text, answers),
    targetId = props.runId,
    targetHash = location.hash,
    fingerprint = targetId + JSON.stringify(body)
  submitting.value = true
  state.error = ''
  try {
    await api(`/runs/${targetId}/resume`, {
      method: 'POST',
      body,
      key: mutationKey(fingerprint),
    })
    clearMutationKey(fingerprint)
    if (!sameTarget(targetId, targetHash)) return
    answer.value = ''
    await openRun(targetId)
    if (!sameTarget(targetId, targetHash)) return
    acknowledgeReview()
    state.notice = action === 'reject' ? '已提交拒绝决定' : '已提交，后台将继续这一轮运行'
    if (action !== 'reject') route('conversation')
  } catch (e) {
    if (!sameTarget(targetId, targetHash)) return
    if (e instanceof ApiError && e.status === 409) {
      await refreshRun().catch(reportError)
      state.stale = true
      reviewed.value = false
      state.error = '当前审核版本已变化。请重新阅读最新内容，再手动决定；不会自动重试。'
    } else reportError(e)
  } finally {
    submitting.value = false
  }
}
function reject() {
  const targetId = props.runId,
    targetHash = location.hash,
    identity = gateIdentity(gate.value)
  actionDialog = Modal.confirm({
    title: '拒绝当前版本？',
    content: '将记录你的拒绝决定，并结束当前流程。历史记录仍会保留。',
    okText: '确认拒绝',
    cancelText: '返回审核',
    okButtonProps: { danger: true },
    onOk: () => {
      if (!sameTarget(targetId, targetHash) || gateIdentity(gate.value) !== identity) return
      return decide('reject')
    },
  })
}
async function retry() {
  if (
    submitting.value ||
    !state.online ||
    (!modelReady.value && !run.value?.model_free_retry) ||
    gate.value
  )
    return
  submitting.value = true
  const targetId = props.runId,
    targetHash = location.hash,
    f = 'retry:' + targetId + run.value?.status
  try {
    await api(`/runs/${targetId}/retry`, { method: 'POST', key: mutationKey(f) })
    clearMutationKey(f)
    if (sameTarget(targetId, targetHash)) await refreshRun()
  } catch (e) {
    if (sameTarget(targetId, targetHash)) reportError(e)
  } finally {
    submitting.value = false
  }
}
function automation() {
  if (!run.value || terminal(run.value) || submitting.value || !state.online) return
  if (!run.value.auto_mode && capabilityConflicts.value.length) return
  const enabled = !run.value.auto_mode,
    targetId = props.runId,
    targetHash = location.hash,
    identity = gateIdentity(gate.value)
  const submit = async () => {
    if (!sameTarget(targetId, targetHash) || gateIdentity(gate.value) !== identity) return
    submitting.value = true
    const f = 'automation:' + targetId + enabled
    try {
      await api(`/runs/${targetId}/automation`, {
        method: 'POST',
        body: { enabled, accepted: enabled },
        key: mutationKey(f),
      })
      clearMutationKey(f)
      if (!sameTarget(targetId, targetHash)) return
      await refreshRun()
      acknowledgeReview()
    } catch (e) {
      if (sameTarget(targetId, targetHash)) reportError(e)
    } finally {
      submitting.value = false
    }
  }
  if (enabled)
    actionDialog = Modal.confirm({
      title: '启用智能推荐持续委托？',
      content:
        'AI 会决定未明确项，并自动批准本轮后续设计与交付，不再逐项询问。测试门禁仍有效。可随时恢复人工确认，但不会撤销已经执行的动作。',
      okText: '确认授权',
      cancelText: '保持人工确认',
      onOk: submit,
    })
  else void submit()
}
async function download() {
  if (!downloadable.value || submitting.value || !state.online) return
  submitting.value = true
  try {
    await downloadRun(props.runId)
  } catch (e) {
    reportError(e)
  } finally {
    submitting.value = false
  }
}
function send() {
  const action = canAct(run.value, 'answer') ? 'answer' : 'revise'
  if (!answer.value.trim()) return
  void decide(action, answer.value.trim())
}
function keydown(event: KeyboardEvent) {
  if (event.key === 'Enter' && !event.shiftKey && !event.isComposing && event.keyCode !== 229) {
    event.preventDefault()
    send()
  }
}
````
