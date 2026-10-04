# ui/tests/capability.test.ts · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：Vue 3 / Ant Design本机操作台源码。** 这是操作台自有的源码或测试支持文件，按路径保留。测试使用合成数据和受控接口，不接触真实模型密钥。

**对应关系：** ui/src及锁文件 → npm ci/test/build → workbench/web → FastAPI本机页面；与生成产品的前端模板是两套不同界面。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `ui/tests/capability.test.ts`；**本文件共有 1 段**。本段覆盖源文件 L1–L281。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`10248`。本段原文以LF换行结束。

<!-- learning-source: {"path": "ui/tests/capability.test.ts", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "9b8210241a8e93c2382fe6474d90abeea889b572480e55b1da510fefc9366761"} -->
````typescript
// ui/tests/capability.test.ts
import { mount } from '@vue/test-utils'
import { beforeAll, beforeEach, describe, expect, it, vi } from 'vitest'
import Antd from 'ant-design-vue'
import { state } from '../src/state'
import { api } from '../src/api'
import RunView from '../src/components/RunView.vue'

vi.mock('../src/api', async (original) => ({
  ...(await original<any>()),
  api: vi.fn().mockResolvedValue({}),
}))
vi.mock('../src/state', async (original) => ({
  ...(await original<any>()),
  openRun: vi.fn().mockResolvedValue(undefined),
}))

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
  vi.clearAllMocks()
  Object.assign(state, {
    authenticated: true,
    online: true,
    stale: false,
    loading: false,
    settings: { ready: true },
    report: {},
    events: [],
    projects: [],
    messages: [{ id: 1, role: 'user', content: '大学生计算机设计大赛报名网站' }],
    run: {
      id: 'saved-run',
      project_id: 'project',
      template: 'fastapiadmin',
      status: 'BLOCKED',
      auto_mode: false,
      pending: {
        gate_id: 'a'.repeat(64),
        digest: 'b'.repeat(64),
        version: 5,
        stage: 'clarification',
        actions: ['answer', 'reject', 'recommend'],
        can_approve: false,
        data: {
          ready: false,
          blocked: ['需要明确参赛者入口，不推定匿名访问'],
          requirement: {
            summary: '大学生计算机设计大赛报名网站',
            questions: ['请明确所需报名入口'],
          },
          capability_conflicts: [
            {
              code: 'registration_entrypoint_unresolved',
              message: '需要明确参赛者入口，不推定匿名访问',
              alternatives: [
                '参赛者注册登录后自行提交并仅管理本人的报名',
                '保留独立公开门户要求并暂停，另行扩展能力',
                '明确改为仅管理员维护',
              ],
            },
          ],
        },
      },
    },
  })
})

describe('persisted registration scope decision', () => {
  it('does not present old planning completion as valid progress after scope recovery', () => {
    state.events = [
      { id: 1, kind: 'stage', data: { name: 'requirements', phase: 'completed', round: 1 } },
      { id: 2, kind: 'stage', data: { name: 'plan', phase: 'completed', round: 1 } },
    ]
    const wrapper = mount(RunView, {
      props: { runId: 'saved-run', view: 'conversation' },
      global: { plugins: [Antd] },
    })
    const steps = wrapper.findAll('.rail-steps li')
    expect(steps[0].classes()).toContain('current')
    expect(steps[0].classes()).not.toContain('done')
    expect(steps[1].classes()).not.toContain('done')
    wrapper.unmount()
  })

  it('shows honest entrant paths without enabling automatic scope reduction', async () => {
    const wrapper = mount(RunView, {
      props: { runId: 'saved-run', view: 'conversation' },
      global: { plugins: [Antd] },
    })
    expect(wrapper.text()).toContain('大学生计算机设计大赛报名网站')
    expect(wrapper.text()).toContain('参赛者注册登录后自行提交并仅管理本人的报名')
    expect(wrapper.text()).toContain('另行扩展能力')
    const smart = wrapper.findAll('button').find((b) => b.text().includes('了解并开启智能推荐'))!
    expect(smart.attributes('disabled')).toBeDefined()
    await smart.trigger('click')
    expect(api).not.toHaveBeenCalled()
    expect(wrapper.find('input[type="radio"]:checked').exists()).toBe(false)
    wrapper.unmount()
  })

  it('submits only the explicit correction bound to the current persisted gate', async () => {
    const wrapper = mount(RunView, {
      props: { runId: 'saved-run', view: 'conversation' },
      global: { plugins: [Antd] },
    })
    const text = '保留参赛者自行报名，使用登录后的现有业务界面，不需要匿名访问'
    const field = wrapper.find('textarea')
    await field.setValue(text)
    await wrapper.find('form').trigger('submit')
    expect(api).toHaveBeenCalledOnce()
    const [path, options] = vi.mocked(api).mock.calls[0]
    expect(path).toBe('/runs/saved-run/resume')
    expect((options as any).body).toMatchObject({
      action: 'answer',
      text,
      gate_id: 'a'.repeat(64),
      version: 5,
      digest: 'b'.repeat(64),
    })
    expect(JSON.stringify((options as any).body)).not.toContain('仅管理员维护')
    wrapper.unmount()
  })
})

it('keeps failed-attempt diagnostics and historical questions readable after the gate is cleared', () => {
  state.run!.pending = null
  state.run!.status = 'FAILED'
  state.messages = [
    {
      message_id: 'gate-old',
      role: 'assistant',
      validation: 'historical_gate',
      content:
        '历史澄清与模板能力提示（保留记录，不代表当前仍未解决）\n参与者将通过哪种入口报名？\n能力限制：模板不支持匿名公开报名页',
    },
    {
      message_id: 'answer',
      role: 'user',
      content: '参赛者注册并登录后，在现有业务界面自行提交报名，仅管理本人报名记录',
    },
    {
      message_id: 'attempt-1',
      role: 'assistant',
      validation: 'failed',
      code: 'schema_validation',
      stage: 'requirements',
      response_id: 'trace-123',
      diagnostic: {
        phase: 'response_validation',
        trace_id: 'trace-123',
        attempt: 1,
        summary: '模型响应未通过结构校验',
        retry_hint: '重试当前运行，无需重填已提交的回答。',
        details: [{ path: ['summary'], type: 'string_type', message: '字段结构或类型不符合约定' }],
      },
    },
  ]
  const wrapper = mount(RunView, {
    props: { runId: 'saved-run', view: 'conversation' },
    global: { plugins: [Antd] },
  })
  expect(wrapper.text()).toContain('参与者将通过哪种入口报名？')
  expect(wrapper.text()).toContain('模板不支持匿名公开报名页')
  expect(wrapper.text()).toContain('仅管理本人报名记录')
  expect(wrapper.text()).toContain('schema_validation')
  expect(wrapper.text()).toContain('trace-123')
  expect(wrapper.text()).toContain('summary：string_type')
  expect(wrapper.text()).toContain('无需重填已提交的回答')
  expect(wrapper.text()).not.toContain('暂无可展示的摘要')
  expect(wrapper.find('form.question-card').exists()).toBe(false)
  wrapper.unmount()
})

it('keeps blocked design feedback usable and renders each tab content inside its panel', async () => {
  state.run!.pending = {
    gate_id: 'a'.repeat(64),
    digest: 'b'.repeat(64),
    version: 7,
    stage: 'design',
    actions: ['approve', 'revise', 'reject', 'recommend'],
    can_approve: false,
    data: {
      blocked: ['实体 registration 字段 status 与框架保留字段冲突'],
      plan: {
        title: '竞赛报名',
        entities: [{ name: 'registration', fields: [{ name: 'status' }] }],
      },
      tasks: [{ id: 'registration-module', title: '报名模块' }],
    },
  }
  const wrapper = mount(RunView, {
    props: { runId: 'saved-run', view: 'review' },
    global: { plugins: [Antd] },
  })
  const field = wrapper.find('textarea[aria-label="审核修改意见"]')
  expect(field.attributes('disabled')).toBeUndefined()
  const submit = wrapper.findAll('button').find((button) => button.text() === '提交修改意见')!
  expect(submit.attributes('disabled')).toBeDefined()
  await field.setValue('保留报名业务状态，修复框架字段冲突')
  expect(submit.attributes('disabled')).toBeUndefined()
  const approval = wrapper
    .findAll('button')
    .find((button) => button.text().includes('确认设计，开始生成'))!
  expect(approval.attributes('disabled')).toBeDefined()
  const dataTab = wrapper.findAll('[role="tab"]').find((tab) => tab.text() === '数据模型')!
  await dataTab.trigger('click')
  expect(wrapper.find('[role="tabpanel"][aria-hidden="false"]').text()).toContain('registration')
  await submit.trigger('click')
  expect(api).toHaveBeenCalledWith(
    '/runs/saved-run/resume',
    expect.objectContaining({
      body: expect.objectContaining({
        action: 'revise',
        text: '保留报名业务状态，修复框架字段冲突',
        version: 7,
        digest: 'b'.repeat(64),
      }),
    }),
  )
  wrapper.unmount()
})

it('labels generic extension READY as reviewed executable contract, not full semantic proof', () => {
  state.run!.status = 'READY'
  state.run!.pending = null
  state.run!.result = {
    coverage_level: 'reviewed-executable-contract',
    full_request_complete: null,
    source_units: [{ id: 'source-0-0', text: '保留原始业务要求' }],
  }
  const wrapper = mount(RunView, {
    props: { runId: 'saved-run', view: 'delivery' },
    global: { plugins: [Antd] },
  })
  expect(wrapper.find('.coverage-notice').text()).toContain('仅证明已审阅可执行合同')
  expect(wrapper.find('.coverage-notice').text()).toContain('不代表全部原始需求')
  expect(wrapper.text()).toContain('保留原始业务要求')
  wrapper.unmount()
})

it('keeps bounded contest evidence explicitly incomplete and download locked', () => {
  state.run!.pending = null
  state.report = {
    'extension-coverage.json': {
      coverage_level: 'bounded-business-slice',
      full_request_complete: false,
      remaining_obligations: ['original.full_source'],
    },
  }
  const wrapper = mount(RunView, {
    props: { runId: 'saved-run', view: 'delivery' },
    global: { plugins: [Antd] },
  })
  expect(wrapper.find('.coverage-notice').text()).toContain('不能交付')
  expect(wrapper.text()).toContain('下载锁定')
  const download = wrapper
    .findAll('button')
    .find((button) => button.text().includes('下载完整交付包'))
  expect(download?.attributes('disabled')).toBeDefined()
  wrapper.unmount()
})
````
