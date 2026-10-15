# ui/tests/settings.test.ts · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：Vue 3 / Ant Design本机操作台源码。** 这是操作台自有的源码或测试支持文件，按路径保留。测试使用合成数据和受控接口，不接触真实模型密钥。

**对应关系：** ui/src及锁文件 → npm ci/test/build → workbench/web → FastAPI本机页面；与生成产品的前端模板是两套不同界面。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `ui/tests/settings.test.ts`；**本文件共有 1 段**。本段覆盖源文件 L1–L454。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`18634`。本段原文以LF换行结束。

<!-- learning-source: {"path": "ui/tests/settings.test.ts", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "63dcb676223ab448784e34ddb96904bf7cdad8f34b56e78cc8d8dde29850b407"} -->
````typescript
// ui/tests/settings.test.ts
import { mount, flushPromises } from '@vue/test-utils'
import { beforeAll, afterEach, describe, expect, it, vi } from 'vitest'
import { Modal } from 'ant-design-vue'
import { installUiComponents } from '../src/ui-components'
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
    const wrapper = mount(SettingsView, { global: { plugins: [installUiComponents] } })
    expect(testButton(wrapper).attributes('title')).toContain('可能产生费用')
    expect(wrapper.findComponent({ name: 'ATooltip' }).exists()).toBe(false)
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
    const wrapper = mount(SettingsView, { global: { plugins: [installUiComponents] } })
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
    const wrapper = mount(SettingsView, { global: { plugins: [installUiComponents] } })
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
    const wrapper = mount(SettingsView, { global: { plugins: [installUiComponents] } })
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
    const wrapper = mount(SettingsView, { global: { plugins: [installUiComponents] } })
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

it('initializes settings arriving after the view mounts and preserves unsaved edits', async () => {
  state.settings = null
  const wrapper = mount(SettingsView, { global: { plugins: [installUiComponents] } })
  connectionSettings()
  await flushPromises()
  expect((wrapper.find('#model-name').element as HTMLInputElement).value).toBe('saved-model')
  expect((wrapper.vm as any).dirty).toBe(false)
  await wrapper.find('#model-name').setValue('unsaved-model')
  state.settings = { ...state.settings!, revision: 'newer-revision' }
  await flushPromises()
  expect((wrapper.find('#model-name').element as HTMLInputElement).value).toBe('unsaved-model')
  wrapper.unmount()
})

function saveButton(wrapper: ReturnType<typeof mount>) {
  return wrapper.findAll('button').find((button) => button.text().includes('保存配置'))!
}
function discoverButton(wrapper: ReturnType<typeof mount>) {
  return wrapper.findAll('button').find((button) => button.text().includes('查询模型列表'))!
}
async function replaceKey(wrapper: ReturnType<typeof mount>, key = 'fixture-new-key') {
  wrapper
    .findAllComponents({ name: 'ASelect' })
    .find((c) => c.props('id') === 'key-action')!
    .vm.$emit('update:value', 'replace')
  await flushPromises()
  await wrapper.find('#model-key').setValue(key)
}

it('blocks editing until initial settings arrive and then enables a complete first-time save', async () => {
  state.authenticated = true
  state.online = true
  state.settings = null
  apiModule.setToken('fixture-only-token')
  const request = vi.spyOn(apiModule, 'api').mockResolvedValue([])
  const wrapper = mount(SettingsView, { global: { plugins: [installUiComponents] } })
  expect(wrapper.find('#model-url').attributes('disabled')).toBeDefined()
  expect(wrapper.text()).toContain('尚未读取配置')
  state.settings = {
    revision: '0',
    default: { base_url: '', model: '', api_key: 'missing' },
    stages: {},
    ready: false,
    validation: [],
    model_review: false,
  }
  await flushPromises()
  await wrapper.find('#model-url').setValue('https://fixture.example/v1')
  await wrapper.find('#model-name').setValue('gpt-6-luna')
  expect(saveButton(wrapper).attributes('disabled')).toBeDefined()
  await replaceKey(wrapper)
  await wrapper.find('#model-max-tokens').setValue('25400')
  expect(wrapper.text()).toContain('新密钥待保存')
  expect(wrapper.text()).not.toContain('服务地址已改变，请选择替换并填写新地址专用的 API Key')
  expect(saveButton(wrapper).attributes('disabled')).toBeUndefined()
  expect(testButton(wrapper).attributes('disabled')).toBeDefined()
  request.mockImplementation(async (path: string, options: any = {}) => {
    if (path === '/settings/models' && options.method === 'PATCH')
      return {
        ...state.settings,
        revision: 'saved',
        default: { ...options.body.default, api_key: 'configured' },
      }
    if (path === '/settings/models') return state.settings
    return []
  })
  await wrapper.find('form').trigger('submit')
  await flushPromises()
  expect(request.mock.calls[0]![1]?.body).toMatchObject({
    expected_revision: '0',
    default: { model: 'gpt-6-luna', max_output_tokens: 25400, api_key: 'fixture-new-key' },
  })
  expect(wrapper.text()).toContain('配置已保存')
  expect((wrapper.vm as any).dirty).toBe(false)
  expect(testButton(wrapper).attributes('disabled')).toBeUndefined()
  expect((wrapper.find('#model-max-tokens').element as HTMLInputElement).value).toBe('25400')
  wrapper.unmount()
})

it('queries an unsaved profile without inference or saving and keeps manual model entry', async () => {
  connectionSettings()
  let resolve!: (value: unknown) => void
  const request = vi.spyOn(apiModule, 'api').mockImplementation(
    () =>
      new Promise((done) => {
        resolve = done
      }),
  )
  const wrapper = mount(SettingsView, { global: { plugins: [installUiComponents] } })
  await wrapper.find('#model-url').setValue('https://new.example/v1')
  expect(discoverButton(wrapper).attributes('disabled')).toBeDefined()
  await replaceKey(wrapper)
  await wrapper.find('#model-name').setValue('')
  await discoverButton(wrapper).trigger('click')
  await discoverButton(wrapper).trigger('click')
  expect(request).toHaveBeenCalledTimes(1)
  expect(request.mock.calls[0]![0]).toBe('/settings/models/discover')
  expect(request.mock.calls[0]![1]?.body).toMatchObject({
    stage: 'default',
    expected_revision: 'saved-revision',
    profile: { base_url: 'https://new.example/v1', model: '', api_key: 'fixture-new-key' },
  })
  expect(wrapper.find('#model-url').attributes('disabled')).toBeDefined()
  expect(testButton(wrapper).attributes('disabled')).toBeDefined()
  resolve({ ok: true, models: ['fixture-a', 'fixture-b'], message: '已读取 2 个模型' })
  await flushPromises()
  expect(wrapper.text()).toContain('已读取 2 个模型')
  expect(wrapper.findComponent({ name: 'AAutoComplete' }).props('options')).toEqual([
    { value: 'fixture-a' },
    { value: 'fixture-b' },
  ])
  await wrapper.find('#model-name').setValue('manual-model')
  expect(saveButton(wrapper).attributes('disabled')).toBeUndefined()
  expect(request).toHaveBeenCalledTimes(1)
  await wrapper.find('#model-url').setValue('https://another.example/v1')
  expect(wrapper.findComponent({ name: 'AAutoComplete' }).props('options')).toEqual([])
  wrapper.unmount()
})

it('requires confirmation before refreshing a dirty draft and explains stale/offline blockers', async () => {
  connectionSettings()
  const request = vi.spyOn(apiModule, 'api')
  const confirm = vi.spyOn(Modal, 'confirm').mockReturnValue({ destroy: vi.fn(), update: vi.fn() })
  const wrapper = mount(SettingsView, { global: { plugins: [installUiComponents] } })
  await wrapper.find('#model-name').setValue('manual-edit')
  state.settings = { ...state.settings, revision: 'changed-elsewhere' }
  await flushPromises()
  expect(saveButton(wrapper).attributes('title')).toContain('配置版本已变化')
  const refresh = wrapper
    .findAll('button')
    .find((button) => button.text().includes('读取最新配置'))!
  await refresh.trigger('click')
  await refresh.trigger('click')
  expect(confirm).toHaveBeenCalledTimes(1)
  expect(request).not.toHaveBeenCalled()
  expect((wrapper.find('#model-name').element as HTMLInputElement).value).toBe('manual-edit')
  state.online = false
  await flushPromises()
  expect(saveButton(wrapper).attributes('title')).toContain('网络离线')
  wrapper.unmount()
})

it('aborts discovery on unmount and ignores the late model list', async () => {
  connectionSettings()
  let resolve!: (value: unknown) => void
  const request = vi.spyOn(apiModule, 'api').mockImplementation(
    () =>
      new Promise((done) => {
        resolve = done
      }),
  )
  const wrapper = mount(SettingsView, { global: { plugins: [installUiComponents] } })
  await discoverButton(wrapper).trigger('click')
  expect(testButton(wrapper).attributes('disabled')).toBeDefined()
  wrapper.unmount()
  expect(request.mock.calls[0]![1]?.signal?.aborted).toBe(true)
  resolve({ ok: true, models: ['late'], message: 'late' })
  await flushPromises()
  expect(request).toHaveBeenCalledTimes(1)
})

it('recovers a failed initial read through the visible reload action', async () => {
  state.authenticated = true
  state.online = true
  state.settings = null
  apiModule.setToken('fixture-only-token')
  const request = vi.spyOn(apiModule, 'api').mockRejectedValueOnce(new Error('fixture read failed'))
  const wrapper = mount(SettingsView, { global: { plugins: [installUiComponents] } })
  const refresh = wrapper
    .findAll('button')
    .find((button) => button.text().includes('读取最新配置'))!
  await refresh.trigger('click')
  await flushPromises()
  expect(wrapper.find('#model-url').attributes('disabled')).toBeDefined()
  request.mockResolvedValue({
    revision: '0',
    default: { base_url: '', model: '', api_key: 'missing' },
    stages: {},
    validation: [],
  })
  await refresh.trigger('click')
  await flushPromises()
  expect(wrapper.find('#model-url').attributes('disabled')).toBeUndefined()
  expect(wrapper.text()).toContain('已读取最新配置')
  expect(wrapper.text()).not.toContain('fixture read failed')
  wrapper.unmount()
})

it('keeps manual entry available after discovery failure and does not auto-retry', async () => {
  connectionSettings()
  const request = vi
    .spyOn(apiModule, 'api')
    .mockResolvedValue({ ok: false, models: [], message: '服务不支持模型列表' })
  const wrapper = mount(SettingsView, { global: { plugins: [installUiComponents] } })
  await discoverButton(wrapper).trigger('click')
  await flushPromises()
  expect(wrapper.text()).toContain('服务不支持模型列表；仍可手动填写模型 ID')
  await wrapper.find('#model-name').setValue('manual-fallback')
  expect(saveButton(wrapper).attributes('disabled')).toBeUndefined()
  expect(request).toHaveBeenCalledTimes(1)
  wrapper.unmount()
})

it('restores the address-specific warning when a replacement key is cleared', async () => {
  connectionSettings()
  const wrapper = mount(SettingsView, { global: { plugins: [installUiComponents] } })
  await wrapper.find('#model-url').setValue('https://new.example/v1')
  const warning = '服务地址已改变，请选择替换并填写新地址专用的 API Key'
  expect(wrapper.text()).toContain(warning)
  await replaceKey(wrapper)
  expect(wrapper.text()).not.toContain(warning)
  expect(saveButton(wrapper).attributes('disabled')).toBeUndefined()
  await wrapper.find('#model-key').setValue('   ')
  expect(wrapper.text()).toContain(warning)
  expect(saveButton(wrapper).attributes('disabled')).toBeDefined()
  expect(discoverButton(wrapper).attributes('disabled')).toBeDefined()
  wrapper.unmount()
})

it('explains environment versus saved source without exposing a configuration path', async () => {
  connectionSettings()
  state.settings!.source = 'environment'
  const wrapper = mount(SettingsView, { global: { plugins: [installUiComponents] } })
  expect(wrapper.text()).toContain('配置来源：服务启动环境（含 .env）')
  state.settings = { ...state.settings, source: 'saved' }
  await flushPromises()
  expect(wrapper.text()).toContain('它优先于 .env；修改 .env 不会自动覆盖')
  expect(wrapper.text()).not.toContain('model-settings.json')
  await wrapper.find('#model-name').setValue('new-model')
  expect(wrapper.text()).toContain('请先保存修改，再测试已保存的有效连接')
  wrapper.unmount()
})
````
