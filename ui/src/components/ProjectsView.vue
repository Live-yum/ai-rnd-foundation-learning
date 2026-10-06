<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import {
  PlusOutlined,
  ArrowRightOutlined,
  FolderOutlined,
  SearchOutlined,
  ReloadOutlined,
} from '@ant-design/icons-vue'
import { state, refreshLists, reportError, sessionIdentity, isSessionActive } from '../state'
import { api } from '../api'
import type { Run } from '../types'
import { statusColor, statusLabel, formatDate, shortId } from '../presentation'
const props = defineProps<{ view: string; projectId?: string }>()
const emit = defineEmits<{ navigate: [path: string] }>()
const query = ref(''),
  filter = ref('all'),
  refreshing = ref(false)
const listedRuns = ref<Run[]>([]),
  hasMore = ref(false),
  loadingRuns = ref(false)
let listGeneration = 0
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
  if (!append) listedRuns.value = []
  const parameters = new URLSearchParams({
    limit: '100',
    offset: String(append ? listedRuns.value.length : 0),
  })
  if (props.view === 'delivery')
    deliveryStatuses.forEach((status) => parameters.append('status', status))
  try {
    const page = await api<Run[]>(
      (props.projectId ? `/projects/${props.projectId}/runs` : '/runs') + '?' + parameters,
    )
    if (generation !== listGeneration || !isSessionActive(session)) return
    listedRuns.value = append ? [...listedRuns.value, ...page] : page
    hasMore.value = page.length === 100
  } catch (error) {
    if (generation === listGeneration && isSessionActive(session)) reportError(error)
  } finally {
    if (generation === listGeneration) loadingRuns.value = false
  }
}
watch(
  () => [props.projectId, props.view],
  () => void loadRuns(),
  { immediate: true },
)
const project = computed(() => state.projects.find((p) => p.id === props.projectId))
const title = computed(() =>
  props.view === 'history'
    ? '每轮运行，都留下完整记录'
    : props.view === 'delivery'
      ? '经过确认的成果，在这里交付'
      : project.value?.title || '每个项目，都能继续往下走',
)
const runs = computed(() =>
  listedRuns.value.filter(
    (r) =>
      (!props.projectId || r.project_id === props.projectId) &&
      (props.view !== 'delivery' || deliveryStatuses.includes(r.status)) &&
      (filter.value === 'all' ||
        (filter.value === 'ready'
          ? ['READY', 'SOURCE_READY'].includes(r.status)
          : filter.value === 'waiting'
            ? r.status.startsWith('WAITING') || r.status === 'BLOCKED'
            : ['QUEUED', 'RUNNING'].includes(r.status))) &&
      (projectName(r.project_id) + ' ' + r.id + ' ' + r.status)
        .toLowerCase()
        .includes(query.value.toLowerCase()),
  ),
)
const projectName = (id: string) =>
  state.projects.find((p) => p.id === id)?.title || '项目 ' + shortId(id)
const latest = (id: string) => state.runs.find((r) => r.project_id === id)
const projects = computed(() =>
  state.projects.filter(
    (p) =>
      p.title.toLowerCase().includes(query.value.toLowerCase()) &&
      (filter.value === 'all' || runs.value.some((r) => r.project_id === p.id)),
  ),
)
async function refresh() {
  refreshing.value = true
  await refreshLists()
  await loadRuns()
  refreshing.value = false
}
</script>
<template>
  <div class="page projects-page">
    <header class="page-heading">
      <div>
        <div class="eyebrow">
          {{
            view === 'delivery'
              ? 'DELIVERY CENTER'
              : view === 'history'
                ? 'RUN HISTORY'
                : 'YOUR WORKSPACE'
          }}
        </div>
        <h1>{{ title }}</h1>
        <p>
          {{
            view === 'delivery'
              ? '先核对验证证据，再确认交付。源码级与运行级验收分别标明。'
              : '项目保存上下文，运行保存过程；历史记录不会被新一轮覆盖。'
          }}
        </p>
      </div>
      <a-button
        type="primary"
        size="large"
        @click="emit('navigate', projectId ? 'project/' + projectId + '/new' : 'home')"
        ><PlusOutlined aria-hidden="true" />{{ projectId ? '新一轮运行' : '新建项目' }}</a-button
      >
    </header>
    <div class="list-toolbar">
      <a-segmented
        v-model:value="filter"
        :options="[
          { value: 'all', label: '全部' },
          { value: 'running', label: '进行中' },
          { value: 'waiting', label: '等待确认' },
          { value: 'ready', label: '已交付' },
        ]"
      />
      <div class="search-actions">
        <a-input
          v-model:value="query"
          placeholder="搜索项目、运行或状态…"
          aria-label="搜索项目和运行"
          allow-clear
          ><template #prefix><SearchOutlined aria-hidden="true" /></template></a-input
        ><a-button :loading="refreshing" aria-label="刷新项目和运行" @click="refresh"
          ><ReloadOutlined aria-hidden="true"
        /></a-button>
      </div>
    </div>
    <div v-if="view === 'projects' && !projectId && projects.length" class="project-grid">
      <article v-for="p in projects" :key="p.id" class="panel project-card">
        <div class="section-top">
          <div class="project-icon"><FolderOutlined aria-hidden="true" /></div>
          <a-tag :color="statusColor(latest(p.id)?.status)">{{
            statusLabel(latest(p.id)?.status)
          }}</a-tag>
        </div>
        <h2>{{ p.title }}</h2>
        <p>{{ latest(p.id)?.template || '从第一轮需求开始' }}</p>
        <p class="muted">项目 {{ shortId(p.id) }}</p>
        <div class="project-card-footer">
          <span
            >{{ state.runs.filter((r) => r.project_id === p.id).length }} 次最近运行 ·
            {{ formatDate(latest(p.id)?.updated_at || p.created_at) }}</span
          ><a-button
            type="text"
            :aria-label="'打开项目 ' + p.title"
            @click="emit('navigate', 'project/' + p.id)"
            ><ArrowRightOutlined aria-hidden="true"
          /></a-button>
        </div>
      </article>
    </div>
    <section class="panel run-list">
      <div class="panel-heading">
        <h2>{{ view === 'delivery' ? '交付与待确认产物' : '最近运行' }}</h2>
        <span class="muted">已读取 {{ listedRuns.length }} 条 · 匹配 {{ runs.length }} 条</span>
      </div>
      <div v-if="runs.length" class="table-scroll">
        <table>
          <thead>
            <tr>
              <th>项目 / 运行</th>
              <th>技术模板</th>
              <th>更新时间</th>
              <th>状态</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="run in runs" :key="run.id">
              <td>
                <strong>{{ projectName(run.project_id) }}</strong
                ><small>{{ shortId(run.id) }}</small>
              </td>
              <td>{{ run.template }}</td>
              <td>{{ formatDate(run.updated_at) }}</td>
              <td>
                <a-tag :color="statusColor(run.status)">{{ statusLabel(run.status) }}</a-tag>
              </td>
              <td>
                <a-button
                  type="link"
                  @click="
                    emit(
                      'navigate',
                      'run/' + run.id + '/' + (view === 'delivery' ? 'delivery' : 'conversation'),
                    )
                  "
                  >{{ ['READY', 'SOURCE_READY'].includes(run.status) ? '查看产物' : '继续' }}
                  <ArrowRightOutlined aria-hidden="true"
                /></a-button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <a-empty
        v-else
        :description="query ? '没有匹配的项目或运行' : '还没有符合条件的运行'"
        class="list-empty"
        ><a-button
          v-if="!query"
          @click="emit('navigate', projectId ? 'project/' + projectId + '/new' : 'home')"
          >开始一轮新需求</a-button
        ></a-empty
      >
      <a-button v-if="hasMore" :loading="loadingRuns" @click="loadRuns(true)"
        >加载更早的运行</a-button
      >
    </section>
    <p class="page-footnote">
      故障恢复保留原 run_id。新一轮按新需求从零生成，不会读取或修改上一轮产物。
    </p>
  </div>
</template>
