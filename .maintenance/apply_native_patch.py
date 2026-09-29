"""Apply reviewed source-level integration fixes. Every replacement has an exact precondition."""
from pathlib import Path


def replace(name, before, after):
    path = Path(name)
    source = path.read_text(encoding='utf-8')
    if after in source:
        return
    if source.count(before) != 1:
        raise ValueError('Unexpected source shape: ' + name)
    path.write_text(source.replace(before, after, 1), encoding='utf-8', newline='\n')


replace('workbench/native.py',
    'response.status_code, headers=response.headers, content=bytes(payload)',
    'response.status_code, headers={k: v for k, v in response.headers.items() if k.lower() not in {"content-encoding", "content-length", "transfer-encoding"}}, content=bytes(payload), request=response.request')
replace('workbench/native.py', 'module_name="rnd",', 'module_name=entity.name,')
replace('workbench/native.py',
    'raise PrerequisiteError("原生生成器拒绝请求；未公开含凭据的上游响应")',
    'raise PrerequisiteError(f"原生生成器拒绝请求 (code={value.get(\'code\')})；未公开含凭据的上游响应")')
replace('workbench/filesystem.py', '    "dist",\n}', '    "dist",\n    "logs",\n}')
replace('workbench/native_modules.py',
    '        tables.append(Table(name, metadata, *columns, comment=entity.description))',
    '        for column in columns:\n            if not column.comment:\n                column.comment = column.name\n        tables.append(Table(name, metadata, *columns, comment=entity.description))')
replace('scripts/native_browser.cjs',
    "    const info = await checked(infoResponse);",
    "    const info = await checked(infoResponse);\n    await page.waitForURL(url => !url.hash.includes('login'));")
replace('scripts/build_handbook.py',
    '            "workbench/native_frontend.py",',
    '            "workbench/native_frontend.py",\n            "workbench/native_modules.py",\n            "workbench/native_acceptance.py",')
replace('.github/workflows/native-runtime.yml',
    '      - uses: actions/setup-node@v4',
    '      - uses: actions/cache/restore@v4\n        if: matrix.template == \'yudao-vben\'\n        with:\n          path: ~/.m2/repository\n          key: native-maven-v1-${{ runner.os }}-${{ matrix.revision }}\n      - uses: actions/setup-node@v4')
replace('.github/workflows/native-runtime.yml',
    '      - name: Preserve revisions and actual evidence',
    '      - uses: actions/cache/save@v4\n        if: always() && matrix.template == \'yudao-vben\'\n        with:\n          path: ~/.m2/repository\n          key: native-maven-v1-${{ runner.os }}-${{ matrix.revision }}\n      - name: Preserve revisions and actual evidence')

path = Path('tests/test_native_modules.py')
source = path.read_text(encoding='utf-8')
if 'def test_native_http_response_is_decompressed_once' not in source:
    source += '''

def test_native_http_response_is_decompressed_once():
    import gzip
    import json
    import httpx
    from workbench.native import NativeClient, NativeConfig
    envelope = json.dumps({"openapi": "3.1.0", "paths": {}}).encode()
    def handler(request):
        return httpx.Response(200, headers={"content-encoding": "gzip", "content-type": "application/json"}, content=gzip.compress(envelope))
    client = NativeClient(NativeConfig(base_url="http://127.0.0.1:8001", openapi_path="/openapi.json", token_env="NATIVE_TOKEN", database_url_env="NATIVE_DATABASE_URL"), "lab-token", transport=httpx.MockTransport(handler))
    try:
        assert client.paths == {}
    finally:
        client.close()


def test_every_native_column_has_a_codegen_comment():
    for template in ('fastapiadmin', 'yudao-vben'):
        _, tables, _ = native_metadata(template, acceptance_spec(), URL, 'comments')
        assert all(column.comment for table in tables for column in table.c)
'''
    path.write_text(source, encoding='utf-8', newline='\n')
print('Reviewed native source fixes applied')
