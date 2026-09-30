<script lang="ts" setup>
import { computed, onMounted, ref, watch } from 'vue';
import { useVbenModal } from '@vben/common-ui';
import { Alert, Button, Card, Select, Space, Statistic, Table, Timeline, TimelineItem, message } from 'ant-design-vue';
import { useVbenForm } from '#/adapter/form';
import { requestClient } from '#/api/request';
import MetricChart from './metric-chart.vue';
import { businessActionLabel, businessDetails, businessDisplayValue, businessFieldLabel, businessStateLabel, businessTimestamp } from './business-form';

interface Role { name: string; label: string }
interface Transition { name: string; label?: string; to_state: string }
interface Meta { bootstrapRequired?: boolean; actions: string[]; transitions: Transition[]; roleAdmin: boolean; roles: Role[]; record: Record<string, unknown> | null }
interface User { id: string; nickname: string; username: string }
interface Event { id: number; actor_id: string; actor_name?: string; action: string; note: string; created_at: string; before_data?: string; after_data?: string }
interface Notice { id: number; message: string; display_message?: string; entity: string; record_id: string; created_at: string; read_at: string | null }
interface RelatedRow { record: Record<string, unknown> & { id: string }; actions: string[] }
interface RelatedGroup { entity: string; label: string; field: string; columns: string[]; records: RelatedRow[] }
interface Related { parent: { entity: string; id: string }; groups: RelatedGroup[] }
interface Metric { name: string; label: string; kind: string; value?: number | null; samples?: number; unit?: string; buckets?: Record<string, number>; bucketLabels?: Record<string, string> }
const props = defineProps<{ entity: string; recordId?: string }>();
const emit = defineEmits<{ changed: [] }>();
const meta = ref<Meta>({ actions: [], transitions: [], roleAdmin: false, roles: [], record: null });
const users = ref<User[]>([]), history = ref<Event[]>([]), notices = ref<Notice[]>([]), metrics = ref<Metric[]>([]);
const relatedGroups = ref<RelatedGroup[]>([]), relatedEvents = ref<Event[]>([]), relatedLabel = ref('');
let relatedRequest = 0;
const busy = ref(false), audit = ref(false), selectedAction = ref(''), selectedTransition = ref('');
const assignee = ref<string>(), selectedUser = ref<string>(), selectedRole = ref<string>();
const userOptions = computed(() => users.value.map(user => ({ label: user.nickname && user.nickname !== user.username ? `${user.nickname} · ${user.username}` : user.username, value: user.id })));
const details = computed(() => businessDetails(props.entity, meta.value.record));
const roleOptions = computed(() => meta.value.roles.map(role => ({ label: role.label, value: role.name })));
let generation = 0;
const [ActionForm, actionFormApi] = useVbenForm({
  schema: [{ fieldName: 'note', label: '处理备注', component: 'Textarea', componentProps: { maxlength: 4000, rows: 4, 'data-testid': 'business-note-input' } }],
  showDefaultActions: false,
});
const [ActionModal, actionModalApi] = useVbenModal({ onConfirm: submitAction });

async function bootstrap() { if (busy.value) return; busy.value = true; try { await requestClient.post('/infra/rnd-business/bootstrap'); message.success('本产品业务角色已初始化'); await reload(); emit('changed'); } finally { busy.value = false; } }
async function reload() {
  const current = ++generation;
  const result = await requestClient.get<Meta>('/infra/rnd-business/meta', { params: { entity: props.entity, id: props.recordId } });
  if (current !== generation) return;
  meta.value = result;
  history.value = []; relatedGroups.value = []; relatedEvents.value = []; relatedLabel.value = ''; relatedRequest++;
  if (result.bootstrapRequired) return;
  if (props.recordId && result.actions.includes(audit.value ? 'read_audit' : 'read_history')) {
    const rows = await requestClient.get<Event[]>('/infra/rnd-business/history', { params: { entity: props.entity, id: props.recordId, audit: audit.value } });
    if (current === generation) history.value = rows;
  }
  const [people, reminders, values, related] = await Promise.all([
    requestClient.get<User[]>('/infra/rnd-business/users'),
    requestClient.get<Notice[]>('/infra/rnd-business/notifications'),
    requestClient.get<Metric[]>('/infra/rnd-business/metrics'),
    props.recordId ? requestClient.get<Related>('/infra/rnd-business/related', { params: { entity: props.entity, id: props.recordId } }) : Promise.resolve({ groups: [] } as Pick<Related, 'groups'>),
  ]);
  if (current !== generation) return;
  users.value = people; notices.value = reminders; metrics.value = values; relatedGroups.value = related.groups;
}
function relatedRowKey(row: RelatedRow) { return row.record.id; }
function relatedData(group: RelatedGroup) {
  return group.records.map(row => ({ ...row, display: Object.fromEntries(
    [...group.columns, 'createdAt', 'archivedAt'].map(field => [field, businessDisplayValue(group.entity, field, row.record)]),
  ) }));
}
function relatedColumns(group: RelatedGroup) {
  return [{ title: '编号', dataIndex: ['record', 'id'], width: 100 },
    ...group.columns.map(field => ({ title: businessFieldLabel(group.entity, field), dataIndex: ['display', field], ellipsis: true, width: 200 })),
    { title: '创建时间', dataIndex: ['display', 'createdAt'], width: 220 },
    { title: '归档时间', dataIndex: ['display', 'archivedAt'], width: 220 },
    { title: '操作', key: 'history', width: 130 }];
}
async function showRelatedHistory(group: RelatedGroup, row: Record<string, unknown>) {
  const record = row.record;
  if (!record || typeof record !== 'object' || !('id' in record) || typeof record.id !== 'string'
    || !Array.isArray(row.actions) || !row.actions.includes('read_history')) throw new Error('Invalid related history row');
  const request = ++relatedRequest, current = generation;
  const entries = await requestClient.get<Event[]>('/infra/rnd-business/history', { params: { entity: group.entity, id: record.id, audit: false } });
  if (request !== relatedRequest || current !== generation) return;
  relatedLabel.value = '_recordLabel' in record && typeof record._recordLabel === 'string' ? record._recordLabel : `${group.label} #${record.id}`; relatedEvents.value = entries;
}
async function openAction(action: string, transition = '') {
  selectedAction.value = action; selectedTransition.value = transition;
  assignee.value = undefined;
  // The pinned native modal mounts its Form only after the first open.
  actionModalApi.open();
  await actionFormApi.resetForm();
}
async function submitAction() {
  if (!props.recordId || busy.value) return;
  busy.value = true;
  try {
    const data = await actionFormApi.getValues();
    await requestClient.post('/infra/rnd-business/action', {
      entity: props.entity, id: props.recordId, action: selectedAction.value,
      transition: selectedTransition.value || undefined,
      assigneeId: assignee.value ?? null, note: data.note || '',
    });
    actionModalApi.close(); message.success('业务操作已保存'); emit('changed'); await reload();
  } finally { busy.value = false; }
}
async function archive() {
  if (!props.recordId || busy.value) return;
  busy.value = true;
  try {
    await requestClient.delete(`/infra/wb-${props.entity.replaceAll('_', '-')}/delete`, { params: { id: props.recordId } });
    message.success('记录已归档，历史保留'); emit('changed'); await reload();
  } finally { busy.value = false; }
}
async function markRead(id: number) { await requestClient.post('/infra/rnd-business/notifications/read', { id }); await reload(); }
async function changeRole(grant: boolean) {
  if (!selectedUser.value || !selectedRole.value || busy.value) return;
  busy.value = true;
  try {
    await requestClient.post('/infra/rnd-business/roles', { userId: selectedUser.value, role: selectedRole.value, grant });
    message.success('业务角色已更新；对应用户重新登录后刷新原生菜单'); await reload();
  } finally { busy.value = false; }
}
async function toggleAudit() { audit.value = !audit.value; await reload(); }
watch(() => [props.entity, props.recordId], () => { audit.value = false; void reload(); });
onMounted(reload);
</script>

<template>
  <section class="mt-4 space-y-4" data-rnd-business-panel>
    <Card title="业务处理与历史">
      <Alert v-if="meta.bootstrapRequired" message="需要原生超级管理员显式初始化本产品业务角色；不会授予其他用户全局管理员权限" type="warning" />
      <Button data-testid="business-bootstrap" v-if="meta.bootstrapRequired" :loading="busy" @click="bootstrap">初始化本产品业务权限</Button>
      <Alert v-if="!recordId" message="点击表格中的“业务详情”处理分配、状态和备注" type="info" />
      <template v-else>
        <dl class="mb-3 grid gap-2 md:grid-cols-2"><div v-for="item in details" :key="item.field"><dt class="text-xs text-gray-500">{{ item.label }}</dt><dd class="break-words">{{ item.value }}</dd></div></dl>
        <p class="mb-3">记录 #{{ recordId }} · 创建人 {{ businessDisplayValue(entity, 'createdBy', meta.record) }} · {{ meta.record?.archivedAt ? '已归档' : '有效' }}</p>
        <Space wrap>
          <Button data-testid="business-assign" v-if="meta.actions.includes('assign') && !meta.record?.archivedAt" @click="openAction('assign')">分配负责人</Button>
          <Button :data-testid="`business-transition-${transition.name}`" v-for="transition in meta.transitions" :key="transition.name" @click="openAction('transition', transition.name)">{{ transition.label || transition.name }} → {{ businessStateLabel(entity, transition.to_state) }}</Button>
          <Button data-testid="business-note" v-if="meta.actions.includes('add_note') && !meta.record?.archivedAt" @click="openAction('add_note')">添加处理备注</Button>
          <Button v-if="meta.actions.includes('archive') && !meta.record?.archivedAt" danger :loading="busy" @click="archive">归档</Button>
          <Button data-testid="business-audit" v-if="meta.actions.includes('read_audit')" @click="toggleAudit">{{ audit ? '查看历史' : '查看审计' }}</Button>
          <Button @click="reload">刷新</Button>
        </Space>
        <Timeline class="mt-4">
          <TimelineItem v-for="entry in history" :key="entry.id">
            <span>{{ businessTimestamp(entry.created_at) }} · {{ businessActionLabel(entry.action) }} · {{ entry.actor_name || `用户 #${entry.actor_id}` }}</span>
            <p>{{ entry.note }}</p>
            <pre v-if="audit && entry.before_data" class="overflow-auto text-xs">{{ entry.before_data }} → {{ entry.after_data }}</pre>
          </TimelineItem>
        </Timeline>
      </template>
    </Card>
    <Card v-for="group in relatedGroups" :key="`${group.entity}:${group.field}`" :title="`关联${group.label}与历史记录`" :data-testid="`business-related-${group.entity}`">
      <Table :data-source="relatedData(group)" :row-key="relatedRowKey" :columns="relatedColumns(group)" :pagination="{ pageSize: 5 }" :scroll="{ x: 'max-content' }">
        <template #bodyCell="{ column, record }"><Button v-if="column.key === 'history' && record.actions.includes('read_history')" :data-testid="`related-history-${group.entity}-${record.record.id}`" @click="showRelatedHistory(group, record)">处理历史</Button></template>
      </Table>
    </Card>
    <Card v-if="relatedLabel" :title="`${relatedLabel} · 处理历史`" data-testid="business-related-history">
      <Timeline><TimelineItem v-for="entry in relatedEvents" :key="entry.id"><span>{{ businessTimestamp(entry.created_at) }} · {{ businessActionLabel(entry.action) }} · {{ entry.actor_name || `用户 #${entry.actor_id}` }}</span><p>{{ entry.note }}</p></TimelineItem></Timeline>
    </Card>
    <Card title="业务统计" v-if="metrics.length">
      <div class="grid gap-4 md:grid-cols-2">
        <template v-for="metric in metrics" :key="metric.name">
          <MetricChart v-if="metric.buckets" :buckets="metric.buckets" :bucket-labels="metric.bucketLabels" :kind="metric.kind" :label="metric.label" />
          <Statistic v-else :title="metric.label" :value="metric.value ?? '暂无样本'" :suffix="metric.unit === 'seconds' ? '秒' : ''" />
        </template>
      </div>
    </Card>
    <Card title="站内提醒">
      <Table :data-source="notices" row-key="id" :pagination="{ pageSize: 5 }" :scroll="{ x: 'max-content' }" :columns="[{ title: '提醒', key: 'message', width: 300 }, { title: '时间', key: 'createdAt', width: 220 }, { title: '状态', key: 'read', width: 120 }]">
        <template #bodyCell="{ column, record }"><template v-if="column.key === 'message'">{{ record.display_message || record.message }}</template><template v-else-if="column.key === 'createdAt'">{{ businessTimestamp(record.created_at) }}</template><template v-else-if="column.key === 'read'"><span :data-testid="`business-notice-read-state-${record.id}`" v-if="record.read_at">已读</span><Button :data-testid="`business-notice-read-${record.id}`" v-else @click="markRead(record.id)">标为已读</Button></template></template>
      </Table>
    </Card>
    <Card v-if="meta.roleAdmin" title="业务角色管理">
      <Space wrap><Select v-model:value="selectedUser" :options="userOptions" placeholder="选择用户" class="min-w-48" /><Select v-model:value="selectedRole" :options="roleOptions" placeholder="选择业务角色" class="min-w-36" /><Button :loading="busy" @click="changeRole(true)">授予</Button><Button :loading="busy" danger @click="changeRole(false)">撤销</Button></Space>
      <p class="mt-2 text-sm">只管理本产品声明的业务角色，不授予平台全局管理员权限</p>
    </Card>
    <ActionModal :title="selectedAction === 'assign' ? '分配负责人' : selectedAction === 'transition' ? '执行状态操作' : '处理备注'">
      <Select data-testid="business-assignee" v-if="selectedAction === 'assign'" v-model:value="assignee" :options="userOptions" allow-clear placeholder="选择负责人，留空取消分配" class="mb-4 w-full" />
      <ActionForm />
    </ActionModal>
  </section>
</template>

<style scoped>
:deep(.ant-table-thead > tr > th) { white-space: nowrap; }
</style>
