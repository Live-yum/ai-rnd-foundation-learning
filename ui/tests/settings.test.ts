import { mount, flushPromises } from '@vue/test-utils'
import { beforeAll, afterEach, describe, expect, it, vi } from 'vitest'
import Antd from 'ant-design-vue'
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
  lock()
  vi.restoreAllMocks()
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
