# ui/src/components/StageTimeline.vue · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：Vue 3 / Ant Design本机操作台源码。** 这是操作台自有的源码或测试支持文件，按路径保留。测试使用合成数据和受控接口，不接触真实模型密钥。

**对应关系：** ui/src及锁文件 → npm ci/test/build → workbench/web → FastAPI本机页面；与生成产品的前端模板是两套不同界面。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `ui/src/components/StageTimeline.vue`；**本文件共有 1 段**。本段覆盖源文件 L1–L70。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`2314`。本段原文以LF换行结束。

<!-- learning-source: {"path": "ui/src/components/StageTimeline.vue", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "ffe7165dad2aa096b5b738b1c3e4d90591eb9bbc990b088acb5f43489e01ace5"} -->
````vue
<!-- ui/src/components/StageTimeline.vue -->
<script setup lang="ts">
import { computed } from 'vue'
import { CheckOutlined, ExclamationCircleOutlined } from '@ant-design/icons-vue'
import { activeStage, milestoneStatus, stages } from '../presentation'
import type { Run, RunEvent } from '../types'
const props = defineProps<{ run: Run; events: RunEvent[]; compact?: boolean; selected?: string }>()
const emit = defineEmits<{ select: [stage: string] }>()
const active = computed(() => activeStage(props.run, props.events))
const entries = computed(() =>
  stages.map((stage, index) => ({
    ...stage,
    status: milestoneStatus(index, props.run, props.events),
  })),
)
const labels = {
  pending: '待执行',
  waiting: '等待确认',
  running: '执行中',
  done: '已有完成记录',
  failed: '失败',
}
</script>
<template>
  <ol :class="compact ? 'rail-steps' : 'milestones'" aria-label="真实执行阶段">
    <li
      v-for="(stage, index) in entries"
      :key="stage.key"
      :class="{
        current: active === index,
        done: stage.status === 'done',
        failed: stage.status === 'failed',
      }"
    >
      <component
        :is="compact ? 'div' : 'button'"
        :class="compact ? 'rail-step' : 'milestone'"
        :type="compact ? undefined : 'button'"
        :aria-pressed="compact ? undefined : selected === stage.key"
        @click="!compact && emit('select', selected === stage.key ? 'all' : stage.key)"
      >
        <span class="step-dot"
          ><CheckOutlined
            v-if="stage.status === 'done'"
            aria-hidden="true"
          /><ExclamationCircleOutlined
            v-else-if="stage.status === 'failed'"
            aria-hidden="true"
          /><template v-else>{{ index + 1 }}</template></span
        >
        <div>
          <strong>{{ stage.label }}</strong>
          <p>{{ stage.status === 'pending' ? '等待前置阶段' : stage.description }}</p>
        </div>
        <a-tag
          v-if="!compact"
          :color="
            stage.status === 'done'
              ? 'green'
              : stage.status === 'failed'
                ? 'red'
                : stage.status === 'pending'
                  ? 'default'
                  : 'blue'
          "
          >{{ labels[stage.status] }}</a-tag
        >
      </component>
    </li>
  </ol>
</template>
````
