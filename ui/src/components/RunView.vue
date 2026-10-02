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
  ClockCircleOutlined,
  ReloadOutlined,
  DownloadOutlined,
  SafetyCertificateOutlined,
  ThunderboltOutlined,
  ExclamationCircleOutlined,
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
} from '../presentation'
import DataDocument from './DataDocument.vue'
import Questionnaire from './Questionnaire.vue'
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
    (item: any) => item.id === 'registration_scope',
  ),
)
const canSubmit = computed(
  () => state.online && state.authenticated && !submitting.value && !state.stale,
)
const modelReady = computed(() => !!state.settings?.ready)
const isQuestions = computed(() => gate.value?.actions.includes('answer'))
const stepEvents = computed(() =>
  state.events.filter((e) => e.kind === 'stage' || e.kind === 'step'),
)
const completeCount = computed(
  () =>
    new Set(
      stepEvents.value
        .filter((e) => e.kind === 'step' || e.data.phase === 'completed')
        .map((e) => e.data.name),
    ).size,
)
const gateTitle = computed(() =>
  gate.value?.stage === 'requirements'
    ? '先对齐需求，再往前走'
    : gate.value?.stage === 'design'
      ? '把方案摊开，一起检查'
      : gate.value?.stage === 'delivery'
        ? '先看验证证据，再确认交付'
        : '一起把需求说清楚',
)
const reviewData = computed(() => {
  const d = gate.value?.data || {}
  if (gate.value?.stage === 'requirements' || gate.value?.stage === 'clarification')
    return d.requirement || d
  if (gate.value?.stage === 'design') {
    if (tab.value === 'data') return d.plan?.entities || d.plan || {}
    if (tab.value === 'tasks') return d.tasks || {}
    if (tab.value === 'interfaces')
      return d.plan?.endpoints || d.plan?.api || d.plan?.business || d.plan || {}
    return d.plan || d
  }
  return d
})
const downloadable = computed(() => ['READY', 'SOURCE_READY'].includes(run.value?.status || ''))
const evidence = computed(
  () => state.report['verification.json'] || state.report['daytona-verification.json'],
)
const delivery = computed(() =>
  gate.value?.stage === 'delivery'
    ? gate.value.data
    : state.report['delivery.json'] || run.value?.result || {},
)
const eventsReversed = computed(() =>
  [...state.events].filter((e) => !e.kind.startsWith('assistant_delta')).reverse(),
)
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
function milestone(index: number) {
  // A restored earlier gate invalidates later-stage completion for this revision.
  // Historical events remain inspectable, but aren't this scope's progress.
  if (gate.value && index === stageIndex.value) return 'waiting'
  if (index > stageIndex.value) return 'pending'
  const relevant = stepEvents.value.filter((e) =>
      stages[index].steps.some((s) => e.data.name === s || e.data.name?.startsWith(s + ':')),
    ),
    last = relevant.at(-1)
  if (!last) return 'pending'
  if (last.kind === 'step' || last.data.phase === 'completed') return 'done'
  if (last.data.phase === 'failed') return 'failed'
  if (last.data.phase === 'waiting') return 'waiting'
  return 'running'
}
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
  if (!modelReady.value && action !== 'reject') return
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
  if (submitting.value || !state.online || !modelReady.value || gate.value) return
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
function reread() {
  acknowledgeReview()
  reviewed.value = false
  route('review')
}
</script>
<template>
  <div v-if="state.loading" class="page">
    <a-skeleton active :paragraph="{ rows: 9 }" />
    <p class="muted">正在读取保存的运行、对话与事件…</p>
  </div>
  <div v-else-if="!run" class="page">
    <a-empty description="暂时无法读取这轮运行"
      ><a-button @click="openRun(runId)">重新读取</a-button></a-empty
    >
  </div>
  <div
    v-else
    class="run-view"
    data-testid="run-workspace"
    :data-run-id="run.id"
    :data-status="run.status"
  >
    <header class="run-heading">
      <div>
        <h1>
          {{ project?.title || '项目 ' + shortId(run.project_id) }}
          <a-tag :color="statusColor(run.status)">{{ statusLabel(run.status) }}</a-tag>
        </h1>
        <p>
          项目 {{ shortId(run.project_id) }} <span>·</span> 当前运行 {{ shortId(run.id) }}
          <span>·</span> {{ run.template }}
        </p>
      </div>
      <div class="header-actions">
        <a-button @click="route(view === 'progress' ? 'conversation' : 'progress')"
          ><ApartmentOutlined aria-hidden="true" />{{
            view === 'progress' ? '返回对话' : '查看进度'
          }}</a-button
        ><a-button @click="showDetails = true"
          ><FileTextOutlined aria-hidden="true" />项目资料</a-button
        >
      </div>
    </header>
    <div v-if="state.stream === 'reconnecting' || state.stream === 'offline'" class="run-notice">
      <a-alert
        type="warning"
        show-icon
        message="实时连接已中断，正在保留最后一次数据"
        description="断开页面连接不会停止后台任务。重新连接后从保存的事件游标继续，不会重复提交操作。"
        ><template #action><a-button @click="openRun(runId)">重新连接</a-button></template></a-alert
      >
    </div>
    <div v-if="state.stale" class="run-notice">
      <a-alert
        type="warning"
        show-icon
        message="审核内容已更新，需要重新阅读"
        description="已禁用旧版本的审批与回答，不会自动提交到新版本。"
        ><template #action><a-button @click="reread">查看最新版本</a-button></template></a-alert
      >
    </div>
    <div v-if="!modelReady" class="run-notice">
      <a-alert
        type="warning"
        show-icon
        message="模型配置尚未就绪"
        description="先保存有效配置，再回答、批准或重试。拒绝与恢复人工确认仍可使用。"
        ><template #action
          ><a-button @click="emit('navigate', 'settings')">检查配置</a-button></template
        ></a-alert
      >
    </div>
    <div v-if="['FAILED', 'PAUSED_LIMIT', 'BLOCKED'].includes(run.status)" class="run-notice">
      <section class="panel recovery-panel">
        <a-tag :color="statusColor(run.status)">{{ run.status }}</a-tag>
        <h2>
          {{
            run.status === 'PAUSED_LIMIT'
              ? '预算暂停，当前结果已保存'
              : run.status === 'BLOCKED'
                ? '先处理阻塞，再继续这一轮'
                : '先定位原因，再恢复同一轮运行'
          }}
        </h2>
        <p v-if="capabilityConflicts.length">
          当前运行与原始目标已保留。请在下方明确报名入口，已有审批不会自动批准新的范围。
        </p>
        <p v-else>{{ run.error || '请查看当前关卡与执行证据，确认问题后继续。' }}</p>
        <details v-if="capabilityConflicts.length && run.error" class="field-hint">
          <summary>查看恢复诊断</summary>
          <p>{{ run.error }}</p>
        </details>
        <div class="header-actions">
          <a-button
            v-if="!gate"
            type="primary"
            :loading="submitting"
            :disabled="!state.online || !modelReady"
            @click="retry"
            ><ReloadOutlined aria-hidden="true" />重试当前运行</a-button
          ><a-button v-else @click="route('conversation')">处理当前关卡</a-button
          ><a-button @click="emit('navigate', 'settings')">查看模型配置</a-button
          ><span class="muted">保留运行 ID 与已完成步骤</span>
        </div>
      </section>
    </div>
    <div v-if="view === 'conversation'" class="conversation-layout">
      <div class="conversation-main" @wheel="autoScroll = false">
        <div class="messages" aria-label="研发对话记录">
          <article
            v-for="(item, index) in state.messages"
            :key="item.message_id || item.id || index"
            class="chat-message"
            :data-testid="item.role === 'user' ? 'user-message' : 'assistant-message'"
            :data-validation="item.validation"
            :data-message-id="item.message_id"
            :class="item.role === 'user' ? 'user-message' : 'assistant-message'"
          >
            <div v-if="item.role !== 'user'" class="assistant-avatar">
              <ThunderboltOutlined aria-hidden="true" />
            </div>
            <div class="message-body">
              <div v-if="item.role !== 'user'" class="message-meta">
                <strong>研发助手</strong><span>{{ formatDate(item.created_at) }}</span
                ><a-tag v-if="item.validation === 'pending'" color="blue">生成中 · 待校验</a-tag
                ><a-tag v-if="item.validation === 'failed'" color="red">未通过校验</a-tag
                ><a-tag v-if="item.transport === 'non_streaming'">完整响应</a-tag>
              </div>
              <div class="message-text">
                {{
                  item.content ||
                  item.text ||
                  (item.validation === 'pending' ? '正在等待模型响应…' : '暂无可展示的摘要')
                }}<span
                  v-if="item.validation === 'pending'"
                  class="typing-cursor"
                  aria-label="响应生成中"
                />
              </div>
              <p v-if="item.validation === 'failed'" class="field-hint">
                此响应不能作为已批准方案，后续以有效关卡和验证证据为准。
              </p>
            </div>
          </article>
          <div v-if="!state.messages.length" class="quiet-empty">此轮尚未产生对话记录</div>
        </div>
        <div v-if="gate" class="conversation-gate">
          <section v-if="capabilityConflicts.length" class="panel gate-preview">
            <div class="section-top">
              <h2>先确认参与者入口与报名范围</h2>
              <a-tag color="orange">不能自动缩减目标</a-tag>
            </div>
            <p>你的原始目标已保留。智能推荐不会替你把参与者自行报名改成管理员录入。</p>
            <p v-for="(item, index) in capabilityConflicts" :key="index">
              {{ item.message }}
            </p>
            <h3 v-if="!hasScopeChoices">可选路径，需要你明确决定</h3>
            <ul v-if="!hasScopeChoices">
              <li v-for="item in capabilityAlternatives" :key="String(item)">{{ item }}</li>
            </ul>
            <p class="field-hint">下方答复只提交你填写的选择，不会自动采用任何替代范围。</p>
          </section>
          <div v-if="blocked.length && !capabilityConflicts.length" class="blocked-list">
            <a-alert type="warning" show-icon message="当前仍有需要解决的内容" />
            <ul>
              <li v-for="(item, index) in blocked" :key="index">{{ item }}</li>
            </ul>
          </div>
          <Questionnaire
            v-if="isQuestions"
            :key="gate.gate_id"
            :gate="gate"
            :disabled="!canSubmit || !modelReady"
            :busy="submitting"
            @submit="(text, answers) => decide('answer', text, answers)"
          />
          <section v-else class="panel gate-preview">
            <div class="section-top">
              <h2>{{ gateTitle }}</h2>
              <a-tag color="gold">等待你确认</a-tag>
            </div>
            <p>
              {{
                gate.data?.requirement?.summary ||
                gate.data?.plan?.title ||
                '当前阶段已产生可审核结果。阅读完整内容后，再决定是否继续。'
              }}
            </p>
            <p class="field-hint">审核版本 v{{ gate.version }} · {{ gate.stage }}</p>
            <a-button
              type="primary"
              size="large"
              @click="route(gate.stage === 'delivery' ? 'delivery' : 'review')"
              ><ArrowRightOutlined aria-hidden="true" />查看并审核当前版本</a-button
            >
          </section>
          <a-button
            v-if="isQuestions && canAct(run, 'reject')"
            danger
            type="text"
            class="question-reject"
            :disabled="!canSubmit"
            @click="reject"
            >拒绝并结束本轮</a-button
          >
        </div>
        <div v-else-if="['RUNNING', 'QUEUED'].includes(run.status)" class="working-note">
          <span class="pulse-dot" />
          <div>
            <strong>{{ run.status === 'QUEUED' ? '已进入队列' : '后台正在串行执行' }}</strong>
            <p>完成当前步骤后会自动更新。离开页面不会取消运行。</p>
          </div>
        </div>
        <div v-else-if="downloadable" class="info-callout">
          <CheckOutlined aria-hidden="true" />
          <div>
            <strong>{{ statusLabel(run.status) }}</strong>
            <p>
              {{
                run.status === 'SOURCE_READY'
                  ? '源码包已通过交付确认；这不代表已经完成运行环境验收。'
                  : '已通过运行级验收及交付确认，可查看报告与下载产物。'
              }}
            </p>
            <a-button type="primary" @click="route('delivery')">查看交付结果</a-button>
          </div>
        </div>
        <form
          v-if="gate && !isQuestions && (canAct(run, 'revise') || canAct(run, 'answer'))"
          class="chat-composer"
          @submit.prevent="send"
        >
          <a-textarea
            v-model:value="answer"
            aria-label="修改意见或补充需求"
            placeholder="继续补充需求，或描述想调整的地方…"
            :bordered="false"
            :auto-size="{ minRows: 1, maxRows: 8 }"
            :maxlength="20000"
            :disabled="!canSubmit || !modelReady"
            @keydown="keydown"
          /><a-button
            type="primary"
            html-type="submit"
            aria-label="提交补充内容"
            :loading="submitting"
            :disabled="!canSubmit || !modelReady || !answer.trim()"
            ><ArrowUpOutlined aria-hidden="true"
          /></a-button>
        </form>
        <section
          v-if="['RUNNING', 'QUEUED'].includes(run.status) || busyDraft"
          class="local-draft-section"
        >
          <div class="chat-composer busy-composer">
            <a-textarea
              v-model:value="busyDraft"
              aria-label="本轮补充草稿（仅保存在当前页面）"
              placeholder="也可以先记下想补充的内容…"
              :bordered="false"
              :auto-size="{ minRows: 2, maxRows: 8 }"
              :maxlength="20000"
            />
            <a-button type="primary" aria-label="当前步骤执行中，暂不可发送" disabled
              ><ArrowUpOutlined aria-hidden="true"
            /></a-button>
          </div>
          <div class="draft-explanation">
            <span>{{
              gate
                ? '草稿仍保留在本页。请将要提交的内容填入当前问题或修改意见，草稿不会自动发送。'
                : '当前步骤尚不能接收新回答。你可以先写草稿，出现可回答关卡后再提交。'
            }}</span
            ><a-button v-if="busyDraft" type="text" size="small" @click="busyDraft = ''"
              >清空草稿</a-button
            >
          </div>
        </section>
        <div ref="chatEnd" />
        <a-button v-if="!autoScroll" class="jump-latest" @click="jumpLatest">回到最新消息</a-button>
      </div>
      <aside class="progress-rail">
        <div class="section-top">
          <h3>研发进度</h3>
          <ApartmentOutlined aria-hidden="true" />
        </div>
        <ol class="rail-steps">
          <li
            v-for="(stage, index) in stages"
            :key="stage.key"
            :class="{ current: stageIndex === index, done: milestone(index) === 'done' }"
          >
            <span class="step-dot"
              ><CheckOutlined aria-hidden="true" v-if="milestone(index) === 'done'" /><template
                v-else
                >{{ index + 1 }}</template
              ></span
            >
            <div>
              <strong>{{ stage.label }}</strong>
              <p>{{ milestone(index) === 'pending' ? '等待前置阶段' : stage.description }}</p>
            </div>
          </li>
        </ol>
        <div class="rail-callout">
          <span>当前需要你</span
          ><strong>{{
            gate
              ? isQuestions
                ? '回答当前澄清问题'
                : '审核当前阶段产物'
              : ['FAILED', 'PAUSED_LIMIT'].includes(run.status)
                ? '检查原因后重试'
                : downloadable
                  ? '查看交付结果'
                  : '等待当前步骤结果'
          }}</strong>
          <p>{{ gate ? '收到回应后，流程才继续' : '进度依据真实事件更新' }}</p>
        </div>
        <div class="rail-callout compact">
          <strong>{{ run.auto_mode ? '智能推荐已开启' : '人工确认模式' }}</strong
          ><a-button
            type="link"
            :disabled="
              terminal(run) ||
              submitting ||
              !state.online ||
              (!run.auto_mode && (!modelReady || capabilityConflicts.length > 0))
            "
            @click="automation"
            >{{ run.auto_mode ? '恢复人工确认' : '了解并开启智能推荐' }}</a-button
          >
          <p v-if="capabilityConflicts.length">先明确答复范围，重复推荐不会改变模板能力。</p>
        </div>
        <div class="stream-status">
          <span class="status-dot" :class="state.stream === 'connected' ? 'online' : 'warning'" />{{
            state.stream === 'connected' ? '实时事件已连接' : '实时事件重连中'
          }}<small>最近更新 {{ formatDate(state.lastSync) }}</small>
        </div>
      </aside>
    </div>
    <div v-else-if="view === 'review'" class="page review-page">
      <header class="page-heading">
        <div>
          <div class="eyebrow">
            {{ gate?.stage === 'design' ? 'DESIGN REVIEW' : 'REQUIREMENTS REVIEW' }}
          </div>
          <h1>{{ gateTitle }}</h1>
          <p>审核当前内容与范围，确认后再继续下一阶段。</p>
        </div>
        <a-button @click="route('conversation')"
          ><MessageOutlined aria-hidden="true" />返回对话</a-button
        >
      </header>
      <div v-if="gate" class="review-layout">
        <article class="panel review-document">
          <div class="document-title">
            <div class="eyebrow">{{ gate.stage.toUpperCase() }}</div>
            <h2>
              {{ gate.data?.requirement?.summary || gate.data?.plan?.title || project?.title }}
            </h2>
            <p>版本 v{{ gate.version }} · AI 生成 / 人工审核</p>
          </div>
          <a-tabs v-if="gate.stage === 'design'" v-model:active-key="tab"
            ><a-tab-pane key="overview" tab="架构与模块" /><a-tab-pane
              key="interfaces"
              tab="接口与业务" /><a-tab-pane key="data" tab="数据模型" /><a-tab-pane
              key="tasks"
              tab="任务与覆盖" /></a-tabs
          ><Questionnaire
            v-if="isQuestions"
            :gate="gate"
            :disabled="!canSubmit || !modelReady"
            :busy="submitting"
            @submit="(text, answers) => decide('answer', text, answers)"
          /><DataDocument v-else :data="reviewData" />
        </article>
        <aside class="review-actions">
          <div class="panel approval-panel">
            <a-tag color="gold">等待{{ gate.stage === 'design' ? '设计' : '需求' }}确认</a-tag>
            <h2>这份{{ gate.stage === 'design' ? '方案' : '需求' }}符合预期吗？</h2>
            <p>确认后继续串行流程。需要修改时，将带着意见返回需求分析。</p>
            <a-alert
              v-if="blocked.length"
              type="warning"
              show-icon
              message="存在阻塞，当前不可批准"
            />
            <ul v-if="blocked.length">
              <li v-for="(item, index) in blocked" :key="index">{{ item }}</li>
            </ul>
            <a-checkbox
              v-if="canAct(run, 'approve')"
              v-model:checked="reviewed"
              :disabled="!canSubmit"
              >我已阅读并核对当前版本</a-checkbox
            ><a-textarea
              v-if="canAct(run, 'revise')"
              v-model:value="answer"
              aria-label="审核修改意见"
              placeholder="填写具体修改意见…"
              :auto-size="{ minRows: 3, maxRows: 10 }"
              :disabled="!canSubmit || !modelReady"
              :maxlength="20000"
            /><a-button
              v-if="gate.actions.includes('approve')"
              type="primary"
              size="large"
              block
              :loading="submitting"
              :disabled="!canSubmit || !modelReady || !canAct(run, 'approve') || !reviewed"
              @click="decide('approve')"
              >{{ gate.stage === 'design' ? '确认设计，开始生成' : '确认需求，生成计划' }}</a-button
            >
            <div class="approval-secondary">
              <a-button
                v-if="canAct(run, 'revise')"
                :loading="submitting"
                :disabled="!canSubmit || !modelReady || !answer.trim()"
                @click="decide('revise', answer.trim())"
                >提交修改意见</a-button
              ><a-button
                v-if="canAct(run, 'reject')"
                danger
                type="text"
                :disabled="!canSubmit"
                @click="reject"
                >拒绝</a-button
              >
            </div>
            <p class="field-hint">
              审核版本：v{{ gate.version }}<br />内容摘要：{{ gate.digest.slice(0, 16) }}…
            </p>
          </div>
          <div class="info-callout">
            <SafetyCertificateOutlined aria-hidden="true" />
            <p>提交时校验审批版本和内容摘要。内容变化后需刷新重审，避免误批旧方案。</p>
          </div>
        </aside>
      </div>
      <a-empty v-else description="当前没有等待审核的关卡"
        ><a-button @click="route('conversation')">返回对话</a-button></a-empty
      >
    </div>
    <div v-else-if="view === 'progress'" class="page progress-page">
      <header class="page-heading">
        <div>
          <div class="eyebrow">EXECUTION WORKSPACE</div>
          <h1>每个阶段，都有可追溯的结果</h1>
          <p>单个持久 Worker 串行执行 · 仅展示动作、结果与证据</p>
        </div>
      </header>
      <div class="stat-grid">
        <div class="panel stat">
          <span>当前状态</span><strong>{{ run.status }}</strong>
          <p>{{ stages[stageIndex].label }}</p>
        </div>
        <div class="panel stat">
          <span>已完成真实步骤</span><strong>{{ completeCount }} 个</strong>
          <p>依据已保存的执行事件</p>
        </div>
        <div class="panel stat">
          <span>当前审核</span><strong>{{ gate ? 'v' + gate.version : '无等待项' }}</strong>
          <p>{{ gate?.stage || '继续后台执行或查看结果' }}</p>
        </div>
        <div class="panel stat">
          <span>执行方式</span><strong>串行</strong>
          <p>不估算完成百分比或剩余时间</p>
        </div>
      </div>
      <div class="progress-columns">
        <section class="panel">
          <div class="panel-heading">
            <h2>阶段时间线</h2>
            <a-tag color="blue">串行工作流</a-tag>
          </div>
          <div class="milestones">
            <div v-for="(stage, index) in stages" :key="stage.key" class="milestone">
              <CheckOutlined
                aria-hidden="true"
                v-if="milestone(index) === 'done'"
                class="success-icon"
              /><ExclamationCircleOutlined
                aria-hidden="true"
                v-else-if="milestone(index) === 'failed'"
                class="error-icon"
              /><ClockCircleOutlined aria-hidden="true" v-else /><strong>{{ stage.label }}</strong
              ><span>{{ stage.steps.join(' / ') }}</span
              ><a-tag
                :color="
                  milestone(index) === 'done'
                    ? 'green'
                    : milestone(index) === 'failed'
                      ? 'red'
                      : milestone(index) === 'pending'
                        ? 'default'
                        : 'blue'
                "
                >{{
                  {
                    done: '已有完成记录',
                    failed: '失败',
                    pending: '待执行',
                    waiting: '等待确认',
                    running: '进行中',
                  }[milestone(index)]
                }}</a-tag
              >
            </div>
          </div>
        </section>
        <section class="panel phase-details">
          <h2>当前阶段详情</h2>
          <h3>{{ stages[stageIndex].label }}</h3>
          <p>{{ stages[stageIndex].description }}</p>
          <p class="muted">可查看的执行证据</p>
          <a-button
            v-for="name in Object.keys(state.report)"
            :key="name"
            type="link"
            @click="showDetails = true"
            ><FileTextOutlined aria-hidden="true" />{{ name }}</a-button
          >
          <p v-if="!Object.keys(state.report).length">尚未产生报告，完成步骤后会更新。</p>
        </section>
      </div>
      <section class="panel event-panel">
        <div class="panel-heading">
          <h2>事件记录</h2>
          <span class="muted">SSE 实时 · 游标 {{ state.cursor }}</span>
        </div>
        <div v-if="eventsReversed.length" class="event-list">
          <div v-for="event in eventsReversed" :key="event.id" class="event-row">
            <time>{{ formatDate(event.created_at) }}</time
            ><span class="event-kind">{{ event.kind }}</span>
            <p>{{ eventSummary(event) }}</p>
          </div>
        </div>
        <a-empty v-else description="正在等待第一个执行事件" />
      </section>
      <p class="page-footnote">
        事件可用于回放实际步骤，不展示模型内部思维。失败或尚未执行的步骤不会计入完成记录。
      </p>
    </div>
    <div v-else-if="view === 'delivery'" class="page delivery-page">
      <header class="page-heading">
        <div>
          <div class="eyebrow">DELIVERY REVIEW</div>
          <h1>先看验证证据，再确认交付</h1>
          <p>当前状态 {{ run.status }} · {{ shortId(run.id) }}</p>
        </div>
        <a-tag :color="statusColor(run.status)">{{ statusLabel(run.status) }}</a-tag>
      </header>
      <a-alert
        :type="run.status === 'READY' ? 'success' : 'info'"
        show-icon
        :message="
          run.status === 'READY'
            ? '运行级验收与交付确认已完成'
            : run.status === 'SOURCE_READY'
              ? '源码级交付已确认，运行验收尚未证明'
              : gate?.stage === 'delivery'
                ? '验证结果已保存，等待你的交付确认'
                : '本轮尚未进入交付确认'
        "
        :description="
          downloadable
            ? '可下载已经过哈希校验的交付包。'
            : '批准前交付下载保持锁定。交付不等于自动部署或数据迁移。'
        "
      />
      <div class="delivery-grid">
        <section class="panel">
          <div class="panel-heading">
            <h2>交付产物</h2>
            <a-tag :color="downloadable ? 'green' : 'gold'">{{
              downloadable ? '可下载' : '下载锁定'
            }}</a-tag>
          </div>
          <div class="panel-content">
            <template v-if="Object.keys(delivery).length"
              ><DataDocument :data="delivery" /></template
            ><a-empty v-else description="尚无交付产物" /><a-button
              type="primary"
              size="large"
              :loading="submitting"
              :disabled="!downloadable || !state.online"
              @click="download"
              ><DownloadOutlined aria-hidden="true" />下载完整交付包</a-button
            >
          </div>
        </section>
        <section class="panel">
          <div class="panel-heading">
            <h2>验证证据</h2>
            <a-tag>后端原始结果</a-tag>
          </div>
          <div class="panel-content">
            <DataDocument v-if="evidence" :data="evidence" /><a-empty
              v-else
              description="尚无验证报告"
            /><a-button
              v-if="Object.keys(state.report).length"
              type="link"
              @click="showDetails = true"
              >查看全部报告</a-button
            >
            <p class="field-hint">未执行与失败项不计入通过数量。</p>
          </div>
        </section>
      </div>
      <section class="panel definition-panel">
        <h2>本次交付的完成定义</h2>
        <div class="definition-grid">
          <div class="definition runtime">
            <h3>READY · 运行级交付</h3>
            <p>运行验收通过，批准交付后可下载</p>
          </div>
          <div class="definition">
            <h3>SOURCE_READY · 源码级交付</h3>
            <p>只证明源码包已交付，不代表已经可运行</p>
          </div>
        </div>
      </section>
      <section v-if="gate?.stage === 'delivery'" class="info-callout delivery-approval">
        <div>
          <h2>你确认这份交付结果吗？</h2>
          <p>批准时校对版本与交付内容摘要；内容变化会要求重新审核。</p>
          <a-checkbox v-model:checked="reviewed" :disabled="!canSubmit"
            >我已阅读本次验收证据与交付等级</a-checkbox
          >
        </div>
        <div class="header-actions">
          <a-button :disabled="!canSubmit" @click="reject">拒绝交付</a-button
          ><a-button
            type="primary"
            size="large"
            :loading="submitting"
            :disabled="!canSubmit || !modelReady || !reviewed || !canAct(run, 'approve')"
            @click="decide('approve')"
            >确认交付并开放下载</a-button
          >
        </div>
      </section>
    </div>
    <a-drawer v-model:open="showDetails" title="项目资料与执行证据" width="min(760px, 100vw)"
      ><a-tabs
        ><a-tab-pane key="report" tab="报告"
          ><a-collapse v-if="Object.keys(state.report).length"
            ><a-collapse-panel v-for="(report, name) in state.report" :key="name" :header="name"
              ><DataDocument :data="report" /></a-collapse-panel></a-collapse
          ><a-empty v-else description="当前尚无报告" /></a-tab-pane
        ><a-tab-pane key="models" tab="实际模型记录"
          ><div v-for="(record, index) in state.usedModels" :key="index" class="model-record">
            <DataDocument :data="record" />
          </div>
          <a-empty v-if="!state.usedModels.length" description="尚未产生模型调用记录" /></a-tab-pane
        ><a-tab-pane key="meta" tab="运行信息"
          ><a-descriptions bordered :column="1"
            ><a-descriptions-item label="项目">{{ project?.title }}</a-descriptions-item
            ><a-descriptions-item label="运行 ID">{{ run.id }}</a-descriptions-item
            ><a-descriptions-item label="状态">{{ run.status }}</a-descriptions-item
            ><a-descriptions-item label="模板">{{ run.template }}</a-descriptions-item
            ><a-descriptions-item label="自动决策">{{
              run.auto_mode ? '已授权' : '人工确认'
            }}</a-descriptions-item></a-descriptions
          ><a-button class="question-text" @click="emit('navigate', 'project/' + run.project_id)"
            >查看此项目的所有运行</a-button
          ></a-tab-pane
        ></a-tabs
      ></a-drawer
    >
  </div>
</template>
