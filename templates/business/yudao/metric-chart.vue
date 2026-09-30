<script lang="ts" setup>
import type { EchartsUIType } from '@vben/plugins/echarts';
import { nextTick, ref, watch } from 'vue';
import { EchartsUI, useEcharts } from '@vben/plugins/echarts';

const props = defineProps<{ buckets: Record<string, number>; bucketLabels?: Record<string, string>; kind: string; label: string }>();
const chartRef = ref<EchartsUIType>();
const { renderEcharts } = useEcharts(chartRef);
watch(() => props.buckets, async () => {
  await nextTick();
  await renderEcharts({
    title: { text: props.label }, tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: Object.keys(props.buckets).map(key => props.bucketLabels?.[key] || key), axisLabel: { rotate: 25, width: 140, overflow: 'truncate' } },
    yAxis: { type: 'value', minInterval: 1 },
    series: [{ type: props.kind === 'time_count' ? 'line' : 'bar', data: Object.values(props.buckets) }],
  });
}, { immediate: true, deep: true });
</script>
<template><EchartsUI ref="chartRef" class="h-72 w-full" /></template>
