import { mount } from '@vue/test-utils'
import { beforeAll, beforeEach, describe, expect, it, vi } from 'vitest'
import Antd from 'ant-design-vue'
import { state } from '../src/state'
import { api } from '../src/api'
import RunView from '../src/components/RunView.vue'
import { activeStage, statusLabel } from '../src/presentation'

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

it('shows exact source and atomic completeness meaning before design approval', () => {
  state.run!.status = 'WAITING_EXTENSION_DESIGN'
  state.run!.pending = {
    ...state.run!.pending!,
    stage: 'extension_design',
    can_approve: true,
    actions: ['approve', 'reject'],
    data: {
      extension: { baseline: { title: '原子合同' }, implementation: {} },
      source_units: [{ id: 'source-0-0', text: '库存不得超卖，过期订单必须释放占用。' }],
      atomic_review: {
        obligations: [{ assertion: '并发占用不得大于真实库存', source_id: 'source-0-0' }],
        complete_source_ids: ['source-0-0'],
      },
      requires_explicit_review: true,
    },
  }
  const wrapper = mount(RunView, {
    props: { runId: 'saved-run', view: 'review' },
    global: { plugins: [Antd] },
  })
  const visible = wrapper.find('.atomic-source-review').text()
  expect(visible).toContain('库存不得超卖，过期订单必须释放占用。')
  expect(visible).toContain('并发占用不得大于真实库存')
  expect(visible).toContain('穷尽分解')
  expect(wrapper.text()).toContain('我已核对原文相关性和完整来源的穷尽分解')
  wrapper.unmount()
})

it('names partial scope approval correctly and keeps remaining obligations visible', () => {
  state.run!.status = 'WAITING_EXTENSION_SCOPE'
  state.run!.pending = {
    ...state.run!.pending!,
    stage: 'extension_scope',
    can_approve: true,
    actions: ['approve', 'reject'],
    data: {
      delivery_kind: 'partial',
      full_request_complete: false,
      unverified_prerequisites: [{ description: '真实邮件服务仍未验证' }],
      review_conflicts: ['原先声明完成的容量规则仍有未验证子句'],
      requires_explicit_review: true,
    },
  }
  expect(statusLabel(state.run!.status)).toBe('等待交付范围确认')
  expect(activeStage(state.run, [])).toBe(5)
  const wrapper = mount(RunView, {
    props: { runId: 'saved-run', view: 'review' },
    global: { plugins: [Antd] },
  })
  expect(wrapper.text()).toContain('真实邮件服务仍未验证')
  expect(wrapper.find('.scope-review-conflicts').text()).toContain(
    '原先声明完成的容量规则仍有未验证子句',
  )
  expect(wrapper.text()).toContain('原文完整性声明已重新打开')
  expect(wrapper.text()).toContain('确认部分范围，准备交付包')
  expect(wrapper.text()).toContain('我接受当前部分成果，保留全部未完成义务')
  expect(wrapper.text()).not.toContain('确认需求，生成计划')
  wrapper.unmount()
})

it('labels an approved partial package without claiming complete delivery', () => {
  state.run!.status = 'SOURCE_READY'
  state.run!.pending = null
  state.run!.result = {
    delivery_kind: 'partial',
    coverage_level: 'bounded-business-slice',
    full_request_complete: false,
  }
  const wrapper = mount(RunView, {
    props: { runId: 'saved-run', view: 'delivery' },
    global: { plugins: [Antd] },
  })
  expect(wrapper.find('.coverage-notice').text()).toContain('仅交付明确批准的部分成果')
  expect(wrapper.find('.coverage-notice').text()).not.toContain('不能交付')
  expect(wrapper.text()).toContain('下载部分成果包')
  wrapper.unmount()
})

it('keeps full reviewed-contract scope distinct from partial delivery', () => {
  state.run!.status = 'WAITING_EXTENSION_SCOPE'
  state.run!.pending = {
    ...state.run!.pending!,
    stage: 'extension_scope',
    can_approve: true,
    actions: ['approve', 'reject'],
    data: { delivery_kind: 'reviewed-contract', full_request_complete: true },
  }
  const wrapper = mount(RunView, {
    props: { runId: 'saved-run', view: 'review' },
    global: { plugins: [Antd] },
  })
  expect(wrapper.text()).toContain('确认范围，准备交付包')
  expect(wrapper.text()).toContain('我已核对当前已审阅合同及交付证据')
  expect(wrapper.text()).not.toContain('我接受当前部分成果')
  wrapper.unmount()
})

it.each(['extension_scope', 'extension_delivery'])(
  'permits exact %s approval after model configuration is removed',
  async (stage) => {
    state.settings = { ready: false } as any
    state.run!.status = 'WAITING_' + stage.toUpperCase()
    state.run!.pending = {
      ...state.run!.pending!,
      stage,
      can_approve: true,
      actions: ['approve', 'reject'],
      data: { delivery_kind: 'partial', full_request_complete: false },
    }
    const wrapper = mount(RunView, {
      props: { runId: 'saved-run', view: stage === 'extension_scope' ? 'review' : 'delivery' },
      global: { plugins: [Antd] },
    })
    await wrapper.find('input[type="checkbox"]').setValue(true)
    const approve = wrapper
      .findAll('button')
      .find((button) =>
        stage === 'extension_scope'
          ? button.text().includes('确认部分范围')
          : button.text().includes('确认交付'),
      )!
    expect(approve).toBeDefined()
    expect(approve.attributes('disabled')).toBeUndefined()
    await approve.trigger('click')
    expect(api).toHaveBeenCalledWith(
      '/runs/saved-run/resume',
      expect.objectContaining({
        body: expect.objectContaining({
          action: 'approve',
          approved: true,
          gate_id: 'a'.repeat(64),
        }),
      }),
    )
    wrapper.unmount()
  },
)

it('routes normal extension-delivery navigation to the final approval screen', async () => {
  state.run!.status = 'WAITING_EXTENSION_DELIVERY'
  state.run!.pending = {
    ...state.run!.pending!,
    stage: 'extension_delivery',
    can_approve: true,
    actions: ['approve', 'reject'],
    data: { delivery_kind: 'partial' },
  }
  const wrapper = mount(RunView, {
    props: { runId: 'saved-run', view: 'conversation' },
    global: { plugins: [Antd] },
  })
  const open = wrapper
    .findAll('button')
    .find((button) => button.text().includes('查看并审核当前版本'))!
  await open.trigger('click')
  expect(wrapper.emitted('navigate')).toContainEqual(['run/saved-run/delivery'])
  wrapper.unmount()
})

it('allows only server-marked retained packaging retries without model settings', async () => {
  state.settings = { ready: false } as any
  state.run!.status = 'FAILED'
  state.run!.pending = null
  state.run!.model_free_retry = true
  const wrapper = mount(RunView, {
    props: { runId: 'saved-run', view: 'conversation' },
    global: { plugins: [Antd] },
  })
  const retry = wrapper.findAll('button').find((button) => button.text().includes('重试当前运行'))!
  expect(retry.attributes('disabled')).toBeUndefined()
  state.run!.model_free_retry = false
  await wrapper.vm.$nextTick()
  expect(retry.attributes('disabled')).toBeDefined()
  state.run!.model_free_retry = true
  await wrapper.vm.$nextTick()
  await retry.trigger('click')
  expect(api).toHaveBeenCalledWith(
    '/runs/saved-run/retry',
    expect.objectContaining({ method: 'POST' }),
  )
  wrapper.unmount()
})
