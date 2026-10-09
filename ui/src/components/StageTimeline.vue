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
