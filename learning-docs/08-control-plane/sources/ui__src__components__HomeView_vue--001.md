# ui/src/components/HomeView.vue · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：Vue 3 / Ant Design本机操作台源码。** 接收用户需求，在提交前打开技术组合与标题确认，再调用创建项目（需要时）和创建运行接口；兼容项以服务器目录为准，重试复用幂等请求身份。

**对应关系：** ui/src及锁文件 → npm ci/test/build → workbench/web → FastAPI本机页面；与生成产品的前端模板是两套不同界面。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `ui/src/components/HomeView.vue`；**本文件共有 1 段**。本段覆盖源文件 L1–L592。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`22961`。本段原文以LF换行结束。

<!-- learning-source: {"path": "ui/src/components/HomeView.vue", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "127f939ee49d357a3d50e947fe3e49db40ecce77943736d1b9fb3c06caa61f27"} -->
````vue
<!-- ui/src/components/HomeView.vue -->
<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, ref, toRefs, watch } from 'vue'
import {
  ArrowRightOutlined,
  CodeOutlined,
  FileTextOutlined,
  MessageOutlined,
  PlusOutlined,
  ReloadOutlined,
  ThunderboltOutlined,
  DeleteOutlined,
} from '@ant-design/icons-vue'
import {
  state,
  mutationKey,
  clearMutationKey,
  refreshLists,
  reportError,
  sessionIdentity,
  isSessionActive,
} from '../state'
import { api } from '../api'
import { formatDate, runGroup, statusColor, statusLabel } from '../presentation'
import type { BatchReceipt } from '../types'
import RunTable from './RunTable.vue'

const props = defineProps<{ projectId?: string }>()
const emit = defineEmits<{ connect: []; navigate: [path: string] }>()
const draftKey = computed(() => props.projectId || 'home')
const requirement = computed({
  get: () => state.homeDrafts[draftKey.value] || '',
  set: (value: string) => {
    state.homeDrafts[draftKey.value] = value
  },
})
const title = computed({
  get: () => state.homeTitles[draftKey.value] || '',
  set: (value: string) => {
    state.homeTitles[draftKey.value] = value
  },
})
const { template, frontend, database, intelligent, allowCustomExtensions } = toRefs(state.creation)
const submitting = ref(false),
  refreshingBatch = ref(false),
  composer = ref<any>(),
  error = ref('')
const selected = computed(() => state.catalog.find((entry) => entry.template === template.value))
const project = computed(() => state.projects.find((item) => item.id === props.projectId))
const recent = computed(() => state.projects.slice(0, 4))
const latestRun = (id: string) => state.runs.find((run) => run.project_id === id)
const mode = computed({
  get: () => (!props.projectId && state.batchMode ? 'batch' : 'single'),
  set: (value: string | number) => {
    state.batchMode = value === 'batch'
    if (state.batchMode && !state.batchDrafts.length) addDraft(requirement.value, title.value)
  },
})
const draftsValid = computed(() =>
  mode.value === 'batch'
    ? state.batchDrafts.length > 0 && state.batchDrafts.every((draft) => draft.requirement.trim())
    : !!requirement.value.trim(),
)
const batchActive = computed(() => state.batchRuns.some((run) => runGroup(run) === 'running'))
const batchSummary = computed(() =>
  [
    ['running', '进行中'],
    ['waiting', '待处理'],
    ['failed', '失败'],
    ['ready', '可交付'],
  ].map(([group, label]) => ({
    label,
    count: state.batchRuns.filter((run) => runGroup(run) === group).length,
  })),
)
let mounted = true
let batchTimer: ReturnType<typeof setInterval> | undefined
onBeforeUnmount(() => {
  mounted = false
  clearInterval(batchTimer)
})
watch(template, () => {
  frontend.value = selected.value?.frontends[0] || ''
  database.value = selected.value?.databases[0] || ''
})
watch(
  () => state.catalog,
  () => {
    if (!selected.value) template.value = state.catalog[0]?.template || ''
    else {
      if (!selected.value.frontends.includes(frontend.value))
        frontend.value = selected.value.frontends[0] || ''
      if (!selected.value.databases.includes(database.value))
        database.value = selected.value.databases[0] || ''
    }
  },
  { immediate: true },
)
watch(
  batchActive,
  (active) => {
    clearInterval(batchTimer)
    if (active)
      batchTimer = setInterval(() => {
        if (document.visibilityState !== 'hidden') void refreshBatch()
      }, 5000)
  },
  { immediate: true },
)

const starters = [
  {
    icon: MessageOutlined,
    title: '做一个客服管理系统',
    subtitle: '客户、工单与团队协作',
    text: '我想做一个内部客服管理系统，管理客户与工单，支持团队协作。请明确角色权限、工单分配和状态流转，并提供可验证的用户操作流程。',
  },
  {
    icon: CodeOutlined,
    title: '做一个比赛报名系统',
    subtitle: '学生登录报名与管理员审核',
    text: '为大学生计算机设计大赛提供登录后使用的报名管理系统。参赛学生自行提交并查看本人报名记录；大赛管理员查看所有报名记录，并审核为通过或退回。学生不能访问其他学生的记录，不能自行审核或提升为管理员。请推荐报名字段和界面细节，保留上述角色与权限要求。',
  },
  {
    icon: FileTextOutlined,
    title: '做一个阅读书架',
    subtitle: '书目、阅读状态与个人记录',
    text: '制作一个阅读书架：维护书目、作者、阅读状态与备注，支持查询筛选。用户仅能查看和编辑自己的记录，管理员管理全部书目。请提供数据持久化、权限隔离和关键用户流程的验收证据。',
  },
]
function addDraft(text = '', name = '') {
  if (state.batchDrafts.length >= 10 || submitting.value) return
  state.batchDrafts.push({ id: crypto.randomUUID(), title: name, requirement: text })
}
function start(text: string) {
  if (mode.value === 'batch') addDraft(text)
  else {
    requirement.value = text
    nextTick(() => composer.value?.focus())
  }
}
function configure() {
  state.settingsReturn = props.projectId ? 'project/' + props.projectId + '/new' : 'home'
  emit('navigate', 'settings')
}
async function refreshBatch() {
  if (refreshingBatch.value || !state.authenticated) return
  refreshingBatch.value = true
  try {
    await refreshLists({ models: false })
  } finally {
    refreshingBatch.value = false
  }
}
function keydown(event: KeyboardEvent) {
  if (event.key === 'Enter' && (event.ctrlKey || event.metaKey) && !event.isComposing) {
    event.preventDefault()
    void create()
  }
}
async function create() {
  if (submitting.value || !draftsValid.value || !state.online) return
  if (!state.authenticated) {
    emit('connect')
    return
  }
  if (!state.settings?.ready) {
    configure()
    state.notice = '先完成默认模型连接配置，需求草稿已保留。'
    return
  }
  if (!selected.value || !frontend.value || !database.value) {
    error.value = '请选择可用模板及其前端、数据库。'
    return
  }
  const session = sessionIdentity(),
    targetHash = location.hash
  const config = {
    template: template.value,
    selection: {
      template: template.value,
      backend: selected.value.backend,
      frontend: frontend.value,
      database: database.value,
    },
    intelligent: intelligent.value,
    allow_custom_extensions: allowCustomExtensions.value,
  }
  const items = (
    mode.value === 'batch'
      ? state.batchDrafts
      : [{ title: project.value?.title || title.value, requirement: requirement.value }]
  ).map((draft) => ({
    ...config,
    title: draft.title.trim() || draft.requirement.trim().split('\n')[0].slice(0, 50),
    requirement: draft.requirement.trim(),
  }))
  const batch = mode.value === 'batch',
    fingerprint = JSON.stringify({ project: props.projectId, items })
  submitting.value = true
  error.value = ''
  try {
    if (batch) {
      const receipt = await api<BatchReceipt>('/batches', {
        method: 'POST',
        body: { items },
        key: mutationKey('batch:' + fingerprint),
      })
      if (!isSessionActive(session)) return
      clearMutationKey('batch:' + fingerprint)
      state.batchRuns = receipt.items.map((item) => ({
        id: item.run_id,
        project_id: item.project_id,
        project_title: item.title,
        template: config.template,
        auto_mode: config.intelligent,
        status: item.status,
      }))
      for (const item of receipt.items) {
        if (!state.projects.some((saved) => saved.id === item.project_id))
          state.projects.unshift({ id: item.project_id, title: item.title })
      }
      state.runs = [
        ...state.batchRuns,
        ...state.runs.filter((run) => !state.batchRuns.some((item) => item.id === run.id)),
      ]
      if (mounted) state.batchDrafts = []
      state.notice = receipt.items.length + ' 个项目已全部入队；每个项目保留独立的运行与审批记录。'
      await refreshBatch()
    } else {
      const item = items[0]
      const targetProject = props.projectId
        ? { id: props.projectId }
        : await api<{ id: string }>('/projects', {
            method: 'POST',
            body: { title: item.title },
            key: mutationKey('project:' + fingerprint),
          })
      if (!isSessionActive(session)) return
      const result = await api<{ run_id: string }>('/projects/' + targetProject.id + '/runs', {
        method: 'POST',
        body: { ...config, requirement: item.requirement },
        key: mutationKey('run:' + fingerprint),
      })
      if (!isSessionActive(session)) return
      clearMutationKey('project:' + fingerprint)
      clearMutationKey('run:' + fingerprint)
      if (mounted) {
        requirement.value = ''
        title.value = ''
      }
      await refreshLists({ models: false })
      if (mounted && location.hash === targetHash)
        emit('navigate', 'run/' + result.run_id + '/conversation')
    }
  } catch (failure) {
    if (!mounted || !isSessionActive(session) || location.hash !== targetHash) return
    reportError(failure)
    error.value = state.error + '。草稿已保留，重新提交同一内容会复用请求标识。'
  } finally {
    submitting.value = false
  }
}
</script>
<template>
  <div class="home-page">
    <header class="home-hero">
      <div class="eyebrow">TEMPLATE → BUILD → VERIFY</div>
      <h1>
        {{
          projectId
            ? '为「' + (project?.title || '当前项目') + '」开始新一轮'
            : '从模板到可验证的全栈项目'
        }}
      </h1>
      <p>选择基础模板，描述需要的功能。逐步查看方案、代码生成和真实验收结果。</p>
      <p v-if="projectId" class="field-hint">新一轮根据完整需求重新生成，历史运行与产物会保留。</p>
    </header>
    <section
      v-if="!projectId && state.batchRuns.length"
      class="panel batch-results"
      aria-label="本次批量队列"
      aria-live="polite"
    >
      <div class="panel-heading">
        <div>
          <h2>本次批量 · {{ state.batchRuns.length }} 个项目</h2>
          <p>
            {{
              batchActive
                ? '队列每 5 秒更新，可打开任一运行查看过程。'
                : '每个项目的结果与审批状态分别展示。'
            }}
          </p>
        </div>
        <a-button :loading="refreshingBatch" aria-label="刷新批量队列" @click="refreshBatch"
          ><ReloadOutlined aria-hidden="true"
        /></a-button>
      </div>
      <div class="queue-summary">
        <span v-for="item in batchSummary" :key="item.label"
          ><strong>{{ item.count }}</strong> {{ item.label }}</span
        >
      </div>
      <RunTable :runs="state.batchRuns" @navigate="(path) => emit('navigate', path)" />
    </section>
    <form class="panel creation-panel" :aria-busy="submitting" @submit.prevent="create">
      <div class="section-top">
        <h2>{{ projectId ? '新一轮需求' : '创建项目' }}</h2>
        <a-segmented
          v-if="!projectId"
          v-model:value="mode"
          :disabled="submitting"
          :options="[
            { value: 'single', label: '单个项目' },
            { value: 'batch', label: '批量项目' },
          ]"
          aria-label="项目创建方式"
        />
      </div>
      <fieldset class="template-picker" :disabled="submitting">
        <legend>1. 选择模板</legend>
        <div v-if="state.catalog.length" class="template-grid">
          <label
            v-for="entry in state.catalog"
            :key="entry.template"
            class="template-card"
            :class="{ selected: template === entry.template }"
          >
            <input
              v-model="template"
              type="radio"
              name="project-template"
              :value="entry.template"
              :aria-label="entry.name"
            />
            <span class="template-card-title"
              ><strong>{{ entry.name }}</strong
              ><small>{{ entry.backend }}</small></span
            >
            <span>{{ entry.frontends.join(' / ') }} · {{ entry.databases.join(' / ') }}</span>
            <small>{{ entry.coding_standard?.summary || entry.features.join(' · ') }}</small>
          </label>
        </div>
        <div v-else class="quiet-empty">
          <FileTextOutlined aria-hidden="true" />
          <div>
            <strong>{{
              state.authenticated ? '模板目录暂时不可用' : '连接工作空间后选择可用模板'
            }}</strong>
            <p>模板决定项目基础结构、能力边界与编码规范。</p>
          </div>
          <a-button @click="state.authenticated ? refreshLists() : emit('connect')">{{
            state.authenticated ? '重新读取' : '连接工作空间'
          }}</a-button>
        </div>
      </fieldset>
      <div v-if="selected" class="selection-details">
        <p><strong>已包含：</strong>{{ selected.features.join(' · ') }}</p>
        <a-collapse ghost>
          <a-collapse-panel key="selection" header="技术选型与模板编码规范">
            <div class="form-grid">
              <div>
                <label class="form-label" for="frontend-selection">前端</label
                ><a-select
                  id="frontend-selection"
                  v-model:value="frontend"
                  :disabled="submitting"
                  :options="selected.frontends.map((value) => ({ value, label: value }))"
                />
              </div>
              <div>
                <label class="form-label" for="database-selection">数据库</label
                ><a-select
                  id="database-selection"
                  v-model:value="database"
                  :disabled="submitting"
                  :options="selected.databases.map((value) => ({ value, label: value }))"
                />
              </div>
            </div>
            <p class="field-hint">
              数据范围：{{
                (selected.scopes || [selected.scope]).filter(Boolean).join(' / ') ||
                '按模板合同确认'
              }}。{{
                selected.template === 'python-basic'
                  ? 'SQLite 无需独立数据库服务；PostgreSQL 需准备数据库。'
                  : '原生模板需准备 Linux / WSL、Node、对应数据库与缓存服务。'
              }}
            </p>
            <div v-if="selected.coding_standard" class="coding-standard">
              <strong>AI 定制此模板时使用的规范</strong>
              <p>{{ selected.coding_standard.summary }}</p>
              <small
                >{{ selected.coding_standard.path
                }}<span v-if="selected.coding_standard.sha256">
                  · SHA-256 {{ selected.coding_standard.sha256.slice(0, 12) }}</span
                ></small
              >
              <details v-if="selected.coding_standard.content">
                <summary>展开完整编码规范</summary>
                <pre>{{ selected.coding_standard.content }}</pre>
              </details>
            </div>
          </a-collapse-panel>
        </a-collapse>
      </div>
      <section class="requirements-editor">
        <h3>2. 描述功能与验收目标</h3>
        <template v-if="mode === 'single'">
          <label class="form-label" for="new-project-title"
            >项目名称 <span class="muted">· 留空时使用需求首行</span></label
          ><a-input
            id="new-project-title"
            v-model:value="title"
            :disabled="submitting || !!project"
            :placeholder="project?.title || '例如：团队阅读书架'"
            :maxlength="200"
          />
          <label class="form-label" for="project-requirement">需求描述</label
          ><a-textarea
            id="project-requirement"
            ref="composer"
            v-model:value="requirement"
            aria-label="描述你的产品需求"
            placeholder="谁会使用？需要哪些页面和功能？怎样判断完成？可以先描述想法，再逐步确认细节。"
            :auto-size="{ minRows: 5, maxRows: 12 }"
            :maxlength="20000"
            :disabled="submitting"
            @keydown="keydown"
          />
        </template>
        <template v-else>
          <p class="field-hint">
            每项创建一个独立项目，共用上方模板和下方执行设置；一次最多 10 项。
          </p>
          <article v-for="(draft, index) in state.batchDrafts" :key="draft.id" class="batch-draft">
            <div class="section-top">
              <h3>项目 {{ index + 1 }}</h3>
              <a-button
                type="text"
                danger
                :disabled="submitting"
                :aria-label="'移除项目 ' + (index + 1)"
                @click="state.batchDrafts.splice(index, 1)"
                ><DeleteOutlined aria-hidden="true"
              /></a-button>
            </div>
            <label class="form-label" :for="'batch-title-' + draft.id">项目名称</label
            ><a-input
              :id="'batch-title-' + draft.id"
              v-model:value="draft.title"
              placeholder="留空时使用需求首行"
              :maxlength="200"
              :disabled="submitting"
            />
            <label class="form-label" :for="'batch-requirement-' + draft.id">需求描述</label
            ><a-textarea
              :id="'batch-requirement-' + draft.id"
              v-model:value="draft.requirement"
              :aria-label="'项目 ' + (index + 1) + ' 的需求'"
              :auto-size="{ minRows: 3, maxRows: 8 }"
              :maxlength="20000"
              :disabled="submitting"
              placeholder="描述这个项目的用户、功能和验收目标"
            />
          </article>
          <p v-if="!state.batchDrafts.length" class="quiet-empty">
            添加项目准备下一批；已提交的运行可在上方队列继续查看。
          </p>
          <a-button
            block
            class="add-batch"
            :disabled="submitting || state.batchDrafts.length >= 10"
            @click="addDraft()"
            ><PlusOutlined aria-hidden="true" />添加项目 · {{ state.batchDrafts.length }} /
            10</a-button
          >
        </template>
      </section>
      <section class="execution-options">
        <h3>3. 选择执行方式</h3>
        <a-checkbox v-model:checked="intelligent" :disabled="submitting"
          >启用智能推荐（持续委托）</a-checkbox
        >
        <a-alert
          v-if="intelligent"
          type="warning"
          show-icon
          message="AI 将补全未明确项，并自动推进允许委托的审批。要求明确人工复核的关卡仍会暂停，测试门禁继续生效。"
        />
        <p v-else class="field-hint">
          人工确认模式：需求、设计与交付等关键节点等待你确认。批量项目分别审批。
        </p>
        <details class="extension-option">
          <summary>模板外功能设置</summary>
          <a-checkbox v-model:checked="allowCustomExtensions" :disabled="submitting"
            >允许受控自定义扩展</a-checkbox
          >
          <p class="field-hint">
            模板已有的登录、数据管理和权限功能无需启用扩展。模板外功能需要额外设计审批、执行环境和独立验收。
          </p>
        </details>
      </section>
      <a-alert v-if="error" type="error" :message="error" show-icon role="alert" />
      <div class="creation-footer">
        <button type="button" class="model-pill" @click="configure">
          <ThunderboltOutlined aria-hidden="true" />默认模型 ·
          {{
            state.authenticated ? (state.settings?.ready ? '已配置' : '待配置') : '连接后查看'
          }}</button
        ><a-button
          type="primary"
          html-type="submit"
          size="large"
          :loading="submitting"
          :disabled="!draftsValid || !state.online"
          >{{ mode === 'batch' ? '提交 ' + state.batchDrafts.length + ' 个项目' : '创建并开始'
          }}<ArrowRightOutlined aria-hidden="true"
        /></a-button>
      </div>
      <p class="field-hint">
        提交后会调用已配置模型，可能产生服务费用。{{
          mode === 'single'
            ? 'Enter 换行，Ctrl / ⌘ + Enter 提交。'
            : '所有项目通过输入校验后一起入队，实际执行与结果独立记录。'
        }}
      </p>
    </form>
    <section class="starter-section">
      <div class="section-top">
        <h3>从一个示例开始</h3>
        <span class="muted">填入后可自由修改</span>
      </div>
      <div class="starter-grid">
        <button
          v-for="starter in starters"
          :key="starter.title"
          class="starter-card"
          :disabled="submitting || (mode === 'batch' && state.batchDrafts.length >= 10)"
          @click="start(starter.text)"
        >
          <component :is="starter.icon" aria-hidden="true" />
          <div>
            <h3>{{ starter.title }}</h3>
            <p>{{ starter.subtitle }}</p>
          </div>
        </button>
      </div>
    </section>
    <section class="recent-section">
      <div class="section-top">
        <h3>继续最近的项目</h3>
        <a-button type="link" @click="emit('navigate', 'projects')"
          >查看全部 <ArrowRightOutlined aria-hidden="true"
        /></a-button>
      </div>
      <div v-if="recent.length" class="recent-grid">
        <button
          v-for="item in recent"
          :key="item.id"
          class="recent-card panel"
          @click="
            emit(
              'navigate',
              latestRun(item.id)
                ? 'run/' + latestRun(item.id)!.id + '/conversation'
                : 'project/' + item.id,
            )
          "
        >
          <div class="project-icon"><MessageOutlined aria-hidden="true" /></div>
          <div>
            <h3>{{ item.title }}</h3>
            <p>{{ formatDate(latestRun(item.id)?.updated_at || item.created_at) }}</p>
          </div>
          <a-tag :color="statusColor(latestRun(item.id)?.status)">{{
            statusLabel(latestRun(item.id)?.status)
          }}</a-tag>
        </button>
      </div>
      <div v-else class="quiet-empty panel">
        <FileTextOutlined aria-hidden="true" />
        <div>
          <strong>{{ state.authenticated ? '还没有项目' : '连接后查看已有项目' }}</strong>
          <p>创建后，需求、审批与每轮运行会自动保存。</p>
        </div>
        <a-button v-if="!state.authenticated" @click="emit('connect')">连接工作空间</a-button>
      </div>
    </section>
  </div>
</template>
````
