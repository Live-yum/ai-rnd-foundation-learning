# ui/src/components/Questionnaire.vue · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：Vue 3 / Ant Design本机操作台源码。** 按后端当前问题渲染单选、多选或文字回答，提交问题ID和选项ID；必填和自定义约束在浏览器提示后仍由后端复验。

**对应关系：** ui/src及锁文件 → npm ci/test/build → workbench/web → FastAPI本机页面；与生成产品的前端模板是两套不同界面。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `ui/src/components/Questionnaire.vue`；**本文件共有 1 段**。本段覆盖源文件 L1–L170。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`6356`。本段原文以LF换行结束。

<!-- learning-source: {"path": "ui/src/components/Questionnaire.vue", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "ed2228bd1857412059232923054337a7a0b0cd167ec6c4e2942ffeda323e6110"} -->
````vue
<!-- ui/src/components/Questionnaire.vue -->
<script setup lang="ts">
import { computed, reactive, watch } from 'vue'
import { ArrowRightOutlined } from '@ant-design/icons-vue'
import type { Gate } from '../types'
interface Question {
  id: string
  prompt: string
  kind: 'single' | 'multiple' | 'text'
  options: { id: string; label: string; description?: string }[]
  required: boolean
  allow_other: boolean
}
const props = defineProps<{ gate: Gate; disabled: boolean; busy: boolean }>()
const emit = defineEmits<{ submit: [text: string, answers?: any[]] }>()
const values = reactive<Record<string, { selected: string[]; text: string; other: boolean }>>({})
const questions = computed<Question[]>(() => {
  const items: Question[] =
    props.gate.data?.requirement?.question_items || props.gate.data?.question_items || []
  const texts: string[] = props.gate.data?.requirement?.questions || []
  return items.length && texts.length && items.map((q) => q.prompt).join('\n') !== texts.join('\n')
    ? []
    : items
})
const legacy = computed<string[]>(() => props.gate.data?.requirement?.questions || [])
const free = reactive({ text: '', submitted: false })
watch(
  () => props.gate.gate_id,
  () => {
    Object.keys(values).forEach((k) => delete values[k])
    questions.value.forEach((q) => (values[q.id] = { selected: [], text: '', other: false }))
    free.text = ''
    free.submitted = false
  },
  { immediate: true },
)
function missing(q: Question) {
  const answer = values[q.id]
  if (!answer) return true
  if (answer.other && !answer.text.trim()) return true
  return q.required && !(answer.selected.length || answer.text.trim())
}
const valid = computed(() =>
  questions.value.length
    ? questions.value.every((q) => !missing(q)) &&
      (!!free.text.trim() ||
        questions.value.some((q) => values[q.id]?.selected.length || values[q.id]?.text.trim()))
    : !!free.text.trim(),
)
function submit() {
  free.submitted = true
  if (props.disabled || props.busy || !valid.value) return
  emit(
    'submit',
    free.text.trim(),
    questions.value.length
      ? questions.value.map((q) => ({
          question_id: q.id,
          option_ids: values[q.id].selected,
          text: values[q.id].text.trim(),
        }))
      : undefined,
  )
}
function single(q: Question, value: string) {
  values[q.id].selected = value === '__other__' ? [] : [value]
  values[q.id].other = value === '__other__'
  if (value !== '__other__') values[q.id].text = ''
}
</script>
<template>
  <form class="question-card panel" @submit.prevent="submit">
    <header class="panel-heading">
      <div>
        <h2>确认这一版的使用方式</h2>
        <p>补充关键细节，再整理为可审核的方案</p>
      </div>
      <a-tag color="blue">交互规划</a-tag>
    </header>
    <div class="question-body">
      <section
        v-for="q in questions"
        :key="q.id"
        class="question"
        :aria-labelledby="'question-' + q.id"
      >
        <div class="question-title">
          <h3 :id="'question-' + q.id">{{ q.prompt }}</h3>
          <a-tag>{{ { single: '单选', multiple: '多选', text: '文字回答' }[q.kind] }}</a-tag
          ><a-tag v-if="q.required" color="gold">必答</a-tag><a-tag v-else>可选</a-tag>
        </div>
        <a-radio-group
          v-if="q.kind === 'single'"
          :value="values[q.id]?.other ? '__other__' : values[q.id]?.selected[0]"
          :disabled="disabled || busy"
          class="choice-list"
          @change="single(q, $event.target.value)"
        >
          <a-radio v-for="option in q.options" :key="option.id" :value="option.id" class="choice"
            ><span>{{ option.label }}</span
            ><small v-if="option.description">{{ option.description }}</small></a-radio
          >
          <a-radio v-if="q.allow_other" value="__other__" class="choice">其他，我来补充</a-radio>
        </a-radio-group>
        <a-checkbox-group
          v-else-if="q.kind === 'multiple'"
          v-model:value="values[q.id].selected"
          :disabled="disabled || busy"
          class="choice-grid"
          ><a-checkbox
            v-for="option in q.options"
            :key="option.id"
            :value="option.id"
            class="choice"
            ><span>{{ option.label }}</span
            ><small v-if="option.description">{{ option.description }}</small></a-checkbox
          ></a-checkbox-group
        >
        <a-textarea
          v-if="
            q.kind === 'text' || values[q.id]?.other || (q.kind === 'multiple' && q.allow_other)
          "
          v-model:value="values[q.id].text"
          :aria-label="q.prompt + '的补充回答'"
          :disabled="disabled || busy"
          :auto-size="{ minRows: 2, maxRows: 6 }"
          :maxlength="10000"
          placeholder="用自己的话补充，不会替你改写原意"
          class="question-text"
        />
        <p v-if="free.submitted && missing(q)" class="field-error" role="alert">
          请完成此题；选择“其他”后需要填写内容
        </p>
      </section>
      <template v-if="!questions.length"
        ><div v-for="(question, index) in legacy" :key="index" class="legacy-question">
          <span>{{ index + 1 }}</span>
          <h3>{{ question }}</h3>
        </div>
        <a-textarea
          v-model:value="free.text"
          aria-label="需求回答"
          :auto-size="{ minRows: 4, maxRows: 12 }"
          :disabled="disabled || busy"
          :maxlength="20000"
          placeholder="按问题逐项回答，或直接描述你的想法…"
      /></template>
      <template v-else
        ><label class="form-label" for="question-extra">其他补充（可选）</label
        ><a-textarea
          id="question-extra"
          v-model:value="free.text"
          :auto-size="{ minRows: 2, maxRows: 6 }"
          :disabled="disabled || busy"
          :maxlength="20000"
          placeholder="还有需要我们知道的吗？"
      /></template>
    </div>
    <footer class="panel-footer">
      <span>必答问题不可跳过 · 提交后先汇总</span
      ><a-button
        type="primary"
        html-type="submit"
        size="large"
        :loading="busy"
        :disabled="disabled || !valid"
        ><ArrowRightOutlined aria-hidden="true" />提交本组答案</a-button
      >
    </footer>
  </form>
</template>
````
