# ui/tests/settings.test.ts · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：Vue 3 / Ant Design本机操作台源码。** 这是操作台自有的源码或测试支持文件，按路径保留。测试使用合成数据和受控接口，不接触真实模型密钥。

**对应关系：** ui/src及锁文件 → npm ci/test/build → workbench/web → FastAPI本机页面；与生成产品的前端模板是两套不同界面。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `ui/tests/settings.test.ts`；**本文件共有 1 段**。本段覆盖源文件 L1–L67。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`2144`。本段原文以LF换行结束。

<!-- learning-source: {"path": "ui/tests/settings.test.ts", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "ddeb62ba8c5800248d4e97a8bde8d60c431e21c7a6fbfdc27f52218a993b06eb"} -->
````typescript
// ui/tests/settings.test.ts
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
````
