import type { VbenFormSchema } from '#/adapter/form';
import { requestClient } from '#/api/request';
interface Field { name: string; kind: string; required: boolean; min_length: number; max_length: number; choices: string[] }
interface Reference { target: string; label: string }
interface BusinessFormSpec { fields: Field[]; controlled: string[]; references: Record<string, Reference> }
const specs: Record<string, BusinessFormSpec> = __FORM_CONFIG__;
const wire = (name: string) => name.replace(/_([a-z])/g, (_, char: string) => char.toUpperCase());

/** Preserve the generated native Form; replace only contract-driven field widgets. */
export function businessFormSchema(entity: string, original: VbenFormSchema[]): VbenFormSchema[] {
  const spec = specs[entity];
  if (!spec) throw new Error('Unknown native business form');
  return original.filter(item => !spec.controlled.map(wire).includes(item.fieldName)).map(item => {
    const field = spec.fields.find(value => wire(value.name) === item.fieldName);
    if (!field) return item;
    const result: VbenFormSchema = { ...item, rules: field.required ? 'required' : undefined };
    const relation = spec.references[field.name];
    if (relation) {
      result.component = 'ApiSelect';
      result.componentProps = {
        api: () => relation.target === '$users' ? requestClient.get('/infra/rnd-business/users') : requestClient.get('/infra/rnd-business/references', { params: { entity: relation.target } }),
        labelField: relation.label, valueField: 'id', allowClear: !field.required,
      };
    } else if (field.kind === 'enum') {
      result.component = 'Select'; result.componentProps = { options: field.choices.map(value => ({ label: value, value })), allowClear: !field.required };
    } else if (field.kind === 'boolean') {
      result.component = 'Select'; result.componentProps = { options: [{ label: '是', value: true }, { label: '否', value: false }], allowClear: !field.required };
    } else if (field.kind === 'datetime' || field.kind === 'date') {
      result.component = 'DatePicker'; result.componentProps = field.kind === 'datetime'
        ? { showTime: true, format: 'YYYY-MM-DD HH:mm:ss [UTC]', valueFormat: 'YYYY-MM-DDTHH:mm:ss[Z]' }
        : { format: 'YYYY-MM-DD', valueFormat: 'YYYY-MM-DD' };
      if (field.kind === 'datetime') result.label = `${String(item.label)} (UTC)`;
    } else if (field.kind === 'integer') {
      result.component = 'InputNumber'; result.componentProps = { precision: 0 };
    } else {
      result.component = field.max_length > 500 ? 'Textarea' : 'Input';
      result.componentProps = { maxlength: field.max_length, minlength: field.min_length };
    }
    result.componentProps = { ...(result.componentProps as Record<string, unknown>), 'data-testid': `business-field-${field.name}`, placeholder: `请输入${field.name}` };
    return result;
  });
}

export function businessPayload(entity: string, values: Record<string, unknown>): Record<string, unknown> {
  const spec = specs[entity];
  if (!spec) throw new Error('Unknown native business form');
  const allowed = new Set(['id', ...spec.fields.filter(field => !spec.controlled.includes(field.name)).map(field => wire(field.name))]);
  return Object.fromEntries(Object.entries(values).filter(([name]) => allowed.has(name)));
}
