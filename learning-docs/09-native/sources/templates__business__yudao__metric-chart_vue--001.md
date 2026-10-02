# templates/business/yudao/metric-chart.vue · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：Vben真实指标的图表组件。** 将服务器已按角色范围计算的指标转换为Echarts展示；空样本、数量、时长和日期轴有不同含义，不在前端编造统计数字。

**对应关系：** 业务metrics响应 → panel.vue → 本图表 → 原生主题。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `templates/business/yudao/metric-chart.vue`；**本文件共有 1 段**。本段覆盖源文件 L1–L27。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1435`。本段原文以LF换行结束。

<!-- learning-source: {"path": "templates/business/yudao/metric-chart.vue", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "9ebf9551af538eeb0590e0acf8587a6a84ebc8175a647f6fc656593d21eca684"} -->
````vue
<!-- templates/business/yudao/metric-chart.vue -->
<script lang="ts" setup>
import type { EchartsUIType } from '@vben/plugins/echarts';
import { nextTick, ref, watch } from 'vue';
import { EchartsUI, useEcharts } from '@vben/plugins/echarts';

const props = defineProps<{ buckets: Record<string, number>; bucketLabels?: Record<string, string>; kind: string; label: string }>();
const chartRef = ref<EchartsUIType>();
const rendered = ref(false);
let generation = 0;
const { renderEcharts } = useEcharts(chartRef);
watch(() => props.buckets, async () => {
  const current = ++generation;
  rendered.value = false;
  await nextTick();
  const chart = await renderEcharts({
    animation: !window.matchMedia('(prefers-reduced-motion: reduce)').matches,
    title: { text: props.label }, tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: Object.keys(props.buckets).map(key => props.bucketLabels?.[key] || key), axisLabel: { rotate: 25, width: 140, overflow: 'truncate' } },
    yAxis: { type: 'value', minInterval: 1 },
    series: [props.kind === 'time_count'
      ? { type: 'line', data: Object.values(props.buckets), showSymbol: true, symbol: 'circle', symbolSize: 8 }
      : { type: 'bar', data: Object.values(props.buckets) }],
  });
  if (current === generation) rendered.value = !!chart;
}, { immediate: true, deep: true });
</script>
<template><EchartsUI ref="chartRef" class="h-72 w-full" data-rnd-metric-chart :data-rnd-metric-rendered="rendered" /></template>
````
