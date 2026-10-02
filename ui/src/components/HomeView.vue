<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, ref, watch } from 'vue'
import {
  ArrowUpOutlined,
  MessageOutlined,
  CodeOutlined,
  FileTextOutlined,
  ThunderboltOutlined,
  ArrowRightOutlined,
  PlusOutlined,
  SafetyCertificateOutlined,
} from '@ant-design/icons-vue'
import { state, mutationKey, clearMutationKey, refreshLists, reportError } from '../state'
import { api } from '../api'
import { formatDate, statusColor, statusLabel } from '../presentation'
const props = defineProps<{ projectId?: string }>()
const emit = defineEmits<{ connect: []; navigate: [path: string] }>()
let mounted = true
onBeforeUnmount(() => {
  mounted = false
})
const requirement = ref(''),
  title = ref(''),
  showCreate = ref(false),
  submitting = ref(false),
  template = ref(''),
  frontend = ref(''),
  database = ref(''),
  intelligent = ref(false),
  composer = ref<any>(),
  error = ref('')
const selected = computed(() => state.catalog.find((c) => c.template === template.value))
const project = computed(() => state.projects.find((p) => p.id === props.projectId))
const recent = computed(() => state.projects.slice(0, 4))
const latestRun = (id: string) => state.runs.find((r) => r.project_id === id)
watch(template, () => {
  frontend.value = selected.value?.frontends[0] || ''
  database.value = selected.value?.databases[0] || ''
})
const starters = [
  {
    icon: MessageOutlined,
    title: '做一个客服管理系统',
    subtitle: '客户、工单与团队协作',
    text: '我想做一个内部客服管理系统，管理客户与工单，支持团队协作。',
  },
  {
    icon: CodeOutlined,
    title: '从一个业务流程开始',
    subtitle: '把日常操作变成易用的工具',
    text: '我想把一个日常业务流程变成工具：',
  },
  {
    icon: FileTextOutlined,
    title: '我已经有一份需求',
    subtitle: '粘贴内容，补齐范围与验收',
    text: '',
  },
]
function start(text: string) {
  requirement.value = text
  nextTick(() => composer.value?.focus())
}
function prepare() {
  if (!requirement.value.trim()) return
  if (!state.authenticated) {
    emit('connect')
    return
  }
  if (!state.settings?.ready) {
    emit('navigate', 'settings')
    state.notice = '先完成默认模型连接配置，再开始研发对话'
    return
  }
  template.value = state.catalog[0]?.template || ''
  title.value = project.value?.title || requirement.value.trim().split('\n')[0].slice(0, 50)
  intelligent.value = false
  error.value = ''
  showCreate.value = true
}
function keydown(event: KeyboardEvent) {
  if (event.key === 'Enter' && !event.shiftKey && !event.isComposing && event.keyCode !== 229) {
    event.preventDefault()
    prepare()
  }
}
async function create() {
  if (
    submitting.value ||
    !state.online ||
    !title.value.trim() ||
    !selected.value ||
    !requirement.value.trim()
  )
    return
  submitting.value = true
  error.value = ''
  const targetHash = location.hash
  const fingerprint = JSON.stringify({
    project: props.projectId,
    title: title.value.trim(),
    requirement: requirement.value.trim(),
    template: template.value,
    frontend: frontend.value,
    database: database.value,
    intelligent: intelligent.value,
  })
  try {
    const p = props.projectId
      ? { id: props.projectId }
      : await api('/projects', {
          method: 'POST',
          body: { title: title.value.trim() },
          key: mutationKey('project:' + fingerprint),
        })
    const result = await api(`/projects/${p.id}/runs`, {
      method: 'POST',
      body: {
        requirement: requirement.value.trim(),
        template: template.value,
        selection: {
          template: template.value,
          backend: selected.value.backend,
          frontend: frontend.value,
          database: database.value,
        },
        intelligent: intelligent.value,
      },
      key: mutationKey('run:' + fingerprint),
    })
    clearMutationKey('project:' + fingerprint)
    clearMutationKey('run:' + fingerprint)
    showCreate.value = false
    requirement.value = ''
    await refreshLists()
    if (mounted && location.hash === targetHash)
      emit('navigate', 'run/' + result.run_id + '/conversation')
  } catch (e) {
    if (!mounted || location.hash !== targetHash) return
    reportError(e)
    error.value = state.error
  } finally {
    submitting.value = false
  }
}
</script>
<template>
  <div class="home-page">
    <div class="home-hero">
      <div class="sparkle-tile"><ThunderboltOutlined aria-hidden="true" /></div>
      <div class="eyebrow">YOUR NEXT IDEA STARTS HERE</div>
      <h1>{{ project ? `继续「${project.title}」` : '今天，想做点什么？' }}</h1>
      <p>从一句需求开始，一起推进到方案、开发与可验证的交付。</p>
    </div>
    <form class="home-composer" @submit.prevent="prepare">
      <a-textarea
        ref="composer"
        v-model:value="requirement"
        aria-label="描述你的产品需求"
        placeholder="描述你想做的产品，也可以先聊一个还不完整的想法…"
        :auto-size="{ minRows: 4, maxRows: 10 }"
        :maxlength="20000"
        :bordered="false"
        @keydown="keydown"
      />
      <div class="composer-tools">
        <a-button type="text" aria-label="查看新对话技术选型" @click="prepare"
          ><PlusOutlined aria-hidden="true" /></a-button
        ><button type="button" class="model-pill" @click="emit('navigate', 'settings')">
          <ThunderboltOutlined aria-hidden="true" />默认模型 ·
          {{
            state.authenticated ? (state.settings?.ready ? '已配置' : '待配置') : '连接后查看'
          }}</button
        ><a-button
          type="primary"
          html-type="submit"
          size="large"
          class="send-button"
          aria-label="开始研发对话"
          :disabled="!requirement.trim() || !state.online"
          ><ArrowUpOutlined aria-hidden="true"
        /></a-button>
      </div>
    </form>
    <p class="composer-hint">
      先澄清需求，再确认方案。关键节点由你决定。<span>Enter 发送 · Shift + Enter 换行</span>
    </p>
    <div class="starter-grid">
      <button
        v-for="starter in starters"
        :key="starter.title"
        class="starter-card"
        @click="start(starter.text)"
      >
        <component aria-hidden="true" :is="starter.icon" />
        <div>
          <h3>{{ starter.title }}</h3>
          <p>{{ starter.subtitle }}</p>
        </div>
      </button>
    </div>
    <section class="recent-section">
      <div class="section-top">
        <h3>继续最近的项目</h3>
        <a-button type="link" @click="emit('navigate', 'projects')"
          >查看全部 <ArrowRightOutlined aria-hidden="true"
        /></a-button>
      </div>
      <div v-if="recent.length" class="recent-grid">
        <button
          v-for="p in recent"
          :key="p.id"
          class="recent-card panel"
          @click="
            emit(
              'navigate',
              latestRun(p.id) ? 'run/' + latestRun(p.id)!.id + '/conversation' : 'project/' + p.id,
            )
          "
        >
          <div class="project-icon"><MessageOutlined aria-hidden="true" /></div>
          <div>
            <h3>{{ p.title }}</h3>
            <p>{{ formatDate(latestRun(p.id)?.updated_at || p.created_at) }}</p>
          </div>
          <a-tag :color="statusColor(latestRun(p.id)?.status)">{{
            statusLabel(latestRun(p.id)?.status)
          }}</a-tag>
        </button>
      </div>
      <div v-else class="quiet-empty panel">
        <FileTextOutlined aria-hidden="true" />
        <div>
          <strong>{{
            state.authenticated ? '还没有项目，第一句话就是起点' : '连接本地工作空间，继续你的项目'
          }}</strong>
          <p>
            {{
              state.authenticated
                ? '需求、确认记录与每轮运行会自动保存。'
                : '输入本机访问令牌后，读取真实项目与运行记录。'
            }}
          </p>
        </div>
        <a-button v-if="!state.authenticated" @click="emit('connect')">连接工作空间</a-button>
      </div>
    </section>
    <p class="home-footer">
      <SafetyCertificateOutlined aria-hidden="true" />密钥不在对话中展示
      <span>·</span> 阶段产物可回看 <span>·</span> 确认后再推进
    </p>
    <a-modal
      v-model:open="showCreate"
      title="确认本次研发的技术选型"
      :footer="null"
      :mask-closable="!submitting"
      :closable="!submitting"
      :keyboard="!submitting"
      width="650px"
    >
      <form @submit.prevent="create" class="create-form">
        <p>技术模板决定可实现的能力。提交后创建一轮真实运行，可能产生模型服务费用。</p>
        <label class="form-label" for="new-project-title">项目名称</label
        ><a-input
          id="new-project-title"
          v-model:value="title"
          :disabled="submitting || !!project"
          :maxlength="200"
        /><label class="form-label" for="template-selection">项目模板 / 后端</label
        ><a-select
          id="template-selection"
          v-model:value="template"
          :disabled="submitting"
          :options="state.catalog.map((c) => ({ value: c.template, label: c.name }))"
        />
        <div class="form-grid">
          <div>
            <label class="form-label" for="frontend-selection">前端</label
            ><a-select
              id="frontend-selection"
              v-model:value="frontend"
              :disabled="submitting"
              :options="(selected?.frontends || []).map((value) => ({ value, label: value }))"
            />
          </div>
          <div>
            <label class="form-label" for="database-selection">数据库</label
            ><a-select
              id="database-selection"
              v-model:value="database"
              :disabled="submitting"
              :options="(selected?.databases || []).map((value) => ({ value, label: value }))"
            />
          </div>
        </div>
        <div v-if="selected" class="template-summary">
          <strong>当前模板能力</strong>
          <p>数据范围：{{ (selected.scopes || [selected.scope]).join(' / ') }}</p>
          <p>{{ selected.features.join(' · ') }}</p>
          <p>
            {{
              selected.template === 'python-basic'
                ? 'SQLite 无需独立数据库服务；PostgreSQL 需准备数据库。'
                : '原生模板需要 Linux / WSL，以及对应后端、Node、PostgreSQL、Redis 环境。'
            }}
          </p>
        </div>
        <a-collapse class="example-help"
          ><a-collapse-panel key="customer-service" header="需求示例：内部客户服务管理平台"
            ><p>示例供你参考，不会替换已输入的需求。</p>
            <ul>
              <li>examples/requirements/customer-service.md：完整业务需求</li>
              <li>examples/requirements/customer-service-decisions.md：需要确认的业务决定</li>
              <li>examples/requirements/customer-service-contract.md：结构化业务合同</li>
            </ul>
            <p>
              声明式业务合同支持已登记的角色与行范围、关联、分配、状态、处理记录、站内提醒和统计；不会执行任意跨实体脚本。
            </p></a-collapse-panel
          ></a-collapse
        ><a-checkbox v-model:checked="intelligent" :disabled="submitting"
          >启用智能推荐（持续委托）</a-checkbox
        ><a-alert
          v-if="intelligent"
          type="warning"
          show-icon
          message="AI 将补全未明确项，并自动批准后续设计与交付，不再逐项询问；测试门禁仍然生效。"
          class="compact-alert"
        />
        <p v-else class="field-hint">人工确认模式：需求、设计与交付等关键节点等待你确认。</p>
        <a-alert v-if="error" type="error" :message="error" show-icon />
        <div class="form-actions">
          <a-button :disabled="submitting" @click="showCreate = false">返回编辑</a-button
          ><a-button
            type="primary"
            html-type="submit"
            :loading="submitting"
            :disabled="!title.trim() || !template || !state.online"
            >确认选型并开始</a-button
          >
        </div>
      </form>
    </a-modal>
  </div>
</template>
