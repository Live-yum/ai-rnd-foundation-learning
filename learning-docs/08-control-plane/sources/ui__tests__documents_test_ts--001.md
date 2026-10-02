# ui/tests/documents.test.ts · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：Vue 3 / Ant Design本机操作台源码。** 这是操作台自有的源码或测试支持文件，按路径保留。测试使用合成数据和受控接口，不接触真实模型密钥。

**对应关系：** ui/src及锁文件 → npm ci/test/build → workbench/web → FastAPI本机页面；与生成产品的前端模板是两套不同界面。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `ui/tests/documents.test.ts`；**本文件共有 1 段**。本段覆盖源文件 L1–L72。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`2694`。本段原文以LF换行结束。

<!-- learning-source: {"path": "ui/tests/documents.test.ts", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "6a5a5e51741042173506ce91ff289151a4b46adc01242a6f68c49d5d8ee3f252"} -->
````typescript
// ui/tests/documents.test.ts
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
````
