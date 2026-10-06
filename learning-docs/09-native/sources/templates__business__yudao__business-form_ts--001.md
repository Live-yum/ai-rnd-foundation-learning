# templates/business/yudao/business-form.ts · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：Vben合同表单与关联选项。** 在原生Form Schema中移出状态/负责人等受控字段，把关系键接为服务器限定的可识别选择项；关系选择器按可读标签搜索并保留虚拟滚动，选项多时也能找到新记录，不扩大后端权限范围。保留字段校验和类型。

**对应关系：** 生成Vben表单 → 本辅助函数 → 合同关系API与原生表单组件。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `templates/business/yudao/business-form.ts`；**本文件共有 1 段**。本段覆盖源文件 L1–L126。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`9039`。本段原文以LF换行结束。

<!-- learning-source: {"path": "templates/business/yudao/business-form.ts", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "6db8570337cfe8781fe82e6f2abe90d68a85909cf4dedacb27524c8ab272725b"} -->
````typescript
// templates/business/yudao/business-form.ts
import type { VbenFormSchema } from '#/adapter/form';
import type { VxeTableGridOptions } from '#/adapter/vxe-table';
import { requestClient } from '#/api/request';
interface Field { name: string; label: string; kind: string; required: boolean; min_length: number; max_length: number; choices: string[]; choice_labels: Record<string, string>; searchable: boolean; filterable: boolean; date_range: boolean; minimum?: number; maximum?: number; exclusive_minimum?: number; exclusive_maximum?: number; pattern?: string; example?: string }
interface Reference { target: string; label: string }
interface BusinessFormSpec { fields: Field[]; controlled: string[]; references: Record<string, Reference>; statusField: string }
const specs: Record<string, BusinessFormSpec> = __FORM_CONFIG__;
const wire = (name: string) => name.replace(/_([a-z])/g, (_, char: string) => char.toUpperCase());
const systemLabels: Record<string, string> = { id: '编号', createdBy: '创建人', createdAt: '创建时间', createTime: '创建时间', updatedAt: '更新时间', archivedAt: '归档时间' };
const recordField = (name: string) => name === 'createTime' ? 'createdAt' : name;
const fieldSpec = (entity: string, name: string) => specs[entity]?.fields.find(field => wire(field.name) === wire(name));

export function businessFieldLabel(entity: string, name: string): string {
  const field = fieldSpec(entity, name);
  return field ? field.label || field.name : systemLabels[name] || name;
}
export function businessTimestamp(value: unknown): string {
  if (value === null || value === undefined || value === '') return '—';
  if (typeof value !== 'string' && typeof value !== 'number') return '—';
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? String(value) : `${date.toISOString().slice(0, 19).replace('T', ' ')} UTC`;
}
export function businessDisplayValue(entity: string, name: string, row: object | null | undefined, fallback?: unknown): string {
  const property = recordField(wire(name));
  const display: unknown = row ? Reflect.get(row, '_display') : undefined;
  if (display && typeof display === 'object') {
    const label: unknown = Reflect.get(display, property);
    if (typeof label === 'string') return label;
  }
  const value: unknown = row && Reflect.has(row, property) ? Reflect.get(row, property) : fallback;
  if (value === null || value === undefined || value === '') return '—';
  const field = fieldSpec(entity, name);
  if (field?.kind === 'datetime' || ['createdAt', 'updatedAt', 'archivedAt'].includes(property)) return businessTimestamp(value);
  if (field?.kind === 'enum') return field.choice_labels[String(value)] || String(value);
  if (field?.kind === 'boolean') return value ? '是' : '否';
  if (field?.kind === 'date' && typeof value === 'string') return value.slice(0, 10);
  return String(value);
}
export function businessDetails(entity: string, row: Record<string, unknown> | null) {
  if (!row) return [];
  return ['id', ...(specs[entity]?.fields.map(field => wire(field.name)) || []), 'createdBy', 'createdAt', 'updatedAt', 'archivedAt']
    .map(field => ({ field, label: businessFieldLabel(entity, field), value: businessDisplayValue(entity, field, row) }));
}
export function businessStateLabel(entity: string, value: string): string {
  const field = fieldSpec(entity, specs[entity]?.statusField || '');
  return field?.choice_labels[value] || value;
}
export function businessActionLabel(action: string): string {
  const labels: Record<string, string> = { created: '创建记录', updated: '更新记录', assign: '分配负责人', transition: '变更状态', add_note: '添加备注', archived: '归档记录', role_granted: '授予角色', role_revoked: '撤销角色' };
  return labels[action] || action;
}
/** Keep the native Vxe grid and its selection/action slots; format only visible data cells. */
export function businessGridColumns<T extends object>(entity: string, original: VxeTableGridOptions<T>['columns']): VxeTableGridOptions<T>['columns'] {
  return original?.map((column): NonNullable<VxeTableGridOptions<T>['columns']>[number] => {
    if (!column.field) return column.slots ? { ...column, width: 240, showHeaderOverflow: true } : column;
    const field = fieldSpec(entity, column.field);
    return { ...column, title: businessFieldLabel(entity, column.field),
      minWidth: field?.kind === 'datetime' || ['createTime', 'createdAt', 'updatedAt', 'archivedAt'].includes(column.field) ? 220 : field?.max_length && field.max_length > 500 ? 240 : 160,
      showHeaderOverflow: true, showOverflow: 'tooltip',
      formatter: ({ row, cellValue }) => businessDisplayValue(entity, column.field || '', row, cellValue),
    };
  });
}

function fieldSchema(entity: string, item: VbenFormSchema, search: boolean): VbenFormSchema {
  const spec = specs[entity];
  const field = fieldSpec(entity, item.fieldName);
  if (!spec || !field) return { ...item, label: businessFieldLabel(entity, item.fieldName) };
  const label = field.label || field.name;
  const result: VbenFormSchema = { ...item, label, rules: !search && field.required ? 'required' : undefined };
  const relation = spec.references[field.name];
  if (relation) {
    result.component = 'ApiSelect';
    result.componentProps = {
      api: () => relation.target === '$users' ? requestClient.get('/infra/rnd-business/users') : requestClient.get('/infra/rnd-business/references', { params: { entity: relation.target } }),
      labelField: relation.label, valueField: 'id', allowClear: search || !field.required,
      // ApiComponent maps the declared relation label to option.label. Keep
      // virtualization while making later authorized records findable by name.
      showSearch: true, optionFilterProp: 'label',
    };
  } else if (field.kind === 'enum') {
    result.component = 'Select'; result.componentProps = { options: field.choices.map(value => ({ label: field.choice_labels[value] || value, value })), allowClear: search || !field.required };
  } else if (field.kind === 'boolean') {
    result.component = 'Select'; result.componentProps = { options: [{ label: '是', value: true }, { label: '否', value: false }], allowClear: search || !field.required };
  } else if (field.kind === 'datetime' || field.kind === 'date') {
    result.component = 'DatePicker'; result.componentProps = field.kind === 'datetime'
      ? { showTime: true, format: 'YYYY-MM-DD HH:mm:ss [UTC]', valueFormat: 'YYYY-MM-DDTHH:mm:ss[Z]' }
      : { format: 'YYYY-MM-DD', valueFormat: 'YYYY-MM-DD' };
    if (field.kind === 'datetime') result.label = `${label} (UTC)`;
  } else if (field.kind === 'integer') {
    result.component = 'InputNumber'; result.componentProps = { precision: 0, min: search ? -2147483648 : Math.max(field.minimum ?? -2147483648, (field.exclusive_minimum ?? -2147483649) + 1), max: search ? 2147483647 : Math.min(field.maximum ?? 2147483647, (field.exclusive_maximum ?? 2147483648) - 1) };
  } else {
    result.component = !search && field.max_length > 500 ? 'Textarea' : 'Input';
    result.componentProps = { maxlength: field.max_length, minlength: field.min_length };
  }
  result.componentProps = { ...(result.componentProps as Record<string, unknown>), 'data-testid': `business-field-${field.name}`, placeholder: `${relation || ['enum', 'boolean', 'date', 'datetime'].includes(field.kind) ? '请选择' : '请输入'}${label}` };
  return result;
}
/** Preserve the generated native Form; replace only contract-driven field widgets. */
export function businessFormSchema(entity: string, original: VbenFormSchema[]): VbenFormSchema[] {
  const spec = specs[entity];
  if (!spec) throw new Error('Unknown native business form');
  return original.filter(item => !spec.controlled.map(wire).includes(item.fieldName)).map(item => fieldSchema(entity, item, false));
}
export function businessSearchSchema(entity: string, original: VbenFormSchema[]): VbenFormSchema[] {
  if (!specs[entity]) throw new Error('Unknown native business form');
  return original.flatMap(item => {
    const field = fieldSpec(entity, item.fieldName);
    if (!field || !(field.searchable || field.filterable || field.date_range)) return [];
    const input = fieldSchema(entity, item, true);
    if (!field.date_range) return [input];
    return [
      ...(field.filterable ? [input] : []),
      { ...input, fieldName: wire(field.name) + '_from', label: `${field.label || field.name} 起始（含）` },
      { ...input, fieldName: wire(field.name) + '_to', label: `${field.label || field.name} 截止（含）` },
    ];
  });
}
export function businessPayload<T extends object>(entity: string, values: T): T {
  const spec = specs[entity];
  if (!spec) throw new Error('Unknown native business form');
  const allowed = new Set(['id', ...spec.fields.filter(field => !spec.controlled.includes(field.name)).map(field => wire(field.name))]);
  const result = { ...values };
  for (const name of Object.keys(result)) if (!allowed.has(name)) Reflect.deleteProperty(result, name);
  return result;
}
````
