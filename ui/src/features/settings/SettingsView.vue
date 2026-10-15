<script setup lang="ts">
import { computed, onBeforeUnmount, reactive, ref, watch } from 'vue'
import { CheckOutlined, SafetyCertificateOutlined, ReloadOutlined } from '@ant-design/icons-vue'
import { Modal } from 'ant-design-vue'
import { api, ApiError, errorText } from '../../api'
import { state, refreshLists, sessionIdentity, isSessionActive } from '../../state'
const sections = [
  { id: 'default', name: '默认连接', hint: '默认所有阶段' },
  { id: 'requirements', name: '需求阶段', hint: '按需覆盖默认连接' },
  { id: 'planning', name: '计划阶段', hint: '按需覆盖默认连接' },
  { id: 'coding', name: '代码阶段', hint: '按需覆盖默认连接' },
  { id: 'review', name: '模型复核', hint: '可选，默认关闭' },
]
const active = ref('default'),
  loading = ref(false),
  testing = ref(false),
  discovering = ref(false),
  confirmingTest = ref(false),
  notice = ref(''),
  error = ref(''),
  conflict = ref(false),
  keyAction = ref('keep')
const form = reactive({
  base_url: '',
  model: '',
  provider: 'auto' as string | null,
  output_mode: 'auto' as string | null,
  max_output_tokens: null as number | null,
  api_key: '',
  model_review: false,
})
const baseline = ref('')
const revision = ref('')
interface ConnectionResult {
  ok: boolean
  stage: string
  revision: string
  message: string
  phase: string
  code: string
  trace_id: string
  retryable: boolean
  attempts: number
  elapsed_ms: number
}
const connectionResult = ref<ConnectionResult | null>(null)
const busy = computed(
  () => loading.value || testing.value || confirmingTest.value || discovering.value,
)
const editable = computed(() => !!state.settings && !!revision.value && !busy.value)
const modelOptions = ref<{ value: string }[]>([])
const discoveryNotice = ref('')
let discoveryController: AbortController | null = null
let mounted = true
let testController: AbortController | null = null
let testConfirmation: ReturnType<typeof Modal.confirm> | null = null
let refreshConfirmation: ReturnType<typeof Modal.confirm> | null = null
function load() {
  const config = state.settings
  if (!config) return
  const profile = active.value === 'default' ? config.default : config.stages?.[active.value]
  Object.assign(form, {
    base_url: profile?.base_url || '',
    model: profile?.model || '',
    provider: profile?.provider ?? (active.value === 'default' ? 'auto' : null),
    output_mode: profile?.output_mode ?? (active.value === 'default' ? 'auto' : null),
    max_output_tokens: profile?.max_output_tokens ?? null,
    api_key: '',
    model_review: !!config.model_review,
  })
  keyAction.value = 'keep'
  revision.value = config.revision
  baseline.value = JSON.stringify(form)
  conflict.value = false
}
const dirty = computed(() => baseline.value !== JSON.stringify(form) || keyAction.value !== 'keep')
baseline.value = JSON.stringify(form)
watch(
  () => state.settings,
  () => {
    if (!dirty.value) load()
    else if (!revision.value) {
      conflict.value = true
      error.value = '配置读取较晚，已保留你的输入。请读取最新配置后重新核对，避免覆盖已有配置。'
    }
  },
  { immediate: true },
)
const original = computed(() =>
  active.value === 'default' ? state.settings?.default : state.settings?.stages?.[active.value],
)
const changedUrl = computed(
  () =>
    form.base_url.trim().replace(/\/$/, '') !== (original.value?.base_url || '').replace(/\/$/, ''),
)
const newUrlNeedsKey = computed(() => changedUrl.value && !!form.base_url.trim())
const missingNewUrlKey = computed(
  () => newUrlNeedsKey.value && (keyAction.value !== 'replace' || !form.api_key.trim()),
)
const validation = computed(() =>
  state.settings?.validation?.find((row: any) => row.stage === active.value),
)
const keyConfigured = computed(() => original.value?.api_key === 'configured')
const effective = computed(() =>
  active.value === 'default' ? original.value : original.value?.effective,
)
const canTest = computed(
  () =>
    !!revision.value &&
    revision.value === state.settings?.revision &&
    !dirty.value &&
    !conflict.value &&
    !loading.value &&
    !testing.value &&
    !discovering.value &&
    state.online &&
    !!effective.value?.base_url &&
    !!effective.value?.model &&
    effective.value?.api_key === 'configured',
)
const testBlockReason = computed(() => {
  if (!state.settings || !revision.value) return '尚未读取配置，请读取最新配置后再测试'
  if (!state.online) return '网络离线，请恢复连接后再测试'
  if (conflict.value || revision.value !== state.settings.revision)
    return '配置版本已变化，请读取最新配置后再测试'
  if (dirty.value) return '请先保存修改，再测试已保存的有效连接'
  if (
    !effective.value?.base_url ||
    !effective.value?.model ||
    effective.value?.api_key !== 'configured'
  )
    return '请先填写并保存服务地址、模型和 API Key，再测试连接'
  return ''
})
const currentResult = computed(() =>
  !dirty.value &&
  connectionResult.value?.revision === revision.value &&
  connectionResult.value?.revision === state.settings?.revision &&
  connectionResult.value?.stage === active.value
    ? connectionResult.value
    : null,
)
const saveBlockReason = computed(() => {
  if (!state.settings || !revision.value) return '尚未读取配置，请点击读取最新配置后再编辑'
  if (!state.online) return '网络离线，请恢复连接后保存'
  if (conflict.value || revision.value !== state.settings.revision)
    return '配置版本已变化，请读取最新配置后重新核对'
  if (missingNewUrlKey.value) return '服务地址已改变，请选择替换并填写新地址专用的 API Key'
  if (keyAction.value === 'replace' && !form.api_key.trim()) return '请填写新的 API Key'
  if (!dirty.value) return '没有需要保存的修改'
  return ''
})
const canSave = computed(() => !saveBlockReason.value)
const canDiscover = computed(
  () =>
    editable.value &&
    state.online &&
    !conflict.value &&
    revision.value === state.settings?.revision &&
    !!(form.base_url.trim() || (active.value !== 'default' && state.settings?.default?.base_url)) &&
    (!newUrlNeedsKey.value || (keyAction.value === 'replace' && !!form.api_key.trim())) &&
    keyAction.value !== 'clear' &&
    (keyAction.value === 'replace'
      ? !!form.api_key.trim()
      : effective.value?.api_key === 'configured'),
)
function profilePatch() {
  const profile: any = {
    base_url: form.base_url.trim(),
    model: form.model.trim(),
    provider: form.provider,
    output_mode: form.output_mode,
    max_output_tokens: form.max_output_tokens,
  }
  if (keyAction.value === 'replace') profile.api_key = form.api_key.trim()
  if (keyAction.value === 'clear') profile.api_key = ''
  return profile
}
watch(
  [
    active,
    () => form.base_url,
    () => form.api_key,
    keyAction,
    revision,
    () => state.settings?.revision,
  ],
  () => {
    modelOptions.value = []
    discoveryNotice.value = ''
  },
)
async function discoverModels() {
  if (!canDiscover.value) return
  const generation = sessionIdentity(),
    targetRevision = revision.value
  discovering.value = true
  error.value = ''
  discoveryNotice.value = ''
  modelOptions.value = []
  discoveryController = new AbortController()
  try {
    const result = await api<{ ok: boolean; models: string[]; message: string }>(
      '/settings/models/discover',
      {
        method: 'POST',
        body: { stage: active.value, expected_revision: revision.value, profile: profilePatch() },
        signal: discoveryController.signal,
      },
    )
    if (!mounted || !isSessionActive(generation)) return
    if (targetRevision !== state.settings?.revision) {
      conflict.value = true
      return
    }
    modelOptions.value = result.ok ? result.models.map((value) => ({ value })) : []
    discoveryNotice.value = result.message + '；仍可手动填写模型 ID。'
  } catch (e) {
    if (!mounted || !isSessionActive(generation)) return
    error.value = errorText(e) + '；仍可手动填写模型 ID。'
    if (e instanceof ApiError && e.status === 409) conflict.value = true
  } finally {
    discovering.value = false
    discoveryController = null
  }
}
function requestRefresh() {
  if (busy.value || refreshConfirmation) return
  const generation = sessionIdentity()
  if (dirty.value)
    refreshConfirmation = Modal.confirm({
      title: '读取最新配置并放弃未保存的修改？',
      content: '新输入的 API Key 也会从页面内存中清除。',
      okText: '读取最新配置',
      cancelText: '继续编辑',
      onCancel: () => {
        refreshConfirmation = null
      },
      onOk: () => {
        refreshConfirmation = null
        if (mounted && isSessionActive(generation)) return refresh()
      },
    })
  else void refresh()
}

function select(id: string) {
  if (busy.value || id === active.value) return
  const go = () => {
    active.value = id
    notice.value = ''
    error.value = ''
    load()
  }
  if (dirty.value)
    Modal.confirm({
      title: '放弃这页未保存的修改？',
      content: '输入的 API Key 也会从页面内存中清除。',
      okText: '放弃修改',
      cancelText: '继续编辑',
      onOk: go,
    })
  else go()
}
async function refresh() {
  if (busy.value) return
  error.value = ''
  notice.value = ''
  const generation = sessionIdentity()
  loading.value = true
  try {
    const settings = await api('/settings/models')
    if (!isSessionActive(generation)) return
    state.settings = settings
    load()
    notice.value = '已读取最新配置，请重新核对后保存'
  } catch (e) {
    if (!isSessionActive(generation)) return
    error.value = errorText(e)
  } finally {
    loading.value = false
  }
}
async function save() {
  if (busy.value || !canSave.value || !state.online) return
  const generation = sessionIdentity()
  loading.value = true
  error.value = ''
  notice.value = ''
  const profile = profilePatch()
  const body: any = {
    expected_revision: revision.value,
    ...(active.value === 'default'
      ? { default: profile }
      : { stages: { [active.value]: profile } }),
  }
  if (active.value === 'review') body.model_review = form.model_review
  try {
    const settings = await api('/settings/models', { method: 'PATCH', body })
    if (!isSessionActive(generation)) return
    state.settings = settings
    load()
    notice.value = '配置已保存 · 仅完成格式校验 · 未测试连接'
    await refreshLists()
  } catch (e) {
    if (!isSessionActive(generation)) return
    error.value = errorText(e)
    if (e instanceof ApiError && e.status === 409) conflict.value = true
  } finally {
    loading.value = false
    form.api_key = ''
  }
}
function confirmConnectionTest() {
  if (!canTest.value || confirmingTest.value) return
  const targetStage = active.value,
    targetRevision = revision.value,
    generation = sessionIdentity(),
    tokenLimit = Math.min(effective.value.max_output_tokens || 128, 128)
  confirmingTest.value = true
  testConfirmation = Modal.confirm({
    title: '发起一次真实模型连接测试？',
    content: `将使用已保存版本 ${targetRevision.slice(0, 8)} 的 ${effective.value.model}（${effective.value.base_url}）发送固定测试内容，最多请求 ${tokenLimit} 个输出 token，可能按服务商价格计费。推理模型可能因测试输出上限被截断。不会发送项目内容，也不会自动重试。`,
    okText: '确认并测试',
    cancelText: '取消',
    onCancel: () => {
      confirmingTest.value = false
      testConfirmation = null
    },
    onOk: async () => {
      confirmingTest.value = false
      if (
        !mounted ||
        !isSessionActive(generation) ||
        !canTest.value ||
        active.value !== targetStage ||
        revision.value !== targetRevision
      ) {
        testConfirmation = null
        return
      }
      testing.value = true
      connectionResult.value = null
      error.value = ''
      notice.value = ''
      testController = new AbortController()
      try {
        const result = await api<ConnectionResult>('/settings/models/test', {
          method: 'POST',
          body: {
            stage: targetStage,
            expected_revision: targetRevision,
            request_id: crypto.randomUUID(),
            confirm_cost: true,
          },
          signal: testController.signal,
        })
        if (!mounted || !isSessionActive(generation)) return
        connectionResult.value = result
      } catch (e) {
        if (!mounted || !isSessionActive(generation)) return
        error.value = errorText(e) + '；未自动重试。若请求已发出，服务商仍可能计费。'
        if (e instanceof ApiError && e.status === 409) conflict.value = true
      } finally {
        testing.value = false
        testController = null
        testConfirmation = null
      }
    },
  })
}
function beforeUnload(event: BeforeUnloadEvent) {
  if (dirty.value) {
    event.preventDefault()
    event.returnValue = ''
  }
}
window.addEventListener('beforeunload', beforeUnload)
onBeforeUnmount(() => {
  mounted = false
  testController?.abort()
  discoveryController?.abort()
  testConfirmation?.destroy()
  refreshConfirmation?.destroy()
  window.removeEventListener('beforeunload', beforeUnload)
  form.api_key = ''
})
defineExpose({ dirty })
</script>
<template>
  <div class="page settings-page">
    <header class="page-heading">
      <div>
        <div class="eyebrow">MODEL CONFIGURATION</div>
        <h1>模型与服务，一处配置</h1>
        <p>默认连接 + 需求 / 计划 / 编码 / 复核阶段覆盖</p>
      </div>
      <a-tag :color="currentResult?.ok ? 'green' : 'gold'">{{
        currentResult?.ok
          ? '当前连接测试通过'
          : state.settings?.ready
            ? '格式有效 · 未验证当前连接'
            : '需要配置'
      }}</a-tag>
    </header>
    <div class="settings-layout">
      <aside class="settings-navigation">
        <div class="panel settings-tabs" role="tablist" aria-label="模型阶段">
          <button
            v-for="section in sections"
            :key="section.id"
            role="tab"
            :aria-selected="active === section.id"
            :class="{ active: active === section.id }"
            :disabled="!editable"
            @click="select(section.id)"
          >
            <strong>{{ section.name }}</strong
            ><small>{{ section.hint }}</small>
          </button>
        </div>
        <div class="security-note">
          <h3><SafetyCertificateOutlined aria-hidden="true" /> 安全约束</h3>
          <p>密钥不出现在聊天、日志或交付包中。后端只返回密钥状态，不回传密钥原文。</p>
          <p>已保存的密钥只能替换，不能查看。</p>
        </div>
      </aside>
      <div class="settings-main">
        <form class="panel settings-form" @submit.prevent="save">
          <div class="section-top">
            <div>
              <h2>{{ sections.find((s) => s.id === active)?.name }}模型连接</h2>
              <p>配置格式有效 ≠ 服务连接成功</p>
            </div>
            <a-tag v-if="active !== 'default'">{{
              original?.key_source === 'default'
                ? '继承默认密钥'
                : original?.key_source === 'override'
                  ? '独立密钥'
                  : '未配置密钥'
            }}</a-tag>
          </div>
          <a-alert
            v-if="state.settings?.source"
            type="info"
            show-icon
            :message="
              state.settings.source === 'saved'
                ? '配置来源：本机已保存配置。它优先于 .env；修改 .env 不会自动覆盖，请在此页编辑并保存。'
                : '配置来源：服务启动环境（含 .env）。修改 .env 后需重启服务；在此页保存后将优先使用本机已保存配置。'
            "
          />
          <a-alert
            v-if="active !== 'default'"
            type="info"
            show-icon
            message="留空的地址和模型将继承默认连接；不同地址必须使用该地址的专用密钥"
          />
          <div class="form-grid">
            <div>
              <label class="form-label" for="model-provider">服务提供商</label
              ><a-select
                id="model-provider"
                v-model:value="form.provider"
                :disabled="!editable"
                :options="[
                  ...(active !== 'default' ? [{ value: null, label: '继承默认' }] : []),
                  { value: 'auto', label: '自动识别' },
                  { value: 'compatible', label: 'OpenAI 兼容服务' },
                  { value: 'openai', label: 'OpenAI' },
                  { value: 'deepseek', label: 'DeepSeek' },
                ]"
              />
            </div>
            <div>
              <label class="form-label" for="model-output">输出协议</label
              ><a-select
                id="model-output"
                v-model:value="form.output_mode"
                :disabled="!editable"
                :options="[
                  ...(active !== 'default' ? [{ value: null, label: '继承默认' }] : []),
                  { value: 'auto', label: '自动' },
                  { value: 'json_object', label: 'JSON 对象' },
                ]"
              />
            </div>
            <div class="full-width">
              <label class="form-label" for="model-url"
                >API Base URL {{ active === 'default' ? '*' : '' }}</label
              ><a-input
                id="model-url"
                v-model:value="form.base_url"
                :disabled="!editable"
                placeholder="https://api.example.com/v1"
                autocomplete="off"
                :maxlength="2048"
              />
              <p class="field-hint">
                仅填 API 根地址；不包含 /chat/completions、账号密码、查询参数或片段。
              </p>
              <a-alert
                v-if="missingNewUrlKey"
                class="compact-alert"
                type="warning"
                show-icon
                message="服务地址已改变，请选择替换并填写新地址专用的 API Key"
              />
            </div>
            <div>
              <label class="form-label" for="model-name"
                >模型名称 {{ active === 'default' ? '*' : '' }}</label
              ><a-auto-complete
                id="model-name"
                v-model:value="form.model"
                :disabled="!editable"
                :options="modelOptions"
                :filter-option="
                  (input: string, option: any) =>
                    option.value.toLowerCase().includes(input.toLowerCase())
                "
                placeholder="查询选择或手动填写模型 ID"
                autocomplete="off"
                :maxlength="256"
              />
              <a-button
                aria-label="查询模型列表"
                :loading="discovering"
                :disabled="!canDiscover"
                @click="discoverModels"
                >查询模型列表</a-button
              >
              <p class="field-hint">
                查询通过后端读取该地址的 /models，不发起推理，也不会保存配置。可直接手填模型 ID。
              </p>
              <p v-if="discoveryNotice" role="status" class="field-hint">{{ discoveryNotice }}</p>
            </div>
            <div>
              <div class="label-row">
                <label class="form-label" for="key-action">API Key</label
                ><a-tag :color="keyConfigured ? 'green' : 'default'">{{
                  keyAction === 'replace' && form.api_key
                    ? '新密钥待保存'
                    : keyConfigured
                      ? '已配置'
                      : '未配置'
                }}</a-tag>
              </div>
              <a-select
                id="key-action"
                v-model:value="keyAction"
                :disabled="!editable"
                :options="[
                  { value: 'keep', label: '保留现有密钥 / 继承默认' },
                  { value: 'replace', label: '替换为新密钥' },
                  { value: 'clear', label: '清除此处密钥' },
                ]"
              /><a-input-password
                v-if="keyAction === 'replace'"
                id="model-key"
                v-model:value="form.api_key"
                aria-label="新 API Key"
                :disabled="!editable"
                placeholder="输入此服务的专用 API Key"
                autocomplete="new-password"
                :visibility-toggle="false"
                class="question-text"
              />
              <p class="field-hint">已保存密钥不会填回输入框。</p>
            </div>
            <div>
              <label class="form-label" for="model-max-tokens">最大输出 Token（可选）</label
              ><a-input-number
                id="model-max-tokens"
                v-model:value="form.max_output_tokens"
                :disabled="!editable"
                :min="1"
                :max="393216"
                :precision="0"
                placeholder="使用平台协议默认上限"
              />
            </div>
            <div v-if="active === 'review'" class="review-toggle">
              <a-switch v-model:checked="form.model_review" :disabled="!editable" /><span
                >启用模型复核</span
              >
              <p class="field-hint">复核覆盖项存在时也会启用。关闭需同时清除覆盖配置。</p>
            </div>
          </div>
          <div class="settings-footnote">
            <SafetyCertificateOutlined aria-hidden="true" />
            <p>
              更换服务地址时，必须为新地址重新填写专用密钥。不会把旧服务的密钥自动发送给新地址。
            </p>
          </div>
          <a-alert v-if="error" type="error" show-icon :message="error" />
          <a-alert v-if="notice" type="success" show-icon :message="notice" />
          <a-alert
            v-if="!notice && !error && !currentResult && !testing"
            :type="dirty ? 'warning' : 'info'"
            :message="dirty ? '配置有未保存的修改' : '保存状态与连接状态分开显示 · 未测试连接'"
          />
          <a-alert
            v-if="testing"
            type="info"
            show-icon
            message="正在请求真实模型响应，请等待；不会自动重试"
          />
          <a-alert
            v-if="currentResult"
            :type="currentResult.ok ? 'success' : 'error'"
            show-icon
            :message="currentResult.message"
          >
            <template #description>
              <p>
                阶段：{{ currentResult.phase }} · 代码：{{ currentResult.code }} · 耗时：{{
                  currentResult.elapsed_ms
                }}
                ms
              </p>
              <p>追踪编号：{{ currentResult.trace_id }} · 请求次数：{{ currentResult.attempts }}</p>
              <p v-if="!currentResult.ok">
                {{
                  currentResult.retryable
                    ? '检查原因后可手动重试，每次重试可能计费。'
                    : '请先修正配置或响应协议，再重新测试。'
                }}
              </p>
            </template>
          </a-alert>
          <a-alert
            v-if="validation && !validation.valid && !dirty"
            type="warning"
            class="compact-alert"
            :message="validation.error"
          />
          <p v-if="saveBlockReason" role="status" class="field-hint">{{ saveBlockReason }}</p>
          <div class="form-actions">
            <span class="muted">{{
              dirty ? '未保存' : '当前配置版本 ' + revision.slice(0, 8)
            }}</span
            ><a-button
              aria-label="读取最新配置"
              :loading="loading"
              :disabled="busy || !state.online"
              @click="requestRefresh"
              ><ReloadOutlined aria-hidden="true" />读取最新配置</a-button
            ><a-button
              :title="testBlockReason || '发起一次真实模型调用，可能产生费用；确认后才开始'"
              aria-label="测试连接"
              :loading="testing"
              :disabled="!canTest || confirmingTest"
              @click="confirmConnectionTest"
              >测试连接</a-button
            ><a-button
              type="primary"
              html-type="submit"
              aria-label="保存配置"
              size="large"
              :loading="loading"
              :disabled="!canSave || busy"
              :title="saveBlockReason || '保存当前配置'"
              ><CheckOutlined aria-hidden="true" />保存配置</a-button
            >
          </div>
          <p v-if="testBlockReason" role="status" class="field-hint">{{ testBlockReason }}</p>
          <p class="field-hint">
            保存仅校验格式，不产生模型费用。测试连接须单独确认，只测试当前页已保存的有效连接。保存后下一次调用使用新配置，进行中的调用保持原配置。
          </p>
        </form>
        <div class="info-callout">
          <SafetyCertificateOutlined aria-hidden="true" />
          <div>
            <strong>本地保存，按阶段生效</strong>
            <p>仅本机后端持有模型密钥。访问令牌仅保留在当前页面内存，刷新页面后需要重新连接。</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
