# ui/src/components/ProjectsView.vue · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：Vue 3 / Ant Design本机操作台源码。** 读取、筛选和打开已有项目，将导航交给上层；不在项目列表中另造创建运行的业务逻辑。

**对应关系：** ui/src及锁文件 → npm ci/test/build → workbench/web → FastAPI本机页面；与生成产品的前端模板是两套不同界面。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `ui/src/components/ProjectsView.vue`；**本文件共有 1 段**。本段覆盖源文件 L1–L294。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`9946`。本段原文以LF换行结束。

<!-- learning-source: {"path": "ui/src/components/ProjectsView.vue", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "f85185f3d604b27ed8d02c5a9d70123b2b553bcfd48417e943ac00f0502ef01d"} -->
````vue
<!-- ui/src/components/ProjectsView.vue -->
<script setup lang="ts">
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import {
  PlusOutlined,
  ArrowRightOutlined,
  FolderOutlined,
  SearchOutlined,
  ReloadOutlined,
} from '@ant-design/icons-vue'
import { state, refreshLists, reportError, sessionIdentity, isSessionActive } from '../state'
import { api, errorText } from '../api'
import type { Run } from '../types'
import {
  statusColor,
  statusLabel,
  formatDate,
  shortId,
  runFilters,
  runGroup,
  runNextAction,
} from '../presentation'
import RunTable from './RunTable.vue'
const props = defineProps<{ view: string; projectId?: string }>()
const emit = defineEmits<{ navigate: [path: string] }>()
const query = ref(''),
  filter = ref('all'),
  template = ref('all'),
  refreshing = ref(false),
  listedRuns = ref<Run[]>([]),
  hasMore = ref(false),
  loadingRuns = ref(false),
  listError = ref('')
let listGeneration = 0
onBeforeUnmount(() => {
  listGeneration++
})
const deliveryStatuses = [
  'READY',
  'SOURCE_READY',
  'WAITING_DELIVERY',
  'WAITING_EXTENSION_SCOPE',
  'WAITING_EXTENSION_DELIVERY',
]
async function loadRuns(append = false) {
  if (append && loadingRuns.value) return
  const generation = ++listGeneration,
    session = sessionIdentity()
  loadingRuns.value = true
  listError.value = ''
  const parameters = new URLSearchParams({
    limit: '100',
    offset: String(append ? listedRuns.value.length : 0),
  })
  if (props.view === 'delivery')
    deliveryStatuses.forEach((status) => parameters.append('status', status))
  try {
    const page = await api<Run[]>(
      (props.projectId ? '/projects/' + props.projectId + '/runs' : '/runs') + '?' + parameters,
    )
    if (generation !== listGeneration || !isSessionActive(session)) return
    listedRuns.value = append ? [...listedRuns.value, ...page] : page
    hasMore.value = page.length === 100
  } catch (error) {
    if (generation === listGeneration && isSessionActive(session)) {
      listError.value = errorText(error)
      reportError(error)
    }
  } finally {
    if (generation === listGeneration) loadingRuns.value = false
  }
}
watch(
  () => [props.projectId, props.view],
  () => {
    listedRuns.value = []
    hasMore.value = false
    void loadRuns()
  },
  { immediate: true },
)
const project = computed(() => state.projects.find((item) => item.id === props.projectId))
const title = computed(() =>
  props.view === 'history'
    ? '运行历史'
    : props.view === 'delivery'
      ? '交付与验收'
      : project.value?.title || '项目工作台',
)
const projectName = (id: string) =>
  state.projects.find((item) => item.id === id)?.title || '项目 ' + shortId(id)
const latest = (id: string) =>
  listedRuns.value.find((run) => run.project_id === id) ||
  state.runs.find((run) => run.project_id === id)
const search = computed(() => query.value.trim().toLowerCase())
function matches(run?: Run) {
  return (
    (filter.value === 'all' || runGroup(run) === filter.value) &&
    (template.value === 'all' || run?.template === template.value)
  )
}
const runs = computed(() =>
  listedRuns.value.filter(
    (run) =>
      (!props.projectId || run.project_id === props.projectId) &&
      (props.view !== 'delivery' || deliveryStatuses.includes(run.status)) &&
      matches(run) &&
      [projectName(run.project_id), run.id, run.status, statusLabel(run.status), run.template]
        .join(' ')
        .toLowerCase()
        .includes(search.value),
  ),
)
const projects = computed(() =>
  state.projects.filter(
    (item) =>
      matches(latest(item.id)) &&
      [item.title, item.id, latest(item.id)?.template, statusLabel(latest(item.id)?.status)]
        .join(' ')
        .toLowerCase()
        .includes(search.value),
  ),
)
const templateOptions = computed(() => [
  { value: 'all', label: '全部模板' },
  ...[
    ...new Set([
      ...state.catalog.map((entry) => entry.template),
      ...listedRuns.value.map((run) => run.template),
    ]),
  ].map((value) => ({
    value,
    label: state.catalog.find((entry) => entry.template === value)?.name || value,
  })),
])
const counts = computed(() =>
  runFilters.map((item) => ({
    ...item,
    count:
      item.value === 'all'
        ? listedRuns.value.length
        : listedRuns.value.filter((run) => runGroup(run) === item.value).length,
  })),
)
async function refresh() {
  if (refreshing.value) return
  refreshing.value = true
  try {
    await refreshLists({ models: false })
    await loadRuns()
  } finally {
    refreshing.value = false
  }
}
function resetFilters() {
  query.value = ''
  filter.value = 'all'
  template.value = 'all'
}
</script>
<template>
  <div class="page projects-page">
    <header class="page-heading">
      <div>
        <div class="eyebrow">
          {{
            view === 'delivery'
              ? 'DELIVERY & EVIDENCE'
              : view === 'history'
                ? 'RUN HISTORY'
                : 'PROJECTS'
          }}
        </div>
        <h1>{{ title }}</h1>
        <p>
          {{
            view === 'delivery'
              ? '源码级、运行级与部分成果分别标明，验收证据可逐项查看。'
              : '每个项目保存独立运行；查看当前状态，处理需要你回应的任务。'
          }}
        </p>
      </div>
      <a-button
        type="primary"
        size="large"
        @click="emit('navigate', projectId ? 'project/' + projectId + '/new' : 'home')"
        ><PlusOutlined aria-hidden="true" />{{
          projectId ? '新一轮运行' : '新建 / 批量创建'
        }}</a-button
      >
    </header>
    <div class="list-toolbar">
      <div class="filter-tabs" role="group" aria-label="按运行状态筛选">
        <button
          v-for="item in counts"
          :key="item.value"
          type="button"
          :class="{ active: filter === item.value }"
          :aria-pressed="filter === item.value"
          @click="filter = item.value"
        >
          {{ item.label }} <span>{{ item.count }}</span>
        </button>
      </div>
      <div class="search-actions">
        <a-input
          v-model:value="query"
          placeholder="搜索名称、运行 ID 或状态"
          aria-label="搜索项目和运行"
          allow-clear
          ><template #prefix><SearchOutlined aria-hidden="true" /></template></a-input
        ><a-select
          v-model:value="template"
          :options="templateOptions"
          aria-label="按技术模板筛选"
          class="template-filter"
        /><a-button :loading="refreshing" aria-label="刷新项目和运行" @click="refresh"
          ><ReloadOutlined aria-hidden="true"
        /></a-button>
      </div>
    </div>
    <a-alert
      v-if="listError"
      type="error"
      show-icon
      class="list-error"
      message="运行记录读取失败"
      :description="
        listError +
        (listedRuns.length ? '。下方保留上次读取的记录。' : '。请重新读取，项目不会丢失。')
      "
      ><template #action
        ><a-button :loading="loadingRuns" @click="loadRuns()">重新读取</a-button></template
      ></a-alert
    >
    <div v-if="view === 'projects' && !projectId && projects.length" class="project-grid">
      <article v-for="item in projects" :key="item.id" class="panel project-card">
        <div class="section-top">
          <div class="project-icon"><FolderOutlined aria-hidden="true" /></div>
          <a-tag :color="statusColor(latest(item.id)?.status)">{{
            statusLabel(latest(item.id)?.status)
          }}</a-tag>
        </div>
        <h2>{{ item.title }}</h2>
        <p>
          {{ latest(item.id) ? runNextAction(latest(item.id)!) : '创建第一轮需求，开始生成项目' }}
        </p>
        <p class="muted">
          {{ latest(item.id)?.template || '尚未选择模板' }} · {{ shortId(item.id) }}
        </p>
        <div class="project-card-footer">
          <span>{{ formatDate(latest(item.id)?.updated_at || item.created_at) }}</span
          ><a-button
            type="text"
            :aria-label="'打开项目 ' + item.title"
            @click="emit('navigate', 'project/' + item.id)"
            >打开项目 <ArrowRightOutlined aria-hidden="true"
          /></a-button>
        </div>
      </article>
    </div>
    <section class="panel run-list" :aria-busy="loadingRuns">
      <div class="panel-heading">
        <h2>{{ view === 'delivery' ? '交付与待确认产物' : '运行队列' }}</h2>
        <span class="muted">已读取 {{ listedRuns.length }} 条 · 匹配 {{ runs.length }} 条</span>
      </div>
      <div v-if="loadingRuns && !listedRuns.length" class="panel-content" role="status">
        <a-skeleton active :paragraph="{ rows: 4 }" />
        <p class="muted">正在读取保存的运行记录…</p>
      </div>
      <RunTable v-else-if="runs.length" :runs="runs" @navigate="(path) => emit('navigate', path)" />
      <a-empty
        v-else-if="!listError"
        :description="
          listedRuns.length || query || filter !== 'all' || template !== 'all'
            ? '没有符合筛选条件的运行'
            : '还没有运行记录'
        "
        class="list-empty"
        ><a-button v-if="query || filter !== 'all' || template !== 'all'" @click="resetFilters"
          >清除筛选</a-button
        ><a-button
          v-else
          @click="emit('navigate', projectId ? 'project/' + projectId + '/new' : 'home')"
          >开始一轮新需求</a-button
        ></a-empty
      >
      <div v-if="hasMore" class="panel-footer">
        <span>筛选适用于已读取的记录，可继续加载历史。</span
        ><a-button :loading="loadingRuns" @click="loadRuns(true)">加载更早的运行</a-button>
      </div>
    </section>
    <p class="page-footnote">故障恢复保留原 run_id 和已有步骤；新一轮根据本次完整需求重新生成。</p>
  </div>
</template>
````
