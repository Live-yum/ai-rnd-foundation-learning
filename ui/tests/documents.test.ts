import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import DataDocument from '../src/components/DataDocument.vue'
describe('scannable complete design documents', () => {
  const fields = [
    {
      name: 'title',
      label: '标题',
      kind: 'text',
      required: true,
      min_length: 1,
      max_length: 250,
      searchable: true,
      filterable: false,
      date_range: false,
      audit_note: '额外元数据应保留',
    },
    {
      name: 'category',
      kind: 'enum',
      required: false,
      choices: ['news', 'guide'],
      choice_labels: { news: '资讯', guide: '攻略' },
      searchable: false,
      filterable: true,
    },
  ]
  it('renders a compact accessible field table with actual constraints', () => {
    const wrapper = mount(DataDocument, { props: { data: fields } })
    expect(wrapper.findAll('thead th').map((node) => node.text())).toEqual([
      '名称',
      '类型',
      '必填',
      '约束',
      '搜索 / 筛选',
    ])
    expect(wrapper.findAll('tbody tr')).toHaveLength(2)
    expect(wrapper.find('tbody').text()).toContain('长度 1–250')
    expect(wrapper.find('tbody').text()).toContain('资讯 (news) / 攻略 (guide)')
    expect(wrapper.find('tbody').text()).toContain('精确筛选')
    expect(wrapper.find('details').text()).toContain('额外元数据应保留')
  })
  it('preserves entity boundaries rather than flattening the schema', () => {
    const wrapper = mount(DataDocument, {
      props: {
        data: [
          { name: 'news', description: '游戏资讯', fields },
          { name: 'notes', description: '知识笔记', fields: [fields[0]] },
        ],
      },
    })
    expect(wrapper.findAll('article.entity-card')).toHaveLength(2)
    expect(wrapper.findAll('table')).toHaveLength(2)
    expect(wrapper.text()).toContain('news · 2 个字段')
  })
  it('uses two-column definition metadata for nested objects and keeps false values', () => {
    const wrapper = mount(DataDocument, {
      props: { data: { required: false, max_length: 100, searchable: true }, depth: 1 },
    })
    expect(wrapper.find('dl.metadata-grid').exists()).toBe(true)
    expect(wrapper.text()).toContain('必填否')
    expect(wrapper.text()).toContain('最大长度100')
  })
  it('keeps root prose readable and escapes untrusted text', () => {
    const wrapper = mount(DataDocument, {
      props: { data: { summary: '<img src=x onerror=alert(1)>', data_scope: 'per_user' } },
    })
    expect(wrapper.findAll('section')).toHaveLength(2)
    expect(wrapper.find('img').exists()).toBe(false)
    expect(wrapper.text()).toContain('按用户隔离')
  })
})
