# ui/tests/settings.test.ts · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：Vue 3 / Ant Design本机操作台源码。** 这是操作台自有的源码或测试支持文件，按路径保留。测试使用合成数据和受控接口，不接触真实模型密钥。

**对应关系：** ui/src及锁文件 → npm ci/test/build → workbench/web → FastAPI本机页面；与生成产品的前端模板是两套不同界面。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `ui/tests/settings.test.ts`；**本文件共有 1 段**。本段覆盖源文件 L1–L218。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`7797`。本段原文以LF换行结束。

<!-- learning-source: {"path": "ui/tests/settings.test.ts", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "7ebeac7c1706c37ef0e68a8447f5318776fa0b1665e77af6afb421972133a65f"} -->
````typescript
// ui/tests/settings.test.ts
import { mount, flushPromises } from '@vue/test-utils'
import { beforeAll, afterEach, describe, expect, it, vi } from 'vitest'
import Antd, { Modal } from 'ant-design-vue'
import SettingsView from '../src/components/SettingsView.vue'
import { state, lock } from '../src/state'
import * as apiModule from '../src/api'
beforeAll(() => {
  vi.stubGlobal(
    'matchMedia',
    vi.fn().mockReturnValue({
      matches: false,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
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
  Modal.destroyAll()
  lock()
  vi.restoreAllMocks()
})

function connectionSettings() {
  const profile = {
    base_url: 'https://saved.example.test/v1',
    model: 'saved-model',
    api_key: 'configured',
    provider: 'auto',
    output_mode: 'auto',
    max_output_tokens: 8000,
  }
  state.settings = {
    revision: 'saved-revision',
    default: profile,
    stages: { coding: { ...profile, effective: { ...profile, model: 'saved-coder' } } },
    model_review: false,
    ready: true,
    validation: [],
  }
  state.authenticated = true
  state.online = true
  apiModule.setToken('fixture-only-token')
}

function testButton(wrapper: ReturnType<typeof mount>) {
  return wrapper.findAll('button').find((button) => button.text().includes('测试连接'))!
}

describe('explicit saved-profile connection tests', () => {
  it('asks about real-call cost once and cancellation makes no request', async () => {
    connectionSettings()
    const request = vi.spyOn(apiModule, 'api')
    const confirm = vi
      .spyOn(Modal, 'confirm')
      .mockReturnValue({ destroy: vi.fn(), update: vi.fn() })
    const wrapper = mount(SettingsView, { global: { plugins: [Antd] } })
    await testButton(wrapper).trigger('click')
    await testButton(wrapper).trigger('click')
    expect(confirm).toHaveBeenCalledTimes(1)
    expect(confirm.mock.calls[0]![0].content).toContain('128')
    expect(confirm.mock.calls[0]![0].content).toContain('可能按服务商价格计费')
    expect(request).not.toHaveBeenCalled()
    await confirm.mock.calls[0]![0].onCancel?.()
    expect(request).not.toHaveBeenCalled()
    wrapper.unmount()
  })

  it('tests the saved effective stage and blocks edits, duplicate clicks and automatic retries', async () => {
    connectionSettings()
    let resolve!: (value: unknown) => void
    const request = vi.spyOn(apiModule, 'api').mockImplementation(
      () =>
        new Promise((done) => {
          resolve = done
        }),
    )
    const confirm = vi
      .spyOn(Modal, 'confirm')
      .mockReturnValue({ destroy: vi.fn(), update: vi.fn() })
    const wrapper = mount(SettingsView, { global: { plugins: [Antd] } })
    await wrapper.findAll('[role="tab"]')[3]!.trigger('click')
    await testButton(wrapper).trigger('click')
    expect(confirm.mock.calls[0]![0].content).toContain('saved-coder')
    const pending = confirm.mock.calls[0]![0].onOk?.()
    await flushPromises()
    await testButton(wrapper).trigger('click')
    expect(request).toHaveBeenCalledTimes(1)
    expect(request.mock.calls[0]![0]).toBe('/settings/models/test')
    expect(request.mock.calls[0]![1]?.body).toMatchObject({
      stage: 'coding',
      expected_revision: 'saved-revision',
      confirm_cost: true,
    })
    expect(JSON.stringify(request.mock.calls[0]![1]?.body)).not.toContain('api_key')
    expect(wrapper.find('#model-name').attributes('disabled')).toBeDefined()
    expect(wrapper.text()).toContain('正在请求真实模型响应')
    resolve({
      ok: false,
      stage: 'coding',
      revision: 'saved-revision',
      phase: 'request',
      code: 'authentication_failed',
      message: '请检查 API Key',
      trace_id: 'trace-123',
      retryable: false,
      attempts: 1,
      elapsed_ms: 42,
    })
    await pending
    await flushPromises()
    expect(wrapper.text()).toContain('authentication_failed')
    expect(wrapper.text()).toContain('trace-123')
    expect(wrapper.text()).toContain('请求次数：1')
    expect(request).toHaveBeenCalledTimes(1)
    wrapper.unmount()
  })

  it('disables testing unsaved edits and clears success when the revision changes', async () => {
    connectionSettings()
    vi.spyOn(apiModule, 'api').mockResolvedValue({
      ok: true,
      stage: 'default',
      revision: 'saved-revision',
      phase: 'completed',
      code: 'connected',
      message: '连接成功',
      trace_id: 'trace-success',
      retryable: false,
      attempts: 1,
      elapsed_ms: 2,
    })
    const confirm = vi
      .spyOn(Modal, 'confirm')
      .mockReturnValue({ destroy: vi.fn(), update: vi.fn() })
    const wrapper = mount(SettingsView, { global: { plugins: [Antd] } })
    await wrapper.find('#model-name').setValue('unsaved-model')
    expect(testButton(wrapper).attributes('disabled')).toBeDefined()
    await wrapper.find('#model-name').setValue('saved-model')
    await testButton(wrapper).trigger('click')
    await confirm.mock.calls[0]![0].onOk?.()
    await flushPromises()
    expect(wrapper.text()).toContain('当前连接测试通过')
    state.settings = { ...state.settings, revision: 'new-revision' }
    await flushPromises()
    expect(wrapper.text()).not.toContain('当前连接测试通过')
    expect(wrapper.text()).not.toContain('trace-success')
    wrapper.unmount()
  })

  it('ignores a late response after unmount and destroys its pending dialog', async () => {
    connectionSettings()
    let resolve!: (value: unknown) => void
    const request = vi.spyOn(apiModule, 'api').mockImplementation(
      () =>
        new Promise((done) => {
          resolve = done
        }),
    )
    const destroy = vi.fn()
    const confirm = vi.spyOn(Modal, 'confirm').mockReturnValue({ destroy, update: vi.fn() })
    const wrapper = mount(SettingsView, { global: { plugins: [Antd] } })
    await testButton(wrapper).trigger('click')
    const pending = confirm.mock.calls[0]![0].onOk?.()
    wrapper.unmount()
    expect(destroy).toHaveBeenCalledTimes(1)
    expect(request.mock.calls[0]![1]?.signal?.aborted).toBe(true)
    resolve({ ok: true, revision: 'saved-revision', stage: 'default' })
    await pending
    expect(request).toHaveBeenCalledTimes(1)
  })
})
describe('model settings save baseline', () => {
  it('becomes clean immediately after saving unchanged normalized form fields', async () => {
    const profile = {
      base_url: 'https://api.example.test/v1',
      model: 'before',
      api_key: 'configured',
      provider: 'auto',
      output_mode: 'auto',
      max_output_tokens: null,
    }
    state.settings = {
      revision: 'rev-1',
      default: profile,
      stages: {},
      model_review: false,
      ready: true,
      validation: [],
    }
    state.authenticated = true
    apiModule.setToken('fixture-only-token')
    const saved = { ...state.settings, revision: 'rev-2', default: { ...profile, model: 'after' } }
    vi.spyOn(apiModule, 'api').mockImplementation(async (path: string, options: any = {}) => {
      if (path === '/settings/models') return saved as any
      return [] as any
    })
    const wrapper = mount(SettingsView, { global: { plugins: [Antd] } })
    expect((wrapper.vm as any).dirty).toBe(false)
    await wrapper.find('#model-name').setValue('after')
    expect((wrapper.vm as any).dirty).toBe(true)
    await wrapper.find('form').trigger('submit')
    await flushPromises()
    expect(wrapper.text()).toContain('配置已保存 · 仅完成格式校验 · 未测试连接')
    expect((wrapper.vm as any).dirty).toBe(false)
    expect(wrapper.text()).not.toContain('未保存')
    wrapper.unmount()
  })
})
````
