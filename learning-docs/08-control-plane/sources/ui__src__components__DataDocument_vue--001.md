# ui/src/components/DataDocument.vue · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：Vue 3 / Ant Design本机操作台源码。** 把结构化需求、计划或报告变成可阅读字段；输出作为文本显示，不执行模型提供的HTML。

**对应关系：** ui/src及锁文件 → npm ci/test/build → workbench/web → FastAPI本机页面；与生成产品的前端模板是两套不同界面。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `ui/src/components/DataDocument.vue`；**本文件共有 1 段**。本段覆盖源文件 L1–L180。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`7227`。本段原文以LF换行结束。

<!-- learning-source: {"path": "ui/src/components/DataDocument.vue", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "cef64422fc36dde4dc6e9e05150f202bd4b595f2f072555e9dc7694c84fc641d"} -->
````vue
<!-- ui/src/components/DataDocument.vue -->
<script setup lang="ts">
import { computed } from 'vue'
import { fieldLabels } from '../presentation'
const props = withDefaults(defineProps<{ data: any; depth?: number }>(), { depth: 0 })
const primitive = (value: any) => value === null || typeof value !== 'object'
const object = (value: any) => value && typeof value === 'object' && !Array.isArray(value)
const useful = (key: string, value: any) =>
  !['question_items', 'questions', 'source_quote'].includes(key) &&
  value !== null &&
  value !== undefined &&
  value !== '' &&
  !(Array.isArray(value) && !value.length) &&
  !(object(value) && !Object.keys(value).length)
const entries = computed(() =>
  object(props.data) ? Object.entries(props.data).filter(([key, value]) => useful(key, value)) : [],
)
const simpleEntries = computed(() => entries.value.filter(([, value]) => primitive(value)))
const complexEntries = computed(() => entries.value.filter(([, value]) => !primitive(value)))
const isFields = computed(
  () =>
    Array.isArray(props.data) &&
    props.data.length > 0 &&
    props.data.every(
      (item) => object(item) && typeof item.name === 'string' && typeof item.kind === 'string',
    ),
)
const isEntities = computed(
  () =>
    Array.isArray(props.data) &&
    props.data.length > 0 &&
    props.data.every(
      (item) => object(item) && typeof item.name === 'string' && Array.isArray(item.fields),
    ),
)
const typeLabels: Record<string, string> = {
  text: '文本',
  integer: '整数',
  boolean: '布尔',
  date: '日期',
  datetime: '日期时间',
  enum: '枚举',
}
const valueLabels: Record<string, string> = {
  per_user: '按用户隔离',
  shared: '团队共享',
  unknown: '待确认',
  runtime: '运行级验收',
  source: '源码级验收',
}
const display = (value: any) =>
  value === true ? '是' : value === false ? '否' : value === null ? '—' : String(value)
function semantic(value: any, key: string) {
  return ['data_scope', 'validation_level', 'mode'].includes(key)
    ? valueLabels[value] || display(value)
    : display(value)
}
function constraints(field: any) {
  const result = []
  if (
    ['text', 'enum'].includes(field.kind) &&
    (field.min_length !== undefined || field.max_length !== undefined)
  )
    result.push(`长度 ${field.min_length ?? 0}–${field.max_length ?? '不限'}`)
  if (field.choices?.length)
    result.push(
      '选项：' +
        field.choices
          .map((choice: string) =>
            field.choice_labels?.[choice] ? `${field.choice_labels[choice]} (${choice})` : choice,
          )
          .join(' / '),
    )
  return result
}
function capabilities(field: any) {
  const result = []
  if (field.searchable) result.push('关键词搜索')
  if (field.filterable) result.push('精确筛选')
  if (field.date_range) result.push('日期范围')
  return result.length ? result.join(' · ') : '未启用'
}
function entityExtras(entity: any) {
  return Object.fromEntries(
    Object.entries(entity).filter(([key]) => !['name', 'description', 'fields'].includes(key)),
  )
}
</script>
<template>
  <div class="data-document" :class="{ 'nested-document': depth > 0 }">
    <p v-if="primitive(data)" class="document-text">{{ display(data) }}</p>
    <div v-else-if="isFields" class="field-schema">
      <div class="field-table-region" role="region" aria-label="字段定义" tabindex="0">
        <table class="field-table">
          <thead>
            <tr>
              <th scope="col">名称</th>
              <th scope="col">类型</th>
              <th scope="col">必填</th>
              <th scope="col">约束</th>
              <th scope="col">搜索 / 筛选</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="field in data" :key="field.name">
              <td data-label="名称">
                <strong>{{ field.label || field.name }}</strong
                ><small v-if="field.label && field.label !== field.name">{{ field.name }}</small>
              </td>
              <td data-label="类型">
                <span class="schema-type">{{ typeLabels[field.kind] || field.kind }}</span>
              </td>
              <td data-label="必填">{{ field.required ? '必填' : '可选' }}</td>
              <td data-label="约束">
                <span
                  v-for="(constraint, index) in constraints(field)"
                  :key="index"
                  class="constraint-line"
                  >{{ constraint }}</span
                ><span v-if="!constraints(field).length">—</span>
              </td>
              <td data-label="搜索 / 筛选">{{ capabilities(field) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <details class="document-details">
        <summary>查看完整字段属性</summary>
        <div v-for="field in data" :key="field.name" class="complete-field">
          <h4>{{ field.label || field.name }}</h4>
          <DataDocument :data="field" :depth="depth + 1" />
        </div>
      </details>
    </div>
    <div v-else-if="isEntities" class="entity-cards">
      <article v-for="entity in data" :key="entity.name" class="entity-card">
        <header>
          <div class="entity-symbol" aria-hidden="true">▦</div>
          <div>
            <h3>{{ entity.description || entity.name }}</h3>
            <p>{{ entity.name }} · {{ entity.fields.length }} 个字段</p>
          </div>
        </header>
        <DataDocument :data="entity.fields" :depth="depth + 1" />
        <details v-if="Object.keys(entityExtras(entity)).length" class="document-details">
          <summary>其他实体定义</summary>
          <DataDocument :data="entityExtras(entity)" :depth="depth + 1" />
        </details>
      </article>
    </div>
    <ul v-else-if="Array.isArray(data) && data.every(primitive)" class="document-list">
      <li v-for="(item, index) in data" :key="index">{{ display(item) }}</li>
    </ul>
    <div v-else-if="Array.isArray(data)" class="document-rows">
      <div v-for="(item, index) in data" :key="index" class="document-row">
        <span class="row-number">{{ String(index + 1).padStart(2, '0') }}</span
        ><DataDocument :data="item" :depth="depth + 1" />
      </div>
    </div>
    <template v-else-if="depth > 0"
      ><dl v-if="simpleEntries.length" class="metadata-grid">
        <div v-for="[key, value] in simpleEntries" :key="key">
          <dt>{{ fieldLabels[key] || key }}</dt>
          <dd>{{ semantic(value, key) }}</dd>
        </div>
      </dl>
      <section v-for="[key, value] in complexEntries" :key="key" class="document-section">
        <h3 class="section-label">{{ fieldLabels[key] || key }}</h3>
        <DataDocument :data="value" :depth="depth + 1" /></section
    ></template>
    <template v-else
      ><section v-for="([key, value], index) in entries" :key="key" class="document-section">
        <h3>
          <span class="section-number">{{ String(index + 1).padStart(2, '0') }}</span
          >{{ fieldLabels[key] || key }}
        </h3>
        <p v-if="primitive(value)" class="document-text">{{ semantic(value, key) }}</p>
        <DataDocument v-else :data="value" :depth="depth + 1" /></section
    ></template>
  </div>
</template>
````
