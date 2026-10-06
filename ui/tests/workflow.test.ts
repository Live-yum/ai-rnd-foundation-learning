import { mount, flushPromises } from '@vue/test-utils'
import { beforeAll, afterEach, expect, it, vi } from 'vitest'
import Antd from 'ant-design-vue'
import HomeView from '../src/components/HomeView.vue'
import ProjectsView from '../src/components/ProjectsView.vue'
import { state, lock } from '../src/state'
import * as apiModule from '../src/api'

beforeAll(() => {
  vi.stubGlobal(
    'matchMedia',
    vi
      .fn()
      .mockReturnValue({
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
})
afterEach(() => {
  lock()
  vi.restoreAllMocks()
})

it('retains the requirement and return target across model setup navigation', async () => {
  state.authenticated = true
  state.settings = { ready: false }
  const wrapper = mount(HomeView, {
    props: { projectId: 'older-project' },
    global: { plugins: [Antd] },
  })
  await wrapper.find('textarea').setValue('保留此完整需求')
  await wrapper.find('form').trigger('submit')
  expect(wrapper.emitted('navigate')?.[0]).toEqual(['settings'])
  expect(state.settingsReturn).toBe('project/older-project/new')
  wrapper.unmount()
  const returned = mount(HomeView, {
    props: { projectId: 'older-project' },
    global: { plugins: [Antd] },
  })
  expect((returned.find('textarea').element as HTMLTextAreaElement).value).toBe('保留此完整需求')
  returned.unmount()
})

it('reads older project history directly and requests the next server page', async () => {
  state.authenticated = true
  apiModule.setToken('test-token')
  state.runs = []
  const page = Array.from({ length: 100 }, (_, i) => ({
    id: 'run-' + i,
    project_id: 'old',
    status: 'READY',
    template: 'python-basic',
    auto_mode: false,
  }))
  const request = vi
    .spyOn(apiModule, 'api')
    .mockResolvedValueOnce(page)
    .mockResolvedValueOnce([{ ...page[0], id: 'oldest' }])
  const wrapper = mount(ProjectsView, {
    props: { projectId: 'old', view: 'projects' },
    global: { plugins: [Antd] },
  })
  await flushPromises()
  expect(request).toHaveBeenCalledWith('/projects/old/runs?limit=100&offset=0')
  expect(wrapper.findAll('tbody tr')).toHaveLength(100)
  await wrapper
    .findAll('button')
    .find((button) => button.text() === '加载更早的运行')!
    .trigger('click')
  await flushPromises()
  expect(request).toHaveBeenCalledWith('/projects/old/runs?limit=100&offset=100')
  expect(wrapper.findAll('tbody tr')).toHaveLength(101)
  wrapper.unmount()
})

it('queries extension scope and delivery states in the delivery center', async () => {
  state.authenticated = true
  apiModule.setToken('test-token')
  const request = vi
    .spyOn(apiModule, 'api')
    .mockResolvedValue([
      {
        id: 'extension',
        project_id: 'old',
        status: 'WAITING_EXTENSION_DELIVERY',
        template: 'python-basic',
        auto_mode: false,
      },
    ])
  const wrapper = mount(ProjectsView, { props: { view: 'delivery' }, global: { plugins: [Antd] } })
  await flushPromises()
  expect(request.mock.calls[0][0]).toContain('status=WAITING_EXTENSION_SCOPE')
  expect(request.mock.calls[0][0]).toContain('status=WAITING_EXTENSION_DELIVERY')
  expect(wrapper.findAll('tbody tr')).toHaveLength(1)
  wrapper.unmount()
})
