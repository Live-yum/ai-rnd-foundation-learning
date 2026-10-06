# ui/src/App.vue · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：Vue 3 / Ant Design本机操作台源码。** 组合本机连接、项目导航与页面路由；锁定时清空内存令牌与当前任务状态。

**对应关系：** ui/src及锁文件 → npm ci/test/build → workbench/web → FastAPI本机页面；与生成产品的前端模板是两套不同界面。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `ui/src/App.vue`；**本文件共有 1 段**。本段覆盖源文件 L1–L411。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`15183`。本段原文以LF换行结束。

<!-- learning-source: {"path": "ui/src/App.vue", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "1aa6a500ae2b2081ef263418ab6490b30bf0d3621936150048dde2b0b1a0a864"} -->
````vue
<!-- ui/src/App.vue -->
<script setup lang="ts">
import { computed, nextTick, onMounted, onBeforeUnmount, ref, watch } from 'vue'
import { Modal } from 'ant-design-vue'
import zhCN from 'ant-design-vue/es/locale/zh_CN'
import {
  AppstoreOutlined,
  ApartmentOutlined,
  FolderOutlined,
  HistoryOutlined,
  SettingOutlined,
  PlusOutlined,
  MenuOutlined,
  MessageOutlined,
  LockOutlined,
  SafetyCertificateOutlined,
  CloseOutlined,
} from '@ant-design/icons-vue'
import { connect, state, lock, openRun, closeRun, refreshLists } from './state'
import { shortId } from './presentation'
import HomeView from './components/HomeView.vue'
import ProjectsView from './components/ProjectsView.vue'
import RunView from './components/RunView.vue'
import SettingsView from './components/SettingsView.vue'
const hash = ref(location.hash.slice(1).replace(/^\//, '') || 'home'),
  authOpen = ref(false),
  mobileOpen = ref(false),
  token = ref(''),
  tokenInput = ref<any>(),
  settingsView = ref<any>(),
  authError = ref('')
const parts = computed(() => hash.value.split('/')),
  section = computed(() => parts.value[0]),
  runId = computed(() => (section.value === 'run' ? parts.value[1] || '' : '')),
  runView = computed(() => parts.value[2] || 'conversation')
const names: Record<string, string> = {
  home: '工作台',
  projects: '全部项目',
  history: '运行历史',
  delivery: '交付中心',
  settings: '模型与配置',
  project: '项目',
  run: '项目 / 对话工作区',
}
const navigation = [
  { id: 'home', name: '工作台', icon: AppstoreOutlined },
  { id: 'projects', name: '全部项目', icon: FolderOutlined },
  { id: 'history', name: '运行历史', icon: HistoryOutlined },
]
const lowerNavigation = [
  { id: 'delivery', name: '交付中心', icon: ApartmentOutlined },
  { id: 'settings', name: '模型与配置', icon: SettingOutlined },
]
const theme = {
  token: {
    colorPrimary: '#4359f5',
    colorInfo: '#4359f5',
    colorSuccess: '#21a482',
    colorWarning: '#cb902f',
    colorError: '#de6177',
    colorText: '#27364f',
    colorTextSecondary: '#5e708a',
    colorBorder: '#e0e7f2',
    colorBgContainer: '#ffffff',
    borderRadius: 9,
    fontFamily:
      'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif',
    fontSize: 14,
    controlHeight: 40,
  },
  components: {
    Button: { primaryShadow: 'none' },
    Card: { borderRadiusLG: 14 },
    Modal: { borderRadiusLG: 16 },
    Tag: { borderRadiusSM: 6 },
  },
}
let allowNavigation = false
function navigate(path: string) {
  const go = () => {
    mobileOpen.value = false
    if ((location.hash.slice(1).replace(/^\//, '') || 'home') === path) return
    allowNavigation = true
    location.hash = '/' + path
  }
  if (section.value === 'settings' && settingsView.value?.dirty)
    Modal.confirm({
      title: '离开并放弃未保存的配置？',
      content: '新输入的密钥也会从页面内存中清除。',
      okText: '离开',
      cancelText: '继续编辑',
      onOk: go,
    })
  else go()
}
function updateHash() {
  const destination = location.hash.slice(1).replace(/^\//, '') || 'home'
  if (
    !allowNavigation &&
    section.value === 'settings' &&
    destination !== 'settings' &&
    settingsView.value?.dirty
  ) {
    history.replaceState(null, '', '#/' + hash.value)
    Modal.confirm({
      title: '离开并放弃未保存的配置？',
      content: '新输入的密钥也会从页面内存中清除。',
      okText: '离开',
      cancelText: '继续编辑',
      onOk: () => {
        allowNavigation = true
        location.hash = '/' + destination
      },
    })
    return
  }
  allowNavigation = false
  hash.value = destination
  nextTick(() =>
    document.querySelector<HTMLElement>('#main-content')?.focus({ preventScroll: true }),
  )
}
let authTrigger: HTMLElement | null = null
function focusMain() {
  document.querySelector<HTMLElement>('#main-content')?.focus({ preventScroll: true })
}
function closeAuth() {
  token.value = ''
  const trigger = authTrigger
  if (trigger?.isConnected) trigger.focus()
}
function showAuth() {
  authTrigger = document.activeElement instanceof HTMLElement ? document.activeElement : null
  authError.value = ''
  authOpen.value = true
}
async function authorize() {
  if (!token.value.trim() || state.connecting) return
  try {
    await connect(token.value)
    token.value = ''
    authOpen.value = false
  } catch {
    authError.value = state.error
  }
}
function disconnect() {
  Modal.confirm({
    title: '锁定本地工作空间？',
    content: '访问令牌与当前页面数据会从内存中清除。后台任务会继续运行。',
    okText: '锁定',
    cancelText: '取消',
    onOk: () => {
      lock()
      navigate('home')
    },
  })
}
watch([runId, () => state.authenticated], async ([id, authenticated], [previous]) => {
  if (id && authenticated) {
    if (id !== previous || !state.run) await openRun(id)
  } else closeRun()
})
watch(section, () => {
  if (
    state.authenticated &&
    ['projects', 'history', 'delivery', 'project', 'settings'].includes(section.value)
  )
    void refreshLists()
})
function offline() {
  state.online = false
  state.notice = '网络离线，保留当前页面数据。恢复连接后再提交操作。'
}
function online() {
  if (state.notice.startsWith('网络离线')) state.notice = ''
  state.online = true
  if (runId.value && state.authenticated) void openRun(runId.value)
  else void refreshLists()
}
onMounted(() => {
  window.addEventListener('hashchange', updateHash)
  window.addEventListener('offline', offline)
  window.addEventListener('online', online)
  state.online = navigator.onLine
})
onBeforeUnmount(() => {
  closeRun()
  window.removeEventListener('hashchange', updateHash)
  window.removeEventListener('offline', offline)
  window.removeEventListener('online', online)
})
</script>
<template>
  <a-config-provider :theme="theme" :locale="zhCN">
    <div class="app-shell">
      <a class="skip-link" href="#main-content" @click.prevent="focusMain">跳到主要内容</a>
      <div v-if="mobileOpen" class="sidebar-overlay" @click="mobileOpen = false" />
      <aside class="sidebar" :class="{ open: mobileOpen }" aria-label="主导航">
        <button class="brand" @click="navigate('home')">
          <span class="brand-mark"><ApartmentOutlined aria-hidden="true" /></span
          ><strong>AI 研发平台</strong>
        </button>
        <a-button class="new-conversation" size="large" @click="navigate('home')"
          ><PlusOutlined aria-hidden="true" />新建对话</a-button
        >
        <nav class="main-nav">
          <button
            v-for="item in navigation"
            :key="item.id"
            :class="{ active: section === item.id }"
            :aria-current="section === item.id ? 'page' : undefined"
            @click="navigate(item.id)"
          >
            <component aria-hidden="true" :is="item.icon" /><span>{{ item.name }}</span>
          </button>
        </nav>
        <div class="sidebar-recents">
          <h3>最近项目</h3>
          <button
            v-for="project in state.authenticated ? state.projects.slice(0, 5) : []"
            :key="project.id"
            :class="{ selected: state.run?.project_id === project.id && section === 'run' }"
            @click="
              navigate(
                state.runs.find((r) => r.project_id === project.id)
                  ? 'run/' +
                      state.runs.find((r) => r.project_id === project.id)!.id +
                      '/conversation'
                  : 'project/' + project.id,
              )
            "
          >
            <span class="recent-dot" /><span>{{ project.title }}</span>
          </button>
          <p v-if="!state.projects.length" class="sidebar-empty">
            {{ state.authenticated ? '你的项目会出现在这里' : '连接后查看最近项目' }}
          </p>
        </div>
        <nav class="bottom-nav">
          <button
            v-for="item in lowerNavigation"
            :key="item.id"
            :class="{ active: section === item.id }"
            :aria-current="section === item.id ? 'page' : undefined"
            @click="navigate(item.id)"
          >
            <component aria-hidden="true" :is="item.icon" /><span>{{ item.name }}</span>
          </button>
        </nav>
        <button class="workspace-profile" @click="state.authenticated ? disconnect() : showAuth()">
          <span class="profile-avatar">我</span
          ><span
            >本地工作空间<small>{{
              state.authenticated ? '已连接 · 点击锁定' : 'LOCAL WORKSPACE'
            }}</small></span
          ><LockOutlined aria-hidden="true" v-if="state.authenticated" />
        </button>
      </aside>
      <div class="app-body">
        <header class="topbar">
          <button class="mobile-menu" aria-label="打开导航菜单" @click="mobileOpen = !mobileOpen">
            <MenuOutlined aria-hidden="true" />
          </button>
          <div class="breadcrumb">
            <span>工作空间</span><span>/</span><strong>{{ names[section] || '工作台' }}</strong>
          </div>
          <div class="topbar-status">
            <span
              class="status-dot"
              :class="state.authenticated && state.online ? 'online' : 'muted-dot'"
            /><span>{{
              state.authenticated
                ? state.online
                  ? '本地服务已连接'
                  : '本地服务离线'
                : '本地优先 · 安全连接'
            }}</span>
          </div>
          <a-button v-if="!state.authenticated" size="small" @click="showAuth"
            >连接本地服务</a-button
          >
          <a-button
            v-if="state.authenticated && !state.online"
            size="small"
            @click="runId ? openRun(runId) : refreshLists()"
            >重新连接</a-button
          >
          <a-tooltip v-if="state.authenticated" title="锁定并清除本页访问令牌"
            ><a-button type="text" aria-label="锁定工作空间" @click="disconnect"
              ><LockOutlined aria-hidden="true" /></a-button
          ></a-tooltip>
        </header>
        <main id="main-content" tabindex="-1">
          <div v-if="state.error && !authOpen" class="global-alert">
            <a-alert
              type="error"
              show-icon
              closable
              :message="state.error"
              @close="state.error = ''"
            />
          </div>
          <div v-if="state.notice" class="global-alert">
            <a-alert
              type="info"
              show-icon
              closable
              :message="state.notice"
              @close="state.notice = ''"
            />
          </div>
          <HomeView
            v-if="section === 'home' || (section === 'project' && parts[2] === 'new')"
            :project-id="section === 'project' ? parts[1] : undefined"
            @connect="showAuth"
            @navigate="navigate"
          />
          <template v-else-if="!state.authenticated"
            ><div class="page locked-page">
              <div class="sparkle-tile"><LockOutlined aria-hidden="true" /></div>
              <h1>连接你的本地工作空间</h1>
              <p>连接后才能读取项目、运行记录与模型配置。</p>
              <a-button type="primary" size="large" @click="showAuth">连接工作空间</a-button>
              <p class="field-hint">访问令牌仅保留在当前页面内存中，不写入浏览器存储。</p>
            </div></template
          >
          <ProjectsView
            v-else-if="['projects', 'history', 'delivery', 'project'].includes(section)"
            :view="section === 'project' ? 'projects' : section"
            :project-id="section === 'project' ? parts[1] : undefined"
            @navigate="navigate"
          />
          <RunView
            v-else-if="section === 'run'"
            :key="runId"
            :run-id="runId"
            :view="runView"
            @navigate="navigate"
          />
          <template v-else-if="section === 'settings'">
            <div v-if="state.settingsReturn" class="global-alert">
              <a-button @click="navigate(state.settingsReturn)">返回需求草稿</a-button>
            </div>
            <SettingsView ref="settingsView" />
          </template>
          <div v-else class="page">
            <a-empty description="没有这个页面"
              ><a-button @click="navigate('home')">返回工作台</a-button></a-empty
            >
          </div>
        </main>
      </div>
      <nav class="mobile-bottom-nav" aria-label="移动导航">
        <button :class="{ active: section === 'home' }" @click="navigate('home')">
          <AppstoreOutlined aria-hidden="true" /><span>工作台</span></button
        ><button
          :disabled="!runId"
          :class="{ active: section === 'run' && runView === 'conversation' }"
          @click="navigate('run/' + runId + '/conversation')"
        >
          <MessageOutlined aria-hidden="true" /><span>对话</span></button
        ><button
          :disabled="!runId"
          :class="{ active: runView === 'progress' && section === 'run' }"
          @click="navigate('run/' + runId + '/progress')"
        >
          <ApartmentOutlined aria-hidden="true" /><span>进度</span></button
        ><button :class="{ active: section === 'settings' }" @click="navigate('settings')">
          <SettingOutlined aria-hidden="true" /><span>配置</span>
        </button>
      </nav>
      <a-modal
        v-model:open="authOpen"
        title="连接本地工作空间"
        :footer="null"
        :mask-closable="!state.connecting"
        :closable="!state.connecting"
        :keyboard="!state.connecting"
        :after-close="closeAuth"
      >
        <form class="auth-form" @submit.prevent="authorize">
          <div class="auth-symbol"><SafetyCertificateOutlined aria-hidden="true" /></div>
          <p>在运行服务的本机终端执行 <code>uv run rnd token</code>，将访问令牌填入下方。</p>
          <label class="form-label" for="access-token">本机访问令牌</label
          ><a-input-password
            id="access-token"
            ref="tokenInput"
            v-model:value="token"
            :visibility-toggle="false"
            autocomplete="off"
            :disabled="state.connecting"
            placeholder="输入本机访问令牌"
          />
          <p class="field-hint">
            只保留在当前页面内存中。刷新或锁定后需要重新连接，不会放入 URL、localStorage 或
            sessionStorage。
          </p>
          <a-alert v-if="authError" type="error" show-icon :message="authError" /><a-button
            type="primary"
            html-type="submit"
            size="large"
            block
            :loading="state.connecting"
            :disabled="!token.trim()"
            >连接工作空间</a-button
          >
        </form>
      </a-modal>
    </div>
  </a-config-provider>
</template>
````
