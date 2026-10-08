# ui/src/components/RunTable.vue · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：Vue 3 / Ant Design本机操作台源码。** 这是操作台自有的源码或测试支持文件，按路径保留。测试使用合成数据和受控接口，不接触真实模型密钥。

**对应关系：** ui/src及锁文件 → npm ci/test/build → workbench/web → FastAPI本机页面；与生成产品的前端模板是两套不同界面。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `ui/src/components/RunTable.vue`；**本文件共有 1 段**。本段覆盖源文件 L1–L62。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1995`。本段原文以LF换行结束。

<!-- learning-source: {"path": "ui/src/components/RunTable.vue", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "ab34f8886e72daaae18788345291146b4927a1ddd9546de5a02e6d8cadfca2dc"} -->
````vue
<!-- ui/src/components/RunTable.vue -->
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
````
