<script setup lang="ts">
import { ArrowRightOutlined } from '@ant-design/icons-vue'
import { state } from '../state'
import {
  formatDate,
  nextRunView,
  runNextAction,
  runStageLabel,
  shortId,
  statusColor,
  statusLabel,
} from '../presentation'
import type { Run } from '../types'
defineProps<{ runs: Run[] }>()
const emit = defineEmits<{ navigate: [path: string] }>()
const projectName = (run: Run) =>
  state.projects.find((project) => project.id === run.project_id)?.title ||
  run.project_title ||
  '项目 ' + shortId(run.project_id)
</script>
<template>
  <div class="table-scroll" tabindex="0" aria-label="项目运行队列，可横向滚动">
    <table class="run-table">
      <thead>
        <tr>
          <th>项目 / 运行</th>
          <th>模板</th>
          <th>状态与下一步</th>
          <th>最近更新</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="run in runs" :key="run.id">
          <td>
            <strong>{{ projectName(run) }}</strong
            ><small>{{ shortId(run.id) }} · {{ runStageLabel(run) }}</small>
          </td>
          <td>
            {{
              state.catalog.find((entry) => entry.template === run.template)?.name || run.template
            }}
          </td>
          <td>
            <a-tag :color="statusColor(run.status)">{{ statusLabel(run.status) }}</a-tag
            ><small>{{ runNextAction(run) }}</small>
          </td>
          <td>{{ formatDate(run.updated_at || run.created_at) }}</td>
          <td>
            <a-button
              type="link"
              :aria-label="'打开运行：' + projectName(run)"
              @click="emit('navigate', `run/${run.id}/${nextRunView(run)}`)"
              >{{ ['READY', 'SOURCE_READY'].includes(run.status) ? '查看产物' : '打开运行' }}
              <ArrowRightOutlined aria-hidden="true"
            /></a-button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
