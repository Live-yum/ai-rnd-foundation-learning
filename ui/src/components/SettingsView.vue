<script setup lang="ts">
import { computed, onBeforeUnmount, reactive, ref } from 'vue'
import { CheckOutlined, SafetyCertificateOutlined, ReloadOutlined } from '@ant-design/icons-vue'
import { Modal } from 'ant-design-vue'
import { api, ApiError, errorText } from '../api'
import { state, refreshLists, sessionIdentity, isSessionActive } from '../state'
const sections = [
  { id: 'default', name: '默认连接', hint: '默认所有阶段' },
  { id: 'requirements', name: '需求阶段', hint: '按需覆盖默认连接' },
  { id: 'planning', name: '计划阶段', hint: '按需覆盖默认连接' },
  { id: 'coding', name: '代码阶段', hint: '按需覆盖默认连接' },
  { id: 'review', name: '模型复核', hint: '可选，默认关闭' },
]
const active = ref('default'),
  loading = ref(false),
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
let revision = ''
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
  revision = config.revision
  baseline.value = JSON.stringify(form)
  conflict.value = false
}
load()
const dirty = computed(() => baseline.value !== JSON.stringify(form) || keyAction.value !== 'keep')
const original = computed(() =>
  active.value === 'default' ? state.settings?.default : state.settings?.stages?.[active.value],
)
const changedUrl = computed(
  () =>
    form.base_url.trim().replace(/\/$/, '') !== (original.value?.base_url || '').replace(/\/$/, ''),
)
const newUrlNeedsKey = computed(() => changedUrl.value && !!form.base_url.trim())
const validation = computed(() =>
  state.settings?.validation?.find((row: any) => row.stage === active.value),
)
const keyConfigured = computed(() => original.value?.api_key === 'configured')
const canSave = computed(
  () =>
    !!state.settings &&
    !!revision &&
    dirty.value &&
    !conflict.value &&
    (!newUrlNeedsKey.value || (keyAction.value === 'replace' && !!form.api_key.trim())) &&
    (keyAction.value !== 'replace' || !!form.api_key.trim()),
)
function select(id: string) {
  if (id === active.value) return
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
  if (loading.value || !canSave.value || !state.online) return
  const generation = sessionIdentity()
  loading.value = true
  error.value = ''
  notice.value = ''
  const profile: any = {
    base_url: form.base_url.trim(),
    model: form.model.trim(),
    provider: form.provider,
    output_mode: form.output_mode,
    max_output_tokens: form.max_output_tokens,
  }
  if (keyAction.value === 'replace') profile.api_key = form.api_key.trim()
  if (keyAction.value === 'clear') profile.api_key = ''
  const body: any = {
    expected_revision: revision,
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
function beforeUnload(event: BeforeUnloadEvent) {
  if (dirty.value) {
    event.preventDefault()
    event.returnValue = ''
  }
}
window.addEventListener('beforeunload', beforeUnload)
onBeforeUnmount(() => {
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
      <a-tag :color="state.settings?.ready ? 'green' : 'gold'">{{
        state.settings?.ready ? '格式有效 · 未测试连接' : '需要配置'
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
                :disabled="loading"
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
                :disabled="loading"
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
                :disabled="loading"
                placeholder="https://api.example.com/v1"
                autocomplete="off"
                :maxlength="2048"
              />
              <p class="field-hint">
                仅填 API 根地址；不包含 /chat/completions、账号密码、查询参数或片段。
              </p>
              <a-alert
                v-if="newUrlNeedsKey"
                class="compact-alert"
                type="warning"
                show-icon
                message="服务地址已改变，请选择替换并填写新地址专用的 API Key"
              />
            </div>
            <div>
              <label class="form-label" for="model-name"
                >模型名称 {{ active === 'default' ? '*' : '' }}</label
              ><a-input
                id="model-name"
                v-model:value="form.model"
                :disabled="loading"
                placeholder="提供商的实际模型 ID"
                autocomplete="off"
                :maxlength="256"
              />
              <p class="field-hint">请按提供商的实际模型 ID 填写。</p>
            </div>
            <div>
              <div class="label-row">
                <label class="form-label" for="key-action">API Key</label
                ><a-tag :color="keyConfigured ? 'green' : 'default'">{{
                  keyConfigured ? '已配置' : '未配置'
                }}</a-tag>
              </div>
              <a-select
                id="key-action"
                v-model:value="keyAction"
                :disabled="loading"
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
                :disabled="loading"
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
                :disabled="loading"
                :min="1"
                :max="393216"
                :precision="0"
                placeholder="使用平台协议默认上限"
              />
            </div>
            <div v-if="active === 'review'" class="review-toggle">
              <a-switch v-model:checked="form.model_review" :disabled="loading" /><span
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
            v-if="!notice && !error"
            :type="dirty ? 'warning' : 'info'"
            :message="dirty ? '配置有未保存的修改' : '保存状态与连接状态分开显示 · 未测试连接'"
          />
          <a-alert
            v-if="validation && !validation.valid && !dirty"
            type="warning"
            class="compact-alert"
            :message="validation.error"
          />
          <div class="form-actions">
            <span class="muted">{{
              dirty ? '未保存' : '当前配置版本 ' + revision.slice(0, 8)
            }}</span
            ><a-button v-if="conflict" :loading="loading" @click="refresh"
              ><ReloadOutlined aria-hidden="true" />读取最新配置</a-button
            ><a-tooltip title="当前服务没有连接测试接口；保存不会发起模型请求或产生模型费用"
              ><a-button disabled>连接测试未开放</a-button></a-tooltip
            ><a-button
              type="primary"
              html-type="submit"
              size="large"
              :loading="loading"
              :disabled="!canSave || !state.online"
              ><CheckOutlined aria-hidden="true" />保存配置</a-button
            >
          </div>
          <p class="field-hint">
            保存后，下次模型调用使用新配置；已经执行中的调用保持原配置。此页面不会发起真实模型调用。
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
