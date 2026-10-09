# ui/src/state.ts · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：Vue 3 / Ant Design本机操作台源码。** 集中管理任务快照、事件游标、当前订阅与错误。切换运行先abort旧订阅并增加代次，迟到请求不得覆盖新任务；重连用游标去重，不重新发起模型生成。

**对应关系：** ui/src及锁文件 → npm ci/test/build → workbench/web → FastAPI本机页面；与生成产品的前端模板是两套不同界面。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**带着一个具体问题阅读：** 快速打开运行A再打开B时，即使A的请求最后才返回，也不能把A消息写到B。openRun先关闭旧订阅并递增runGeneration；回调核对代次后才更新。重连只接受id大于当前cursor的事件，因此同一已提交delta不会再追加一次。

**创建路径：** `ui/src/state.ts`；**本文件共有 1 段**。本段覆盖源文件 L1–L327。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`10078`。本段原文以LF换行结束。

<!-- learning-source: {"path": "ui/src/state.ts", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "0f25268bee022a1744e190fccf3f9d063443c3980661f8bb54dc4cdd32361010"} -->
````typescript
// ui/src/state.ts
import { reactive } from 'vue'
import { api, ApiError, errorText, hasToken, isAbort, readStream, setToken } from './api'
import { applyMessageEvent, gateIdentity } from './presentation'
import type {
  CatalogEntry,
  ChatMessage,
  Project,
  ProjectDraft,
  Run,
  RunEvent,
  RecordData,
} from './types'
const emptyCreation = () => ({
  template: '',
  frontend: '',
  database: '',
  intelligent: false,
  allowCustomExtensions: false,
})
export const state = reactive({
  authenticated: false,
  connecting: false,
  online: true,
  loading: false,
  busy: false,
  notice: '',
  error: '',
  catalog: [] as CatalogEntry[],
  models: [] as RecordData[],
  settings: null as RecordData | null,
  projects: [] as Project[],
  runs: [] as Run[],
  run: null as Run | null,
  messages: [] as ChatMessage[],
  events: [] as RunEvent[],
  report: {} as RecordData,
  usedModels: [] as RecordData[],
  stream: 'idle',
  lastSync: '',
  cursor: 0,
  stale: false,
  homeDrafts: {} as Record<string, string>,
  homeTitles: {} as Record<string, string>,
  creation: emptyCreation(),
  batchMode: false,
  batchDrafts: [] as ProjectDraft[],
  batchRuns: [] as Run[],
  settingsReturn: '',
})
let runController: AbortController | undefined,
  runGeneration = 0,
  refreshTimer: ReturnType<typeof setTimeout> | undefined
let authGeneration = 0
export function sessionIdentity() {
  return authGeneration
}
export function isSessionActive(identity: number) {
  return identity === authGeneration && state.authenticated && hasToken()
}
const mutationKeys = new Map<string, string>()
export function mutationKey(fingerprint: string) {
  if (!mutationKeys.has(fingerprint)) mutationKeys.set(fingerprint, crypto.randomUUID())
  return mutationKeys.get(fingerprint)!
}
export function clearMutationKey(fingerprint: string) {
  mutationKeys.delete(fingerprint)
}
async function readModelConfig(generation = authGeneration) {
  const results = await Promise.allSettled([api('/models'), api('/settings/models')])
  if (!isSessionActive(generation)) return
  state.models = results[0].status === 'fulfilled' ? results[0].value : []
  state.settings = results[1].status === 'fulfilled' ? results[1].value : null
  const failure = results.find((r) => r.status === 'rejected')
  if (failure && failure.status === 'rejected')
    state.notice =
      '模型配置暂时无法读取：' +
      errorText(failure.reason) +
      '。已有项目仍可查看，新模型工作已禁用。'
}
export async function connect(token: string) {
  if (state.connecting) return
  const generation = ++authGeneration
  state.connecting = true
  state.error = ''
  setToken(token)
  try {
    const [catalog, projects, runs] = await Promise.all([
      api('/catalog'),
      api('/projects'),
      api('/runs'),
    ])
    if (generation !== authGeneration) return
    Object.assign(state, { catalog, projects, runs, authenticated: true, online: true })
    await readModelConfig(generation)
    if (!isSessionActive(generation)) return
    state.lastSync = new Date().toISOString()
  } catch (error) {
    if (generation !== authGeneration) return
    setToken('')
    state.authenticated = false
    state.error = errorText(error)
    state.online = error instanceof ApiError
    throw error
  } finally {
    if (generation === authGeneration) state.connecting = false
  }
}
export function closeRun() {
  runGeneration++
  runController?.abort()
  runController = undefined
  clearTimeout(refreshTimer)
  state.stream = 'idle'
}
export function lock() {
  authGeneration++
  closeRun()
  setToken('')
  mutationKeys.clear()
  Object.assign(state, {
    authenticated: false,
    connecting: false,
    loading: false,
    settings: null,
    catalog: [],
    models: [],
    projects: [],
    runs: [],
    run: null,
    messages: [],
    events: [],
    report: {},
    usedModels: [],
    error: '',
    notice: '',
    cursor: 0,
    stale: false,
    homeDrafts: {},
    homeTitles: {},
    batchMode: false,
    batchDrafts: [],
    batchRuns: [],
    settingsReturn: '',
  })
  Object.assign(state.creation, emptyCreation())
}
export async function refreshLists(options: { models?: boolean } = {}) {
  const generation = authGeneration
  if (!isSessionActive(generation)) return
  try {
    const [projects, runs] = await Promise.all([api('/projects'), api('/runs')])
    if (!isSessionActive(generation)) return
    Object.assign(state, { projects, runs, online: true })
    state.batchRuns = state.batchRuns.map((saved) => ({
      ...saved,
      ...runs.find((run: Run) => run.id === saved.id),
    }))
    if (options.models !== false) await readModelConfig(generation)
    if (!isSessionActive(generation)) return
    state.lastSync = new Date().toISOString()
  } catch (error) {
    if (isSessionActive(generation)) reportError(error)
  }
}
export function reportError(error: unknown) {
  if (isAbort(error)) return
  state.error = errorText(error)
  if (!(error instanceof ApiError)) state.online = false
  if (error instanceof ApiError && error.status === 401) {
    const message = state.error
    lock()
    state.error = message
  }
}
function updateRun(next: Run) {
  if (
    state.run?.id === next.id &&
    gateIdentity(state.run.pending) !== gateIdentity(next.pending) &&
    state.run.pending
  )
    state.stale = true
  state.run = next
  const i = state.runs.findIndex((r) => r.id === next.id)
  if (i >= 0) state.runs[i] = { ...state.runs[i], ...next }
  const batchIndex = state.batchRuns.findIndex((r) => r.id === next.id)
  if (batchIndex >= 0) state.batchRuns[batchIndex] = { ...state.batchRuns[batchIndex], ...next }
}
export async function refreshRun() {
  const id = state.run?.id,
    generation = runGeneration
  if (!id || !runController) return
  const [run, report, usedModels] = await Promise.all([
    api<Run>(`/runs/${id}`, { signal: runController.signal }),
    api(`/runs/${id}/report`, { signal: runController.signal }),
    api(`/runs/${id}/models`, { signal: runController.signal }),
  ])
  if (generation !== runGeneration) return
  updateRun(run)
  state.report = report
  state.usedModels = usedModels
  state.online = true
  state.lastSync = new Date().toISOString()
}
function requestRefresh() {
  clearTimeout(refreshTimer)
  refreshTimer = setTimeout(() => refreshRun().catch(reportError), 120)
}
export async function openRun(id: string) {
  closeRun()
  const generation = runGeneration,
    controller = new AbortController()
  runController = controller
  Object.assign(state, {
    loading: true,
    error: '',
    run: null,
    messages: [],
    events: [],
    report: {},
    usedModels: [],
    cursor: 0,
    stale: false,
    stream: 'connecting',
  })
  try {
    const [run, transcript, report, usedModels] = await Promise.all([
      api<Run>(`/runs/${id}`, { signal: controller.signal }),
      api(`/runs/${id}/transcript`, { signal: controller.signal }),
      api(`/runs/${id}/report`, { signal: controller.signal }),
      api(`/runs/${id}/models`, { signal: controller.signal }),
    ])
    if (generation !== runGeneration) return
    state.run = run
    state.messages = transcript.messages || []
    state.cursor = Number(transcript.cursor || transcript.latest_cursor || 0)
    state.report = report
    state.usedModels = usedModels
    state.lastSync = new Date().toISOString()
    state.online = true
    // Historical evidence is separate from the transcript snapshot and never reapplies old text deltas.
    let after = 0
    const history: RunEvent[] = []
    for (;;) {
      const batch = await api<RunEvent[]>(`/runs/${id}/events?after=${after}`, {
        signal: controller.signal,
      })
      if (generation !== runGeneration) return
      history.push(...batch)
      if (batch.length < 200) break
      after = batch[batch.length - 1].id
    }
    state.events = history
    void followStream(id, controller, generation)
  } catch (error) {
    if (generation === runGeneration) {
      reportError(error)
      state.stream = 'offline'
    }
  } finally {
    if (generation === runGeneration) state.loading = false
  }
}
function delay(ms: number, signal: AbortSignal) {
  return new Promise<void>((resolve) => {
    const timer = setTimeout(resolve, ms)
    signal.addEventListener(
      'abort',
      () => {
        clearTimeout(timer)
        resolve()
      },
      { once: true },
    )
  })
}
async function followStream(id: string, controller: AbortController, generation: number) {
  let failures = 0
  while (!controller.signal.aborted && generation === runGeneration) {
    try {
      const result = await readStream(
        id,
        state.cursor,
        controller.signal,
        (event) => {
          if (generation !== runGeneration || event.id <= state.cursor) return
          state.cursor = event.id
          const exists = state.events.some((e) => e.id === event.id)
          if (!exists) state.events.push(event)
          applyMessageEvent(state.messages, event)
          state.lastSync = new Date().toISOString()
          if (
            !event.kind.startsWith('assistant_') ||
            ['assistant_completed', 'assistant_failed'].includes(event.kind)
          )
            requestRefresh()
        },
        () => {
          if (generation !== runGeneration) return
          state.stream = 'connected'
          state.online = true
          failures = 0
          requestRefresh()
        },
      )
      if (controller.signal.aborted) return
      if (result.idle) {
        state.stream = 'connected'
        await delay(3000, controller.signal)
        continue
      }
    } catch (error) {
      if (controller.signal.aborted || isAbort(error)) return
      if (error instanceof ApiError && [401, 404].includes(error.status)) {
        reportError(error)
        state.stream = 'offline'
        return
      }
    }
    state.stream = 'reconnecting'
    state.online = false
    failures++
    await delay(Math.min(1000 * 2 ** Math.min(failures - 1, 4), 15000), controller.signal)
  }
}
export function acknowledgeReview() {
  state.stale = false
}
````
