"""Connect tested native runtime entry points without changing native authentication code."""
from pathlib import Path


def replace(name, before, after):
    path = Path(name)
    source = path.read_text(encoding='utf-8')
    if after in source:
        return
    if source.count(before) != 1:
        raise ValueError('Unexpected source shape: ' + name)
    path.write_text(source.replace(before, after, 1), encoding='utf-8', newline='\n')


replace('workbench/native_acceptance.py',
    'assert response.json().get("code", response.status_code) in (400, 422)',
    'assert response.status_code in (400, 422) or response.json().get("code") in (400, 422), "Required-field validation must return a client validation error"')
replace('workbench/native.py',
    'def generate_native(settings, template, plan, destination):\n    config, token, db_url',
    'def generate_native(settings, template, plan, destination):\n    from workbench.native_delivery import managed_generate, runtime_enabled\n\n    if runtime_enabled(settings, template):\n        return managed_generate(settings, template, plan, destination)\n    config, token, db_url')
replace('workbench/native.py',
    '    current = manifest(destination)\n    if current != receipt["files"]',
    '    if receipt.get("execution") == "managed-runtime":\n        from workbench.native_delivery import managed_verify\n\n        return managed_verify(destination, receipt)\n    current = manifest(destination)\n    if current != receipt["files"]')
replace('workbench/native.py',
    'def package_native(destination, report):\n    listing',
    'def package_native(destination, report):\n    if report.get("validation_level") == "runtime":\n        from workbench.native_delivery import managed_package\n\n        return managed_package(destination, report)\n    listing')
replace('workbench/flow.py',
    '原生模板当前只接通原生 CRUD 导出；不接受 Python 规则插件',
    '原生模板使用原生 CRUD 生成器；不接受 Python 规则插件')
replace('workbench/flow.py',
    '        pack = design_pack(plan,',
    '''        if state["template"] != "python-basic":
            from workbench.native_delivery import runtime_config, runtime_enabled
            from workbench.native_modules import validate_plan

            if runtime_enabled(self.settings, state["template"]):
                try:
                    validate_plan(plan)
                    runtime_config(self.settings, state["template"])
                except (ValueError, PrerequisiteError) as exc:
                    reasons.append(str(exc))
        pack = design_pack(plan,''')
replace('workbench/flow.py',
    '原生模板也只对其声明的能力生成，不承诺任意软件。',
    '原生全栈运行模板只支持明确批准的 shared 数据 + 原生角色权限，简单文本/整数/布尔字段单表 CRUD；不能把 per_user 悄悄改成 shared。每个实体至少需要一个必填文本字段用于独立界面验收。实体名称最多20个小写字母/数字/下划线，描述不可包含引号、路径或多行文本。不承诺任意软件。')
replace('workbench/cli.py', 'if __name__ == "__main__":', '''@native_app.command("runtime-config")
def native_runtime_config(template: str):
    """创建原生全栈运行配置；必须显式授权专用空 PostgreSQL 库。"""
    from workbench.native_delivery import write_runtime_example

    typer.echo(str(write_runtime_example(Settings(), template)))


@native_app.command("serve")
def native_serve(run: str):
    """重新打开已验收原生产品；复用开发库，不删库、不重新生成。"""
    from workbench.native_delivery import serve_managed

    try:
        serve_managed(Settings(), run)
    except KeyboardInterrupt:
        typer.echo("原生后端和前端预览已停止。")


if __name__ == "__main__":''')
replace('scripts/build_handbook.py',
    '            "workbench/native_acceptance.py",',
    '            "workbench/native_acceptance.py",\n            "workbench/native_lab.py",\n            "workbench/native_delivery.py",')
replace('workbench/native_modules.py',
    '    for entity in plan.entities:\n        if len(entity.name)',
    '    for entity in plan.entities:\n        if not any(field.kind == "text" and field.required for field in entity.fields):\n            raise ValueError("Native runtime requires a required text field in each entity for independent UI acceptance")\n        if len(entity.name)')
path = Path('workbench/native_acceptance.py')
source = path.read_text(encoding='utf-8')
if 'def wire_name(' not in source:
    source = source.replace('def sample_record(entity, suffix="original"):', '''def wire_name(template, name):
    if template == "fastapiadmin":
        return name
    first, *rest = name.split("_")
    return first + "".join(piece[:1].upper() + piece[1:] for piece in rest)


def sample_record(entity, suffix="original", template="fastapiadmin"):''')
    source = source.replace('        f.name: (', '        wire_name(template, f.name): (')
    source = source.replace('sample_record(entity)', 'sample_record(entity, template=template)')
    for mode in ('updated', 'persistent', 'writer'):
        source = source.replace(f'sample_record(entity, "{mode}")', f'sample_record(entity, "{mode}", template)')
    source = source.replace('invalid.pop(required.name)', 'invalid.pop(wire_name(template, required.name))')
    source = source.replace('str(sample[f.name])', 'str(sample[wire_name(template, f.name)])')
    path.write_text(source, encoding='utf-8', newline='\n')
print('Native runtime entry points connected')
