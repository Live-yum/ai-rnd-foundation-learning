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
