"""Actual native generation, mounting, permissions, CRUD, restart and browser acceptance."""
import os
import traceback
from pathlib import Path
from workbench.domain import digest
from workbench.filesystem import atomic_text, manifest, write_json
from workbench.native_acceptance import check_generated_persistence, generated_crud, generated_permissions
from workbench.native_environment import bootstrap_database, copy_source, install_backend, login, native_environment, running_backend
from workbench.native_frontend import build_frontend, frontend_environment, frontend_preview
from workbench.native_modules import create_native_tables, generate_modules, validate_plan
from workbench.settings import ROOT
from workbench.tools import run_command


def generated_browser(template, front_url, reports):
    command = ['node', str(ROOT / 'scripts/native_browser.cjs'), template, front_url, str(reports.resolve()), str(ROOT / '.native/browser/node_modules/playwright'), str((reports / 'browser-targets.json').resolve())]
    try:
        result = run_command(command, ROOT, 240, {'NODE_OPTIONS': '--dns-result-order=ipv4first', 'PLAYWRIGHT_BROWSERS_PATH': os.environ.get('PLAYWRIGHT_BROWSERS_PATH', '0')})
    except Exception as exc:
        atomic_text(reports / 'browser.log', getattr(exc, 'log', str(exc)))
        raise
    atomic_text(reports / 'browser.log', result['log'])


def run_acceptance(template, source, output, frontend_source, url, reports, plan):
    """Shared by CLI and CI; never reset an existing database or workspace."""
    plan = validate_plan(plan)
    source, output, reports = Path(source).resolve(), Path(output).resolve(), Path(reports).resolve()
    reports.mkdir(parents=True, exist_ok=True)
    before = manifest(source)
    copy_source(source, output)
    backend = output / 'backend' if template == 'fastapiadmin' else output
    if template == 'fastapiadmin':
        frontend = output / 'frontend/web'
    else:
        frontend = output.parent / 'frontend-product'
        copy_source(frontend_source, frontend)
    env = native_environment(template, backend, url, 8001 if template == 'fastapiadmin' else 48080)
    write_json(reports / 'approved-spec.json', plan.model_dump())
    write_json(reports / 'acceptance.json', {'template': template, 'generated_runtime_verified': False})
    try:
        bootstrap_database(template, backend, url)
        install_backend(template, backend, reports / 'baseline')
        with running_backend(template, backend, env, reports / 'baseline') as (base_url, openapi):
            token = login(template, base_url)
            write_json(reports / 'baseline/login.json', {'native_login': True})
            mapping = create_native_tables(template, plan, url, digest(plan.model_dump()), reports)
            targets = generate_modules(template, backend, frontend, base_url, openapi, token, mapping, plan, reports)
        if template == 'yudao-vben':
            install_backend(template, backend, reports / 'generated-build')
        with running_backend(template, backend, env, reports / 'generated') as (base_url, _):
            token = login(template, base_url)
            records = generated_crud(template, base_url, token, targets, plan)
            write_json(reports / 'generated/crud.json', records)
            write_json(reports / 'generated/permissions.json', generated_permissions(template, base_url, token, targets, plan))
        with running_backend(template, backend, env, reports / 'restart') as (base_url, _):
            token = login(template, base_url)
            write_json(reports / 'restart/persistence.json', check_generated_persistence(template, base_url, token, targets, records))
            write_json(reports / 'browser-targets.json', targets)
            front_env = frontend_environment(template, base_url)
            build_frontend(template, frontend, front_env, reports)
            with frontend_preview(template, frontend, front_env, reports) as front_url:
                generated_browser(template, front_url, reports)
        assert before == manifest(source), 'Original native source was modified'
        write_json(reports / 'generated-manifest.json', {'backend': manifest(backend), 'frontend': manifest(frontend)})
        report = {'template': template, 'scope': 'generated-native-modules', 'generated_runtime_verified': True, 'native_codegen': True, 'automatic_mount': True, 'menu_and_permissions': True, 'real_crud': True, 'restart_persistence': True, 'frontend_build': True, 'frontend_typecheck': True, 'real_browser': True, 'entities': [e.name for e in plan.entities], 'spec_digest': digest(plan.model_dump()), 'source_unmodified': True, 'data_scope': 'shared-with-native-role-permissions'}
        write_json(reports / 'acceptance.json', report)
        print('Generated native modules, menus, permissions, CRUD, restart, frontend build and browser PASS')
        return report
    except Exception as exc:
        frame = traceback.extract_tb(exc.__traceback__)[-1]
        atomic_text(reports / 'failure.log', f'{type(exc).__name__} at {Path(frame.filename).name}:{frame.lineno} ({frame.name}): {exc}\n' + getattr(exc, 'log', ''))
        raise
