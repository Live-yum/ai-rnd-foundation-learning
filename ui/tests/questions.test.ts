import { mount } from '@vue/test-utils'
import { beforeAll, describe, expect, it, vi } from 'vitest'
import Antd from 'ant-design-vue'
import Questionnaire from '../src/components/Questionnaire.vue'
const items = [
  {
    id: 'role',
    prompt: '谁来使用？',
    kind: 'single',
    options: [{ id: 'team', label: '团队成员' }],
    required: true,
    allow_other: true,
  },
  {
    id: 'features',
    prompt: '需要哪些功能？',
    kind: 'multiple',
    options: [
      { id: 'search', label: '搜索' },
      { id: 'date', label: '日期' },
    ],
    required: true,
    allow_other: true,
  },
]
const gate = {
  gate_id: 'a'.repeat(64),
  version: 1,
  digest: 'b'.repeat(64),
  stage: 'clarification',
  data: { requirement: { questions: items.map((i) => i.prompt), question_items: items } },
  actions: ['answer', 'reject'],
  can_approve: false,
}
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
const create = (override: any = {}) =>
  mount(Questionnaire, {
    props: { gate, disabled: false, busy: false, ...override },
    global: { plugins: [Antd] },
  })
describe('structured question user intent', () => {
  it('requires every required answer and submits exact option ids', async () => {
    const wrapper = create()
    expect(wrapper.find('button[type="submit"]').attributes('disabled')).toBeDefined()
    await wrapper.find('input[type="radio"]').setValue(true)
    await wrapper.find('input[type="checkbox"]').setValue(true)
    expect(wrapper.find('button[type="submit"]').attributes('disabled')).toBeUndefined()
    await wrapper.find('form').trigger('submit')
    expect(wrapper.emitted('submit')?.[0]).toEqual([
      '',
      [
        { question_id: 'role', option_ids: ['team'], text: '' },
        { question_id: 'features', option_ids: ['search'], text: '' },
      ],
    ])
    wrapper.unmount()
  })
  it('clears hidden Other text when a fixed option is chosen', async () => {
    const wrapper = create()
    const radios = wrapper.findAll('input[type="radio"]')
    await radios[1].setValue(true)
    await wrapper.find('textarea[aria-label="谁来使用？的补充回答"]').setValue('不得偷偷带入')
    await radios[0].setValue(true)
    await wrapper.find('input[type="checkbox"]').setValue(true)
    await wrapper.find('form').trigger('submit')
    expect(JSON.stringify(wrapper.emitted('submit'))).not.toContain('不得偷偷带入')
    wrapper.unmount()
  })
  it('requires Other text and keeps exact custom intent', async () => {
    const wrapper = create()
    await wrapper.findAll('input[type="radio"]')[1].setValue(true)
    await wrapper.find('input[type="checkbox"]').setValue(true)
    expect(wrapper.find('button[type="submit"]').attributes('disabled')).toBeDefined()
    await wrapper
      .find('textarea[aria-label="谁来使用？的补充回答"]')
      .setValue('客服、主管与只读运营')
    await wrapper.find('form').trigger('submit')
    expect((wrapper.emitted('submit')?.[0]?.[1] as any[])[0]).toEqual({
      question_id: 'role',
      option_ids: [],
      text: '客服、主管与只读运营',
    })
    wrapper.unmount()
  })
  it('resets answers on a new gate version', async () => {
    const wrapper = create()
    await wrapper.find('input[type="radio"]').setValue(true)
    await wrapper.find('input[type="checkbox"]').setValue(true)
    await wrapper.setProps({ gate: { ...gate, gate_id: 'c'.repeat(64), version: 2 } })
    expect(wrapper.find('button[type="submit"]').attributes('disabled')).toBeDefined()
    wrapper.unmount()
  })
  it('falls back to all original questions when structured prompts do not match', () => {
    const wrapper = create({
      gate: {
        ...gate,
        data: { requirement: { questions: ['另一个不能隐藏的问题'], question_items: items } },
      },
    })
    expect(wrapper.text()).toContain('另一个不能隐藏的问题')
    expect(wrapper.findAll('input[type="radio"]')).toHaveLength(0)
    expect(wrapper.find('textarea[aria-label="需求回答"]').exists()).toBe(true)
    wrapper.unmount()
  })
  it('never submits while disabled or already busy', async () => {
    const wrapper = create({ busy: true })
    await wrapper.find('form').trigger('submit')
    expect(wrapper.emitted('submit')).toBeUndefined()
    wrapper.unmount()
  })
  it('does not enable an empty submission when every structured question is optional', async () => {
    const optional = items.map((item) => ({ ...item, required: false }))
    const wrapper = create({
      gate: {
        ...gate,
        data: {
          requirement: { questions: optional.map((item) => item.prompt), question_items: optional },
        },
      },
    })
    expect(wrapper.find('button[type="submit"]').attributes('disabled')).toBeDefined()
    await wrapper.find('#question-extra').setValue('只补充这一条真实意图')
    expect(wrapper.find('button[type="submit"]').attributes('disabled')).toBeUndefined()
    wrapper.unmount()
  })
})
