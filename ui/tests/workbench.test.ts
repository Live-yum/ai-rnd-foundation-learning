import { mount, flushPromises } from '@vue/test-utils'
import { beforeAll, beforeEach, afterEach, describe, expect, it, vi } from 'vitest'
import Antd from 'ant-design-vue'
import HomeView from '../src/components/HomeView.vue'
import ProjectsView from '../src/components/ProjectsView.vue'
import RunView from '../src/components/RunView.vue'
import { lock, state } from '../src/state'
import * as apiModule from '../src/api'
import type { BatchReceipt, Run } from '../src/types'

beforeAll(() => {
  vi.stubGlobal(
    'matchMedia',
    vi.fn().mockReturnValue({
      matches: false,
      addListener() {},
      removeListener() {},
      addEventListener() {},
      removeEventListener() {},
    }),
  )
  vi.stubGlobal(
    'ResizeObserver',
    class {
      observe() {}
      disconnect() {}
      unobserve() {}
    },
  )
  Element.prototype.scrollIntoView = vi.fn()
})
beforeEach(() => {
  lock()
  apiModule.setToken('test-token')
  Object.assign(state, {
    authenticated: true,
    online: true,
    settings: { ready: true },
    catalog: [
      {
        template: 'python-basic',
        name: 'Python 全栈模板',
        backend: 'fastapi',
        frontends: ['vue'],
        databases: ['sqlite'],
        features: ['CRUD', '权限'],
      },
      {
        template: 'fastapiadmin',
        name: 'FastAPIAdmin',
        backend: 'fastapi',
        frontends: ['vue3'],
        databases: ['postgresql'],
        features: ['权限', '管理页面'],
      },
    ],
  })
})
afterEach(() => {
  lock()
  vi.restoreAllMocks()
})
const options = { global: { plugins: [Antd] } }
const receipt: BatchReceipt = {
  items: [
    { project_id: 'project-a', title: '库存项目', run_id: 'run-a', status: 'QUEUED' },
    { project_id: 'project-b', title: '工单项目', run_id: 'run-b', status: 'QUEUED' },
  ],
}
function batchDrafts() {
  state.batchMode = true
  state.batchDrafts = [
    { id: 'a', title: ' 库存项目 ', requirement: ' 管理商品出入库 ' },
    { id: 'b', title: '工单项目', requirement: '管理客户工单' },
  ]
}

describe('template creation and atomic batch submission', () => {
  it('keeps the existing single-project protocol and uses Enter for multiline requirements', async () => {
    const request = vi.spyOn(apiModule, 'api').mockImplementation(async (path, input) => {
      if (path === '/projects' && input?.method === 'POST') return { id: 'single-project' }
      if (path === '/projects/single-project/runs') return { run_id: 'single-run' }
      return []
    })
    const wrapper = mount(HomeView, options)
    await wrapper.find('#new-project-title').setValue('库存项目')
    await wrapper.find('textarea').setValue('登记出库\n库存不得为负数')
    await wrapper.find('textarea').trigger('keydown', { key: 'Enter' })
    expect(request).not.toHaveBeenCalled()
    await wrapper.find('form').trigger('submit')
    await flushPromises()
    expect(request).toHaveBeenCalledWith(
      '/projects',
      expect.objectContaining({
        method: 'POST',
        body: { title: '库存项目' },
        key: expect.any(String),
      }),
    )
    expect(request).toHaveBeenCalledWith(
      '/projects/single-project/runs',
      expect.objectContaining({
        method: 'POST',
        body: {
          requirement: '登记出库\n库存不得为负数',
          template: 'python-basic',
          selection: {
            template: 'python-basic',
            backend: 'fastapi',
            frontend: 'vue',
            database: 'sqlite',
          },
          intelligent: false,
          allow_custom_extensions: false,
        },
      }),
    )
    expect(wrapper.emitted('navigate')).toContainEqual(['run/single-run/conversation'])
    wrapper.unmount()
  })

  it('submits distinct projects once, with shared selection, and opens each returned run', async () => {
    batchDrafts()
    const request = vi
      .spyOn(apiModule, 'api')
      .mockImplementation(async (path) => (path === '/batches' ? receipt : []))
    const wrapper = mount(HomeView, options)
    await wrapper.find('input[value="fastapiadmin"]').setValue(true)
    await wrapper.find('.execution-options input[type="checkbox"]').setValue(true)
    await wrapper.find('form').trigger('submit')
    await flushPromises()
    const batchCalls = request.mock.calls.filter(([path]) => path === '/batches')
    expect(batchCalls).toHaveLength(1)
    expect(batchCalls[0][1]).toMatchObject({
      method: 'POST',
      key: expect.any(String),
      body: {
        items: [
          {
            title: '库存项目',
            requirement: '管理商品出入库',
            template: 'fastapiadmin',
            selection: {
              template: 'fastapiadmin',
              backend: 'fastapi',
              frontend: 'vue3',
              database: 'postgresql',
            },
            intelligent: true,
            allow_custom_extensions: false,
          },
          {
            title: '工单项目',
            requirement: '管理客户工单',
            template: 'fastapiadmin',
            intelligent: true,
          },
        ],
      },
    })
    expect(request.mock.calls.filter(([, input]) => input?.method === 'POST')).toHaveLength(1)
    expect(wrapper.findAll('.batch-results tbody tr')).toHaveLength(2)
    await wrapper.find('[aria-label="打开运行：工单项目"]').trigger('click')
    expect(wrapper.emitted('navigate')).toContainEqual(['run/run-b/conversation'])
    expect(state.batchDrafts).toEqual([])
    wrapper.unmount()
  })

  it('limits batches to ten entries and blocks a batch with any empty requirement', async () => {
    const request = vi.spyOn(apiModule, 'api')
    const wrapper = mount(HomeView, options)
    await wrapper
      .findAll('.ant-segmented-item')
      .find((item) => item.text() === '批量项目')!
      .find('input')
      .setValue(true)
    for (let index = 0; index < 12; index++) await wrapper.find('.add-batch').trigger('click')
    expect(state.batchDrafts).toHaveLength(10)
    expect(wrapper.find('.add-batch').attributes('disabled')).toBeDefined()
    state.batchDrafts[0].requirement = '只有第一项填写了需求'
    await wrapper.find('form').trigger('submit')
    expect(request).not.toHaveBeenCalled()
    expect(wrapper.find('button[type="submit"]').attributes('disabled')).toBeDefined()
    wrapper.unmount()
  })

  it('preserves drafts and the idempotency key after an uncertain response and prevents double submit', async () => {
    batchDrafts()
    let rejectFirst!: (error: Error) => void
    let attempts = 0
    const request = vi.spyOn(apiModule, 'api').mockImplementation(async (path) => {
      if (path !== '/batches') return []
      if (++attempts === 1)
        return new Promise((_, reject) => {
          rejectFirst = reject
        })
      return receipt
    })
    const wrapper = mount(HomeView, options)
    await wrapper.find('form').trigger('submit')
    await wrapper.find('form').trigger('submit')
    expect(attempts).toBe(1)
    rejectFirst(new Error('连接中断'))
    await flushPromises()
    expect(wrapper.text()).toContain('草稿已保留')
    expect(state.batchDrafts[0].requirement).toBe(' 管理商品出入库 ')
    state.online = true
    await wrapper.find('form').trigger('submit')
    await flushPromises()
    const batchCalls = request.mock.calls.filter(([path]) => path === '/batches')
    expect(batchCalls).toHaveLength(2)
    expect(batchCalls[0][1]?.key).toBe(batchCalls[1][1]?.key)
    expect(batchCalls[0][1]?.body).toEqual(batchCalls[1][1]?.body)
    wrapper.unmount()
  })

  it('does not restore private batch results after the workspace is locked', async () => {
    batchDrafts()
    let resolve!: (value: BatchReceipt) => void
    const request = vi.spyOn(apiModule, 'api').mockReturnValue(
      new Promise((accept) => {
        resolve = accept
      }),
    )
    const wrapper = mount(HomeView, options)
    await wrapper.find('form').trigger('submit')
    lock()
    resolve(receipt)
    await flushPromises()
    expect(state.batchRuns).toEqual([])
    expect(state.projects).toEqual([])
    expect(state.runs).toEqual([])
    expect(request).toHaveBeenCalledOnce()
    wrapper.unmount()
  })

  it('preserves template settings and batch drafts when returning from model configuration', async () => {
    batchDrafts()
    state.settings = { ready: false }
    const wrapper = mount(HomeView, options)
    await wrapper.find('input[value="fastapiadmin"]').setValue(true)
    await wrapper.find('.execution-options input[type="checkbox"]').setValue(true)
    await wrapper.find('form').trigger('submit')
    expect(wrapper.emitted('navigate')).toContainEqual(['settings'])
    wrapper.unmount()
    const returned = mount(HomeView, options)
    expect((returned.find('input[value="fastapiadmin"]').element as HTMLInputElement).checked).toBe(
      true,
    )
    expect((returned.find('#batch-title-a').element as HTMLInputElement).value).toBe(' 库存项目 ')
    expect(state.creation.intelligent).toBe(true)
    expect(state.creation.database).toBe('postgresql')
    returned.unmount()
  })

  it('shows the selected server-provided coding standard as escaped, read-only text', async () => {
    state.catalog[0].coding_standard = {
      path: 'templates/standards/python-basic.md',
      summary: '保留模板结构，先确认验收合同',
      sha256: 'a'.repeat(64),
      content: '# 编码规范\n<script>unsafe()</script>\n使用真实测试。',
    }
    const wrapper = mount(HomeView, options)
    await wrapper.find('.selection-details .ant-collapse-header').trigger('click')
    expect(wrapper.find('.coding-standard').text()).toContain('templates/standards/python-basic.md')
    expect(wrapper.find('.coding-standard pre').text()).toContain('<script>unsafe()</script>')
    expect(wrapper.find('.coding-standard script').exists()).toBe(false)
    wrapper.unmount()
  })
})

it('shows loading explicitly and filters failed and budget-paused runs using readable status', async () => {
  let resolve!: (value: Run[]) => void
  vi.spyOn(apiModule, 'api').mockReturnValue(
    new Promise((accept) => {
      resolve = accept
    }),
  )
  const wrapper = mount(ProjectsView, { ...options, props: { view: 'history' } })
  expect(wrapper.find('.ant-skeleton').exists()).toBe(true)
  expect(wrapper.text()).not.toContain('还没有运行记录')
  resolve(
    ['FAILED', 'PAUSED_LIMIT', 'READY'].map((status) => ({
      id: status,
      project_id: status,
      status,
      template: 'python-basic',
      auto_mode: false,
    })),
  )
  await flushPromises()
  await wrapper
    .findAll('.filter-tabs button')
    .find((item) => item.text().startsWith('失败'))!
    .trigger('click')
  expect(wrapper.findAll('tbody tr')).toHaveLength(1)
  expect(wrapper.find('tbody').text()).toContain('运行失败')
  await wrapper
    .findAll('.filter-tabs button')
    .find((item) => item.text().startsWith('待处理'))!
    .trigger('click')
  expect(wrapper.findAll('tbody tr')).toHaveLength(1)
  expect(wrapper.find('tbody').text()).toContain('预算暂停')
  await wrapper
    .findAll('.filter-tabs button')
    .find((item) => item.text().startsWith('全部'))!
    .trigger('click')
  await wrapper.find('[aria-label="搜索项目和运行"]').setValue('预算暂停')
  expect(wrapper.findAll('tbody tr')).toHaveLength(1)
  wrapper.unmount()
})

it('filters actual events by the selected stage and keeps raw data collapsed by default', async () => {
  state.run = {
    id: 'run',
    project_id: 'project',
    template: 'python-basic',
    status: 'RUNNING',
    current_step: 'code',
    auto_mode: false,
  }
  state.events = [
    { id: 1, kind: 'stage', data: { name: 'plan', phase: 'completed' } },
    { id: 2, kind: 'stage', data: { name: 'code', phase: 'started' } },
    { id: 3, kind: 'assistant_start', data: { stage: 'code', message_id: 'code-response' } },
    { id: 4, kind: 'assistant_delta', data: { stage: 'code', text: 'partial response' } },
  ]
  const wrapper = mount(RunView, { ...options, props: { runId: 'run', view: 'progress' } })
  expect(wrapper.findAll('.event-row')).toHaveLength(3)
  expect(wrapper.find('.event-row .data-document').exists()).toBe(false)
  await wrapper
    .findAll('.milestone')
    .find((item) => item.text().includes('生成与编码'))!
    .trigger('click')
  expect(wrapper.findAll('.event-row')).toHaveLength(2)
  expect(wrapper.find('.event-panel').text()).not.toContain('plan ·')
  expect(wrapper.find('.stat-grid').text()).toContain('1 / 6')
  wrapper.unmount()
})
