<template>
  <div class="fa-full-height business-native-page">
    <ElAlert v-if="error" :title="error" type="error" :closable="false" />
    <ElCard v-if="!config">
      <ElButton @click="initialize('join')">加入业务工作区</ElButton>
      <ElButton @click="initialize('bootstrap')">管理员初始化业务角色</ElButton>
      <p>使用原生账号登录。普通注册用户只能加入默认业务角色。</p>
    </ElCard>
    <template v-else>
      <ElTabs v-model="tab" @tab-change="changeTab">
        <ElTabPane v-for="entity in visibleEntities" :key="entity.name" :label="entity.description" :name="entity.name" />
        <ElTabPane v-if="config.permissions.some((permission: Item) => permission.actions.includes('read_metrics'))" label="统计" name="$metrics" />
        <ElTabPane label="提醒" name="$inbox" />
        <ElTabPane v-if="config.can_manage_roles" label="业务角色" name="$roles" />
      </ElTabs>
      <ElCard v-if="tab === '$metrics'">
        <ElRow :gutter="16"><ElCol v-for="metric in metrics" :key="metric.name" :span="8">
          <ElCard><h3>{{ metric.label }}</h3><ElStatistic v-if="metric.value.value != null" :value="metric.value.value" :precision="metric.value.kind === 'average_duration' ? 2 : 0" />
            <span v-else-if="!metric.value.groups">暂无数据</span>
            <small v-if="metric.value.samples != null">{{ metric.value.samples }} 个样本 · 单位：秒</small>
            <FaTable v-if="metric.value.groups" :data="metric.display_groups || metric.value.groups" :columns="[{ prop: metric.value.kind === 'time_count' ? 'day' : 'key', label: '分组' }, { prop: 'count', label: '数量' }]" /></ElCard>
        </ElCol></ElRow>
      </ElCard>
      <ElCard v-else-if="tab === '$inbox'">
        <FaTable :columns="[]" :data="inbox"><ElTableColumn label="业务" min-width="130"><template #default="{ row }">{{ entityLabel(row.entity) }}</template></ElTableColumn><ElTableColumn prop="record_title" label="相关记录" min-width="220" show-overflow-tooltip />
          <ElTableColumn label="事件" min-width="140"><template #default="{ row }">{{ eventLabel(row.event) }}</template></ElTableColumn><ElTableColumn label="时间（UTC）" min-width="210"><template #default="{ row }">{{ dateText(row.created_at) }}</template></ElTableColumn>
          <ElTableColumn label="已读"><template #default="{ row }"><ElButton :data-testid="'read-notice-' + row.id" :disabled="row.read" @click="markRead(row)">{{ row.read ? '已读' : '标记已读' }}</ElButton></template></ElTableColumn>
        </FaTable>
      </ElCard>
      <ElCard v-else-if="tab === '$roles'">
        <FaTable :columns="[]" :data="users"><ElTableColumn prop="name" label="用户" /><ElTableColumn label="业务角色"><template #default="{ row }">{{ roleLabel(row.role) }}</template></ElTableColumn>
          <ElTableColumn label="变更角色"><template #default="{ row }">
            <ElSelect :model-value="row.role" :disabled="row.id === config.actor.id || busy" @change="changeRole(row, $event)">
              <ElOption v-for="role in config.business.roles" :key="role.name" :value="role.name" :label="role.label" />
            </ElSelect>
          </template></ElTableColumn>
        </FaTable>
      </ElCard>
      <template v-else-if="current">
        <FaSearchBar data-testid="business-search" v-model="searchForm" :items="searchItems" :show-search="true" :show-reset="true" @search="refresh" @reset="resetSearch" />
        <ElCard class="fa-table-card">
          <div v-for="field in current.fields.filter((f: Item) => f.date_range)" :key="field.name">
            <span>{{ field.label || field.name }}</span>
            <ElDatePicker v-model="searchForm[field.name + '_from']" :type="field.kind === 'datetime' ? 'datetime' : 'date'" :value-format="field.kind === 'date' ? 'YYYY-MM-DD' : undefined" placeholder="起始日期（含）" />
            <ElDatePicker v-model="searchForm[field.name + '_to']" :type="field.kind === 'datetime' ? 'datetime' : 'date'" :value-format="field.kind === 'date' ? 'YYYY-MM-DD' : undefined" placeholder="结束日期（含）" />
          </div>
          <ElButton data-testid="business-create" v-if="can('create')" :disabled="busy" @click="edit(null)">新增</ElButton>
          <ElSwitch v-model="archived" active-text="归档记录" @change="refresh" />
          <FaTable :columns="[]" :data="rows" v-loading="busy" row-key="id">
            <ElTableColumn v-for="field in current.fields" :key="field.name" :prop="field.name" :label="field.label || field.name" :min-width="columnWidth(field)" show-overflow-tooltip><template #default="{ row }">{{ displayValue(tab, field.name, row[field.name], row) }}</template></ElTableColumn>
            <ElTableColumn label="操作" width="360" fixed="right"><template #default="{ row }">
              <ElButton v-if="can('read_history')" :data-testid="'history-' + row.id" @click="showHistory(row)">历史</ElButton>
              <ElButton :data-testid="'related-' + row.id" @click="showRelated(row)">关联记录</ElButton>
              <template v-if="!row.archived_at">
                <ElButton v-if="can('update')" :data-testid="'update-' + row.id" @click="edit(row)">编辑</ElButton>
                <ElButton v-if="can('assign')" :data-testid="'assign-' + row.id" @click="showAssignment(row)">分配</ElButton>
                <ElButton v-if="can('add_note')" :data-testid="'note-' + row.id" @click="showNote(row)">备注</ElButton>
                <ElButton v-for="transition in transitions(row)" :key="transition.name" :data-testid="'transition-' + row.id + '-' + transition.name" :disabled="busy" @click="act(row, 'transition', { transition: transition.name })">{{ transition.label || transition.name }}</ElButton>
                <ElButton v-if="can('archive')" type="danger" :data-testid="'archive-' + row.id" @click="archiveRow(row)">归档</ElButton>
              </template>
            </template></ElTableColumn>
          </FaTable>
          <ElPagination v-model:current-page="page" :page-size="20" :total="total" @current-change="refresh" />
        </ElCard>
      </template>
      <FaDialog v-model="dialog" :title="editing ? '编辑记录' : '新增记录'" width="650px">
        <FaForm v-model="form" :items="formItems" :show-submit="false" :show-reset="false" label-width="130px">
          <template v-for="field in editableFields" :key="field.name" #[field.name]><div :data-testid="'field-' + field.name" class="business-field-control">
            <ElSelect v-if="relation(field)" v-model="form[field.name]" clearable filterable remote :remote-method="(query: string) => searchOptions(field, query)">
              <ElOption v-for="option in options[field.name] || []" :key="option.id" :label="option.label" :value="option.id" />
              <template #footer><ElButton v-if="optionMore[field.name]" @click="searchOptions(field, optionQueries[field.name] || '', (optionPages[field.name] || 1) + 1)">加载更多</ElButton></template>
            </ElSelect>
            <ElSelect v-else-if="field.kind === 'enum'" v-model="form[field.name]" clearable><ElOption v-for="choice in field.choices" :key="choice" :value="choice" :label="field.choice_labels?.[choice] || choice" /></ElSelect>
            <ElSwitch v-else-if="field.kind === 'boolean'" v-model="form[field.name]" />
            <ElInputNumber v-else-if="field.kind === 'integer'" v-model="form[field.name]" />
            <ElDatePicker v-else-if="field.kind === 'date' || field.kind === 'datetime'" v-model="form[field.name]" :type="field.kind === 'date' ? 'date' : 'datetime'" :value-format="field.kind === 'date' ? 'YYYY-MM-DD' : undefined" />
            <ElInput v-else v-model="form[field.name]" :maxlength="field.max_length" show-word-limit :type="field.max_length > 500 ? 'textarea' : 'text'" />
          </div></template>
        </FaForm>
        <template #footer><ElButton @click="dialog = false">取消</ElButton><ElButton data-testid="business-save" type="primary" :loading="busy" @click="save">保存</ElButton></template>
      </FaDialog>
      <FaDialog v-model="historyOpen" title="记录历史" width="800px">
        <ElTimeline><ElTimelineItem v-for="item in history" :key="item.id" :timestamp="dateText(item.created_at)">
          <strong>{{ eventLabel(item.event) }}</strong> · {{ item.actor_name || '历史参与者' }}<p v-if="item.data.text">{{ item.data.text }}</p><p v-if="item.data.transition">{{ transitionLabel(item.data.transition) }}</p>
          <ElDescriptions v-if="item.data.after" :column="2" border><ElDescriptionsItem v-for="(value, key) in item.data.after" :key="key" :label="fieldLabel(tab, String(key))">{{ displayValue(tab, String(key), value, item.data.after, item.after_display) }}</ElDescriptionsItem></ElDescriptions>
        </ElTimelineItem></ElTimeline>
      </FaDialog>
      <FaDialog v-model="relatedOpen" title="关联历史" width="900px">
        <section v-for="(records, entity) in related" :key="entity"><h3>{{ entityLabel(String(entity)) }}</h3>
          <FaTable :data="records" :columns="[]"><ElTableColumn v-for="field in entityFields(String(entity))" :key="field.name" :label="field.label || field.name" :min-width="columnWidth(field)" show-overflow-tooltip><template #default="{ row }">{{ displayValue(String(entity), field.name, row[field.name], row) }}</template></ElTableColumn><ElTableColumn label="详情" fixed="right" width="120"><template #default="{ row }"><ElButton @click="openRelated(String(entity), row)">查看历史</ElButton></template></ElTableColumn></FaTable>
        </section>
      </FaDialog>
      <FaDialog v-model="assignmentOpen" data-testid="assignment-dialog" title="分配负责人" form-mode="update" @confirm="assignSelected">
        <ElSelect v-model="selectedAssignee" filterable placeholder="选择可处理此业务的用户"><ElOption v-for="user in eligibleUsers" :key="user.id" :value="user.id" :label="`${user.name} · ${user.username} · ${roleLabel(user.role)}`" /></ElSelect>
      </FaDialog>
    </template>
  </div>
</template>
<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { ElMessageBox } from 'element-plus';
import { request } from '@utils';
import type { SearchFormItem } from '@/components/forms/fa-search-bar/index.vue';
import FaForm from '@/components/forms/fa-form/index.vue';
import type { FormItem } from '@/components/forms/fa-form/index.vue';
import FaTable from '@/components/tables/fa-table/index.vue';

type Item = Record<string, any>;
const config = ref<Item | null>(null), tab = ref(''), error = ref(''), busy = ref(false);
const rows = ref<Item[]>([]), total = ref(0), page = ref(1), archived = ref(false);
const metrics = ref<Item[]>([]), inbox = ref<Item[]>([]), users = ref<Item[]>([]);
const searchForm = ref<Item>({}), dialog = ref(false), form = ref<Item>({}), editing = ref<Item | null>(null);
const historyOpen = ref(false), history = ref<Item[]>([]), relatedOpen = ref(false), related = ref<Item>({});
const assignmentOpen = ref(false), selectedAssignee = ref(''), assignmentRow = ref<Item | null>(null);
const eligibleUsers = computed(() => users.value.filter(u => config.value?.business.permissions.some((p: Item) => p.role === u.role && p.entity === tab.value && ['all', 'assigned'].includes(p.scope) && p.actions.includes('read') && (p.actions.includes('update') || p.actions.includes('transition')))));
const optionQueries = ref<Record<string, string>>({}), optionPages = ref<Record<string, number>>({}), optionMore = ref<Record<string, boolean>>({});
const options = ref<Record<string, Item[]>>({});
const visibleEntities = computed(() => config.value?.entities.filter((e: Item) => config.value?.permissions.some((p: Item) => p.entity === e.name && p.actions.includes('read'))) || []);
const current = computed(() => config.value?.entities.find((e: Item) => e.name === tab.value));
const workflow = computed(() => config.value?.business.workflows.find((w: Item) => w.entity === tab.value));
const resource = computed(() => config.value?.business.resources.find((r: Item) => r.entity === tab.value));
const protectedFields = computed(() => new Set([resource.value?.assignee_field, workflow.value?.status_field, ...(workflow.value?.transitions.map((t: Item) => t.set_timestamp) || [])]));
const editableFields = computed(() => current.value?.fields.filter((f: Item) => !protectedFields.value.has(f.name)) || []);
const formItems = computed<FormItem[]>(() => editableFields.value.map((f: Item) => ({ key: f.name, label: f.label || f.name, type: 'input', span: 24 })));
const searchItems = computed<SearchFormItem[]>(() => [{ key: 'q', label: '搜索', type: 'input' }, ...(current.value?.fields.filter((f: Item) => f.filterable).map((f: Item) => ({ key: f.name, label: f.label || f.name, type: f.kind === 'enum' ? 'select' : 'input', options: f.kind === 'enum' ? f.choices.map((choice: string) => ({ label: f.choice_labels?.[choice] || choice, value: choice })) : undefined, placeholder: `请选择或输入${f.label || f.name}` })) || [])]);
function entityFields(entity: string): Item[] { return config.value?.entities.find((e: Item) => e.name === entity)?.fields || []; }
function entityLabel(entity: string) { return config.value?.entities.find((e: Item) => e.name === entity)?.description || entity; }
function roleLabel(role: string) { return config.value?.business.roles.find((r: Item) => r.name === role)?.label || role; }
function fieldLabel(entity: string, key: string) { return entityFields(entity).find(f => f.name === key)?.label || ({ id: '编号', created_by: '创建人', created_at: '创建时间', updated_at: '更新时间', archived_at: '归档时间' } as Record<string, string>)[key] || key; }
function dateText(value: unknown) { if (!value) return '—'; const date = new Date(String(value)); return Number.isNaN(date.getTime()) ? String(value) : date.toISOString().slice(0, 19).replace('T', ' ') + ' UTC'; }
function columnWidth(field: Item) { return field.kind === 'datetime' ? 220 : field.max_length > 500 ? 280 : 160; }
function displayValue(entity: string, key: string, value: unknown, row: Item = {}, extra: Item = {}) {
  if (value == null || value === '') return '—';
  if (extra[key] || row._display?.[key]) return extra[key] || row._display[key];
  const field = entityFields(entity).find(f => f.name === key);
  if (field?.choice_labels?.[String(value)]) return field.choice_labels[String(value)];
  if (field?.kind === 'datetime' || ['created_at', 'updated_at', 'archived_at'].includes(key)) return dateText(value);
  if (typeof value === 'boolean') return value ? '是' : '否';
  if (config.value?.business.relations.some((r: Item) => r.entity === entity && r.field === key)) return '关联记录';
  return String(value);
}
function eventLabel(event: string) { return ({ created: '创建记录', updated: '编辑记录', update: '编辑记录', assigned: '分配负责人', transitioned: '状态更新', add_note: '添加备注', note_added: '添加备注', archived: '归档记录', due: '已到截止时间' } as Record<string, string>)[event] || event; }
function transitionLabel(name: string) { return workflow.value?.transitions.find((t: Item) => t.name === name)?.label || name; }
function can(action: string) { return config.value?.permissions.some((p: Item) => p.entity === tab.value && p.actions.includes(action)); }
function relation(field: Item) { return config.value?.business.relations.find((r: Item) => r.entity === tab.value && r.field === field.name); }
function transitions(row: Item) { return can('transition') ? workflow.value?.transitions.filter((t: Item) => t.roles.includes(config.value?.actor.role) && t.from_states.includes(row[workflow.value?.status_field])) || [] : []; }
async function api(path: string, method = 'get', data?: Item) {
  const response: any = await request({ url: `/business/${path}`, method: method as any, ...(method === 'get' ? { params: data } : { data }) });
  return response.data.data;
}
async function perform(fn: () => Promise<void>) { if (busy.value) return; busy.value = true; error.value = ''; try { await fn(); } catch (e: any) { error.value = e?.message || '操作失败，请重试'; } finally { busy.value = false; } }
async function load() { config.value = await api('configuration'); if (!tab.value) tab.value = visibleEntities.value[0]?.name || '$inbox'; await refresh(); }
async function initialize(action: string) { await perform(async () => { await api(action, 'post', {}); await load(); }); }
async function changeTab() { searchForm.value = {}; page.value = 1; archived.value = false; rows.value = []; dialog.value = false; historyOpen.value = false; assignmentOpen.value = false; await refresh(); }
async function refresh() {
  if (!config.value) return;
  const activeTab = tab.value;
  if (tab.value === '$metrics') metrics.value = await api('metrics');
  else if (tab.value === '$inbox') inbox.value = await api('inbox');
  else if (tab.value === '$roles') users.value = await api('users');
  else { const { q, ...filters } = searchForm.value; for (const field of current.value?.fields || []) { if (field.kind === 'datetime') for (const key of [field.name, field.name + '_from', field.name + '_to']) if (filters[key]) filters[key] = new Date(filters[key]).toISOString(); } const result = await api(`${tab.value}/list`, 'get', { q: q || '', filters: JSON.stringify(Object.fromEntries(Object.entries(filters).filter(([, v]) => v !== '' && v != null))), archived: archived.value, page: page.value }); if (tab.value === activeTab) { rows.value = result.items; total.value = result.total; } }
}
function resetSearch() { searchForm.value = {}; page.value = 1; void refresh(); }
async function searchOptions(field: Item, query: string, pageNumber = 1) { const rel = relation(field); if (!rel) return; const target = config.value?.entities.find((e: Item) => e.name === rel.target_entity); const response = rel.target_entity === '$users' ? { items: await api('users'), total: 0 } : await api(`${rel.target_entity}/list`, 'get', { page_size: 100, page: pageNumber, q: target?.fields.some((f: Item) => f.searchable) ? query : '' }); const result = response.items.map((r: Item) => ({ id: r.id, label: r._title || r.name || r.title || '业务记录' })); options.value[field.name] = pageNumber === 1 ? result : [...(options.value[field.name] || []), ...result]; optionQueries.value[field.name] = query; optionPages.value[field.name] = pageNumber; optionMore.value[field.name] = pageNumber * 100 < response.total; }
async function edit(row: Item | null) {
  editing.value = row; form.value = {}; options.value = {};
  for (const field of editableFields.value) {
    form.value[field.name] = row?.[field.name] ?? (field.kind === 'boolean' ? false : null);
    if (relation(field)) { await searchOptions(field, '');
    }
  }
  dialog.value = true;
}
async function save() { await perform(async () => { const body = { ...form.value }; for (const field of editableFields.value) { if (field.kind === 'datetime' && body[field.name]) body[field.name] = new Date(body[field.name]).toISOString(); } await api(editing.value ? `${tab.value}/${editing.value.id}/update` : `${tab.value}/create`, 'post', body); dialog.value = false; await refresh(); }); }
async function act(row: Item, action: string, data: Item) { await perform(async () => { await api(`${tab.value}/${row.id}/${action}`, 'post', data); await refresh(); }); }
async function archiveRow(row: Item) { try { await ElMessageBox.confirm('归档后记录和历史保留，不能再编辑。继续？', '归档'); await act(row, 'archive', {}); } catch { /* cancelled */ } }
async function showNote(row: Item) { try { const result = await ElMessageBox.prompt('输入备注', '新增备注', { inputType: 'textarea' }); await act(row, 'add_note', { text: result.value }); } catch { /* cancelled */ } }
async function showAssignment(row: Item) { users.value = await api('users'); assignmentRow.value = row; selectedAssignee.value = row[resource.value?.assignee_field] || ''; assignmentOpen.value = true; }
async function assignSelected() { if (!assignmentRow.value || !selectedAssignee.value) return; await act(assignmentRow.value, 'assign', { assignee: selectedAssignee.value }); if (!error.value) assignmentOpen.value = false; }

async function openRelated(entity: string, row: Item) { tab.value = entity; relatedOpen.value = false; await refresh(); await showHistory(row); }
async function showHistory(row: Item) { history.value = await api(`${tab.value}/${row.id}/history`, 'get', { audit: can('read_audit') }); historyOpen.value = true; }
async function showRelated(row: Item) { related.value = await api(`${tab.value}/${row.id}/related`); relatedOpen.value = true; }
async function markRead(row: Item) { await perform(async () => { await api(`inbox/${row.id}/read`, 'post', {}); await refresh(); }); }
async function changeRole(row: Item, role: string) { await perform(async () => { await api(`users/${row.id}/role`, 'put', { role }); await refresh(); }); }
onMounted(() => perform(load));
</script>

<style scoped>
.business-native-page :deep(.el-table__header .cell) { white-space: nowrap; word-break: normal; }
.business-native-page :deep(.el-table__body .cell) { word-break: normal; }
.business-field-control { width: 100%; }
.business-field-control :deep(.el-select), .business-field-control :deep(.el-date-editor), .business-field-control :deep(.el-input-number) { width: 100%; }
</style>
