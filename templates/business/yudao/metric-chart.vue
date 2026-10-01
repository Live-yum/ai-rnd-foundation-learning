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
