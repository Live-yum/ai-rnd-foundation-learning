# ui/tests/workflow.test.ts · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：Vue 3 / Ant Design本机操作台源码。** 这是操作台自有的源码或测试支持文件，按路径保留。测试使用合成数据和受控接口，不接触真实模型密钥。

**对应关系：** ui/src及锁文件 → npm ci/test/build → workbench/web → FastAPI本机页面；与生成产品的前端模板是两套不同界面。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `ui/tests/workflow.test.ts`；**本文件共有 1 段**。本段覆盖源文件 L1–L108。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`3438`。本段原文以LF换行结束。

<!-- learning-source: {"path": "ui/tests/workflow.test.ts", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "8ed5377d824664e6294a17192c7e2328be93961080f0daaf4b0761c0ad57b2c0"} -->
````typescript
// ui/tests/workflow.test.ts
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
````
