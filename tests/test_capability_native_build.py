"""Bounded native Rollup scheduling; OS isolation remains the security boundary."""

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

from scripts.capability_guard import RESOURCE_LIMITS
from workbench import capability_native_runtime as native
from workbench.capability_dependencies import NATIVE_NODE_ROOT, NODE


@pytest.fixture
def node():
    value = shutil.which("node")
    if not value:
        if any(
            os.environ.get(key) == "1"
            for key in ("RND_REQUIRE_NODE_TESTS", "RND_REQUIRE_NATIVE_VITE_TESTS")
        ):
            pytest.fail("Node is required by this job")
        pytest.skip("Node tooling unavailable")
    return value


def local_command(root):
    command = native.native_frontend_build_command()
    sealed = json.dumps(NATIVE_NODE_ROOT + "/vite/dist/node/index.js")
    assert command.argv[3].count(sealed) == 1
    # URI transport is portable to Windows and does not expand the production
    # command argument bound when a pytest temporary path happens to be long.
    command.argv[3] = command.argv[3].replace(
        sealed, json.dumps((root / "vite/dist/node/index.js").as_uri())
    )
    return command


def bounded_run(node, command, root):
    # Consumer-local paths stand in for the immutable runtime mount in these
    # fixtures only. Execute the exact controller-generated JavaScript body.
    def limits():
        import resource

        resource.setrlimit(resource.RLIMIT_NOFILE, (256, 256))

    environment = {"PATH": os.environ.get("PATH", ""), "HOME": str(root), "CI": "true"}
    # Windows executable/temporary-directory discovery needs these ordinary OS
    # values; do not inherit unrelated credentials into the fixture process.
    for key in ("SYSTEMROOT", "SystemRoot", "WINDIR", "TEMP", "TMP"):
        if key in os.environ:
            environment[key] = os.environ[key]
    return subprocess.run(
        [node, *command.argv[1:]],
        cwd=root,
        env=environment,
        capture_output=True,
        text=True,
        timeout=30,
        preexec_fn=limits if os.name == "posix" else None,
    )


def test_native_build_keeps_sealed_tool_mode_and_existing_resource_limit():
    command = native.native_frontend_build_command()
    assert command.cwd == "frontend/web"
    assert command.argv[:3] == [NODE, "--input-type=module", "--eval"]
    assert command.argv[3].startswith(
        "import {build} from " + json.dumps(NATIVE_NODE_ROOT + "/vite/dist/node/index.js")
    )
    assert "mode:'production'" in command.argv[3]
    assert "maxParallelFileOps:32" in command.argv[3]
    assert "external:" not in command.argv[3]
    assert "configFile:" not in command.argv[3]
    assert "catch" not in command.argv[3]
    assert RESOURCE_LIMITS["RLIMIT_NOFILE"] == 256
    assert native.native_prepare_commands()[2].argv == [
        "pnpm",
        "exec",
        "vite",
        "build",
        "--mode",
        "production",
    ]
    assert native.native_prepare_commands()[3].argv == [
        "pnpm",
        "exec",
        "vue-tsc",
        "--noEmit",
        "--skipLibCheck",
    ]


@pytest.mark.parametrize("case", ["normal", "override", "late-override", "removed", "error"])
def test_exact_wrapper_hooks_and_errors_with_data_only_api_fixture(node, tmp_path, case):
    module = tmp_path / "vite/dist/node/index.js"
    module.parent.mkdir(parents=True)
    (tmp_path / "package.json").write_text('{"type":"module"}')
    module.write_text(
        "import assert from 'node:assert/strict';\n"
        + f"const testCase = {json.dumps(case)};\n"
        + """
export async function build(config) {
  assert.deepEqual(Object.keys(config).sort(), ['build','mode','plugins']);
  assert.equal(config.mode, 'production');
  assert.deepEqual(config.build, {rollupOptions:{maxParallelFileOps:32}});
  assert.equal(config.plugins.length, 1);
  const guard = config.plugins[0];
  assert.equal(guard.enforce, 'post');
  assert.equal(guard.options.order, 'post');
  if (testCase === 'error') throw new Error('original config failure');
  if (testCase === 'removed') return;
  const output = {manualChunks: () => 'retained'};
  const plugins = [{name:'original'}];
  const initialLimit = testCase === 'override' ? 4096 : 32;
  const original = {input:'index.html',output,plugins,maxParallelFileOps:initialLimit};
  const options = guard.options.handler(original);
  assert.equal(options.maxParallelFileOps,32);
  assert.equal(options.output,output);
  assert.equal(options.plugins,plugins);
  assert.equal(options.input,'index.html');
  assert.equal(original.maxParallelFileOps,initialLimit);
  if (testCase === 'late-override') options.maxParallelFileOps = 2048;
  guard.buildStart(options);
  console.log('fixture hooks passed');
}
"""
    )
    result = bounded_run(node, local_command(tmp_path), tmp_path)
    if case in {"normal", "override"}:
        assert result.returncode == 0, result.stderr
        assert "fixture hooks passed" in result.stdout
    else:
        assert result.returncode != 0
        assert {
            "late-override": "native-build-file-limit",
            "removed": "native-build-check-missing",
            "error": "original config failure",
        }[case] in result.stderr


def require_real_vite():
    # Actual-tool coverage is mandatory after native baseline preparation in CI.
    # Reuse the pinned installed tree; no download/install or changed lock.
    root = os.environ.get("RND_NATIVE_TEST_NODE_MODULES")
    if not root:
        if os.environ.get("RND_REQUIRE_NATIVE_VITE_TESTS") == "1":
            pytest.fail("Native Vite tool tree is required by this job")
        pytest.skip("Set RND_NATIVE_TEST_NODE_MODULES to an existing pinned native tool tree")
    root = Path(root).resolve()
    assert (root / "vite/dist/node/index.js").is_file()
    assert json.loads((root / "vite/package.json").read_text())["version"] == "7.3.3"
    return root


@pytest.fixture
def real_vite():
    return require_real_vite()


def test_required_native_vite_cannot_be_silently_skipped(monkeypatch, tmp_path):
    monkeypatch.setenv("RND_REQUIRE_NATIVE_VITE_TESTS", "1")
    monkeypatch.delenv("RND_NATIVE_TEST_NODE_MODULES", raising=False)
    with pytest.raises(pytest.fail.Exception, match="required"):
        require_real_vite()
    monkeypatch.setenv("RND_NATIVE_TEST_NODE_MODULES", str(tmp_path))
    with pytest.raises(AssertionError):
        require_real_vite()
    module = tmp_path / "vite/dist/node/index.js"
    module.parent.mkdir(parents=True)
    module.write_text("export const placeholder = true;")
    (tmp_path / "vite/package.json").write_text('{"version":"0.0.0"}')
    with pytest.raises(AssertionError):
        require_real_vite()


@pytest.mark.node_tools
@pytest.mark.parametrize(
    "case",
    [
        "normal",
        "config",
        "resolved",
        "options",
        "post-options",
        "late-override",
        "removed",
        "error",
    ],
)
def test_real_vite_preserves_config_and_bounds_candidate_hooks(node, real_vite, tmp_path, case):
    (tmp_path / "package.json").write_text('{"type":"module"}')
    (tmp_path / "index.html").write_text('<script type="module" src="/main.js"></script>')
    (tmp_path / "main.js").write_text("import {value} from '@retained'; console.log(value);")
    (tmp_path / "retained.js").write_text("export const value = 'original alias retained';")
    hook = {
        "normal": "",
        "config": "config(){return {build:{rollupOptions:{maxParallelFileOps:4096}}}},",
        "resolved": "configResolved(c){c.build.rollupOptions.maxParallelFileOps=4096},",
        "options": "options(o){return {...o,maxParallelFileOps:4096}},",
        "post-options": "options:{order:'post',handler(o){return {...o,maxParallelFileOps:4096}}},",
        "late-override": "configResolved(c){c.plugins.push({name:'late',options:{order:'post',handler(o){return {...o,maxParallelFileOps:4096}}}})},",
        "removed": "configResolved(c){c.plugins=c.plugins.filter(p=>p.name!=='rnd:fd32')},",
        "error": "config(){throw new Error('original config failure')},",
    }[case]
    (tmp_path / "vite.config.mjs").write_text(
        "import {writeFileSync} from 'node:fs';\n"
        "import {fileURLToPath} from 'node:url';\n"
        "export default {\n"
        "resolve:{alias:{'@retained':fileURLToPath(new URL('./retained.js',import.meta.url))}},\n"
        "build:{rollupOptions:{maxParallelFileOps:1000,output:{entryFileNames:'kept/[name].js'}}},\n"
        "plugins:[{name:'original-plugin',"
        + hook
        + "generateBundle(){writeFileSync('original-plugin-ran.txt','yes')}}]\n};\n"
    )
    original = (tmp_path / "vite.config.mjs").read_bytes()
    result = bounded_run(node, local_command(real_vite), tmp_path)
    assert (tmp_path / "vite.config.mjs").read_bytes() == original
    if case in {"late-override", "removed", "error"}:
        assert result.returncode != 0
        assert {
            "late-override": "native-build-file-limit",
            "removed": "native-build-check-missing",
            "error": "original config failure",
        }[case] in result.stderr
    else:
        assert result.returncode == 0, result.stderr
        assert (tmp_path / "dist/index.html").is_file()
        assert (tmp_path / "dist/kept/index.js").is_file()
        assert "original alias retained" in (tmp_path / "dist/kept/index.js").read_text()
        assert (tmp_path / "original-plugin-ran.txt").read_text() == "yes"


def test_native_ci_requires_real_vite_after_baseline_before_source_admission():
    path = Path(__file__).resolve().parents[1] / ".github/workflows/native-capability-profile.yml"
    workflow = path.read_text()
    baseline = workflow.index("- name: Produce exact native baseline")
    check = workflow.index("- name: Require bounded native Vite scheduling")
    admission = workflow.index("- name: Build and register exact native offline dependency profile")
    assert baseline < check < admission
    step = workflow[check : workflow.index("      - name:", check + 1)]
    assert "RND_REQUIRE_NATIVE_VITE_TESTS: '1'" in step
    assert "RND_REQUIRE_NODE_TESTS: '1'" in step
    assert "${{ github.workspace }}/.native/tool-product/frontend/web/node_modules" in step
    assert "uv run pytest -q tests/test_capability_native_build.py" in step
