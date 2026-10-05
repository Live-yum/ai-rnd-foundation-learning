# tests/test_daytona_capability_profile.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts`、`scripts.daytona_bootstrap`、`workbench.capability_isolation`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `dependency_record`（L24–L35）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`profile.sha256`、`(profile.ROOT / "templates/product" / name).read_bytes`。 返回路径：L25的`{ "schema": 1, "profile": "python-basic", "image_id": SNAPSHOT, "manifest_sha256": "1" * 6…`。
- `base_config`（L38–L50）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`local.IMAGES.items`、`local.gateway_service`、`copy.deepcopy`。 返回路径：L50的`{"services": services, "networks": copy.deepcopy(local.NETWORKS)}`。
- `test_profile_transformation_preserves_general_defaults_and_all_other_fields`（L53–L74）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L59断言`original == untouched`；L60断言`result["name"] == profile.PROJECT`；L61断言`result["services"]["runner"]["image"] == RUNNER`；L62断言`result["services"]["runner"]["environment"]["USE_SNAPSHOT_ENTRYPOINT"] == "false"`；L63断言`result["services"]["runner"]["privileged"] is True`；L64断言`result["services"]["runner"]["environment"]["RESOURCE_LIMITS_DISABLED"] == "true"`；L65断言`result["services"]["api"]["environment"]["DEFAULT_SNAPSHOT"] == image`；L67断言`"USE_SNAPSHOT_ENTRYPOINT" not in original["services"]["runner"]["environment"]`。后续分支沿下方源码相同行号继续阅读。 调用`base_config`、`copy.deepcopy`、`profile.render_profile`、`local.IMAGES["runner"].startswith`、`snapshot_resources`、`pytest.raises`、`profile.profile_directory`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `snapshot_inspect`（L77–L95）：不接收显式业务参数，从已配置对象/模块读取依赖。 调用`profile.recipe_identity`。 返回路径：L79的`{ "Id": SNAPSHOT, "Os": "linux", "Architecture": "amd64", "RepoDigests": ["127.0.0.1:6000/…`。
- `test_snapshot_requires_declared_control_identity_and_no_inherited_command`（L108–L114）：接收`field`、`value`。 调用`snapshot_inspect`、`profile.recipe_identity`、`profile.validate_image`、`pytest.raises`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_runner_requires_the_explicit_normal_daemon_entrypoint`（L117–L125）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L120遍历`([], ["USE_SNAPSHOT_ENTRYPOINT=true"])`。 调用`snapshot_inspect`、`profile.recipe_identity`、`pytest.raises`、`profile.validate_image`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `source_fixture`（L128–L169）：接收`tmp_path`、`monkeypatch`。 控制顺序：L139遍历`profile.RECIPE_PATHS`。 调用`context.mkdir`、`path.parent.mkdir`、`path.write_text`、`"".join`、`difflib.unified_diff`、`source.splitlines`、`source.replace(profile.OLD, profile.NEW) .replace(profile.LIMIT_A…`、`source.replace(profile.OLD, profile.NEW) .replace`、`source.replace`等。 返回路径：L169的`root, context, source, workspace`。
- `source_fixture.export`（L155–L163）：接收`directory`、`command`、`target`。 调用`Path`、`path.parent.mkdir`、`path.write_bytes`、`source.encode`、`(Path(target) / "go.work").write_bytes`、`workspace.encode`、`(Path(target) / "apps/runner/go.mod").write_bytes`、`(Path(target) / "apps/runner/go.sum").write_bytes`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_source_preimage_and_patch_are_exact_and_module_inputs_are_preserved`（L172–L182）：接收`tmp_path`、`monkeypatch`。 控制顺序：L175断言`(context / profile.SOURCE_FILE).read_text() == source.replace( profile.OLD, profile.N…`；L178断言`(context / "go.work").read_text() == workspace`；L179断言`(context / "apps/runner/go.mod").read_text() == "module fixture\ngo 1.25.5\n"`；L180断言`(context / "go.work.sum").read_text() == "fixture v1 h1:fixture\n"`；L181断言`record["source_sha"] == profile.DAYTONA_SOURCE`；L182断言`(context / "capability-build/NOTICE").is_file()`。 调用`source_fixture`、`profile.source_context`、`(context / profile.SOURCE_FILE).read_text`、`source.replace( profile.OLD, profile.NEW ).replace`、`source.replace`、`(context / "go.work").read_text`、`(context / "apps/runner/go.mod").read_text`、`(context / "go.work.sum").read_text`、`(context / "capability-build/NOTICE").is_file`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_custom_source_patch_binds_only_its_reviewed_primary_bridge`（L185–L195）：接收`tmp_path`、`monkeypatch`。 控制顺序：L190断言`source.count(assignment) == 1`；L192断言`custom.index(assignment) < custom.index("pidLimit := int64(256)")`；L193断言`custom.index(assignment) < custom.index('"rnd-source-native-"')`；L194断言`"Privileged: false" in source`；L195断言`"NetworkMode" not in source.split("// Custom-source executions", 1)[0]`。 调用`source_fixture`、`profile.source_context`、`(context / profile.SOURCE_FILE).read_text`、`source.count`、`source.split`、`custom.index`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_custom_source_patch_pins_cpu_memory_and_no_extra_swap_independent_of_global_flag`（L198–L209）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L202断言`'if strings.HasPrefix(sandboxDto.Name, "rnd-source-") {' in custom`；L203断言`"resourceLimitsDisabled" not in profile.LIMIT_INSERT`；L204断言`"hostConfig.CPUPeriod = 100000" in custom`；L205断言`"hostConfig.CPUQuota = 100000" in custom`；L206断言`"hostConfig.Memory = 2 * 1024 * 1024 * 1024" in custom`；L207断言`"hostConfig.CPUQuota = 200000" in native`；L208断言`"hostConfig.Memory = 6 * 1024 * 1024 * 1024" in native`；L209断言`native.endswith("\t\t}\n\t\thostConfig.MemorySwap = hostConfig.Memory\n\t}\n")`。 调用`profile.LIMIT_INSERT.split`、`native.endswith`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_shared_memory_patch_is_exact_and_only_changes_the_native_container_branch`（L212–L230）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L217遍历`( 'hostConfig.IpcMode = container.IpcMode("private")', "hostConfi…`；L221断言`native.count(statement) == 1`；L222断言`statement not in custom + after_native + profile.NEW`；L223断言`"/dev/shm" not in profile.LIMIT_INSERT`；L224断言`"Binds" not in profile.LIMIT_INSERT and "Mounts" not in profile.LIMIT_INSERT`；L227断言`profile.SOURCE_BLOB == "d5a97203afa87c3fa0065702723c41645bf284b6"`；L228断言`profile.sha256(patch) == "637d72fa9426bd186dc729c20a2f47e8b138140d6a339299e0ab59c3c18…`。 调用`profile.LIMIT_INSERT.split`、`native.split`、`native.count`、`(profile.ROOT / "tools/daytona/capability-runner.patch").read_byt…`、`profile.sha256`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_complete_source_resource_mapping_preserves_strict_bounds`（L234–L260）：接收`native`。 控制顺序：L247断言`proof["cpu_quota"] == quota`；L248断言`proof["memory"] == proof["memory_swap"] == memory`；L249遍历`( ("CpuPeriod", 0), ("CpuQuota", 0), ("CpuQuota", quota + 1), ("M…`。 调用`profile.require_execution_resources`、`pytest.raises`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_source_drift_fails_closed_before_any_build`（L264–L274）：接收`tmp_path`、`monkeypatch`、`changed`。 控制顺序：L266按`changed == "source"`分支；L268按`changed == "workspace"`分支。 调用`source_fixture`、`monkeypatch.setattr`、`(root / "tools/daytona/capability-runner.patch").open`、`file.write`、`pytest.raises`、`profile.source_context`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `application_inspect`（L277–L308）：不接收显式业务参数，从已配置对象/模块读取依赖。 返回路径：L278的`{ "Name": "/" + SANDBOX, "Image": SNAPSHOT, "State": {"Running": True}, "Config": { "User"…`。
- `inspection`（L312–L348）：接收`tmp_path`、`monkeypatch`。 调用`dependency_record`、`application_inspect`、`monkeypatch.setattr`。 返回路径：L348的`tmp_path, outer, inner, calls`。
- `inspection.docker`（L339–L345）：接收`*args`、`**kwargs`。 控制顺序：L341按`"info" in args`分支；L343按`"network" in args`分支。 调用`calls.append`、`json.dumps`、`inner.get`。 返回路径：L342的`json.dumps(inner.get("engine_security", ["name=seccomp,profile=builtin"]))`；L344的`json.dumps(inner["bridge_inspect"])`；L345的`json.dumps([outer if args[0] == "container" else inner])`。
- `execution_inspection`（L352–L371）：接收`inspection`。 调用`inner["HostConfig"].update`、`inner["Mounts"].append`。 返回路径：L371的`inspection`。
- `native_inspection`（L375–L392）：接收`execution_inspection`、`monkeypatch`。 调用`copy.deepcopy`、`profile.require_profile`、`monkeypatch.setattr`、`inner["HostConfig"].update`。 返回路径：L392的`execution_inspection`。
- `test_native_inspection_binds_private_shared_memory_without_expanding_mounts`（L395–L411）：接收`native_inspection`。 控制顺序：L400断言`proof["shared_memory"] == {"ipc_mode": "private", "size_bytes": 67108864}`；L401断言`type(proof["shared_memory"]["size_bytes"]) is int`；L402断言`proof["resource_limits"] == { "cpu_period": 100000, "cpu_quota": 200000, "memory": 6 …`；L410断言`proof["trusted_readonly_binary_mounts"] is True`；L411断言`len(calls) == 4`。 调用`profile.inspect_created_sandbox`、`type`、`len`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_shared_memory_rejects_missing_changed_and_untyped_inspection`（L435–L456）：接收`native_inspection`、`require_resources`、`field`、`value`。 控制顺序：L439按`value is None`分支；L450断言`error.value.diagnostic() == { "container_rejection": "shared_memory", "shared_memory_…`；L455断言`"secret" not in json.dumps(error.value.diagnostic())`；L456断言`len(calls) == 3`。 调用`inner["HostConfig"].pop`、`pytest.raises`、`profile.inspect_created_sandbox`、`error.value.diagnostic`、`json.dumps`、`len`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_sqlite_inspection_keeps_prior_ipc_policy_without_native_shared_memory`（L460–L468）：接收`execution_inspection`、`ipc_mode`。 控制顺序：L464按`ipc_mode is not None`分支；L467断言`"shared_memory" not in proof`；L468断言`proof["resource_limits"]["memory"] == 2 * 1024**3`。 调用`profile.inspect_created_sandbox`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_shared_memory_preserves_all_other_container_predicates`（L489–L495）：接收`native_inspection`、`mutation`。 调用`mutation`、`pytest.raises`、`profile.inspect_created_sandbox`、`pytest.mark.parametrize`、`row["HostConfig"].update`、`row["Mounts"].append`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_execution_inspection_still_accepts_exact_resource_network_and_mount_policy`（L498–L512）：接收`execution_inspection`。 控制顺序：L503断言`proof["resource_limits"] == { "cpu_period": 100000, "cpu_quota": 100000, "memory": 2 …`；L511断言`proof["trusted_readonly_binary_mounts"] is True`；L512断言`len(calls) == 4`。 调用`profile.inspect_created_sandbox`、`len`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_actual_inspector_rejections_reach_receipt_without_upload_or_secret_data`（L594–L644）：接收`execution_inspection`、`settings`、`mutation`、`category`、`facts`。 控制顺序：L634断言`result["passed"] is False and result["cleanup"] == "deleted"`；L635断言`result["kind"] == "isolation_environment" and operations == ["deleted"]`；L636断言`"container_isolation" not in result`；L638断言`diagnostic["container_rejection"] == category`；L639断言`diagnostic.items() >= facts.items()`；L641断言`json.loads(receipt_text) == result`；L642断言`"secret" not in receipt_text.lower()`；L643断言`"must-not-be-in-receipt" not in receipt_text`。后续分支沿下方源码相同行号继续阅读。 调用`mutation`、`fixed_application`、`SimpleNamespace`、`operations.append`、`_verify`、`plan.selection.model_dump`、`profile.require_profile`、`profile.inspect_created_sandbox`、`diagnostic.items`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_actual_inspector_rejections_reach_receipt_without_upload_or_secret_data.forbidden`（L606–L607）：接收`*args`、`**kwargs`。 调用`pytest.fail`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_inspector_diagnostics_allow_only_finite_fields_values_and_bounded_numbers`（L647–L675）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L671断言`error.diagnostic() == expected`；L673断言`error.diagnostic() == expected`；L675断言`error.diagnostic() == {}`。 调用`ContainerInspectionRejected`、`error.diagnostic`、`error._facts.update`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_readonly_inspection_is_scoped_to_owned_uuid_and_redacts_everything_else`（L678–L711）：接收`inspection`。 控制顺序：L683断言`proof["privileged"] is False and proof["seccomp"] == "docker-default"`；L684断言`proof["snapshot_image_id"] == SNAPSHOT`；L685断言`calls == [ ("container", "inspect", OUTER), ( "exec", OUTER, "docker", "--host", "uni…`；L708断言`"SECRET" not in json.dumps(proof) and "TOKEN" not in json.dumps(proof)`；L711断言`len(calls) == 3`。 调用`profile.inspect_created_sandbox`、`json.dumps`、`pytest.raises`、`len`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_created_application_rejects_real_inspect_drift`（L738–L742）：接收`inspection`、`mutation`。 调用`mutation`、`pytest.raises`、`profile.inspect_created_sandbox`、`pytest.mark.parametrize`、`row.update`、`row["Config"].update`、`row["HostConfig"].update`、`row["Mounts"][0].update`、`row["Mounts"].append`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_wrong_runner_is_rejected_before_an_inner_exec`（L745–L750）：接收`inspection`。 控制顺序：L750断言`len(calls) == 1`。 调用`pytest.raises`、`profile.inspect_created_sandbox`、`len`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_recipe_keeps_real_embeds_glibc_smoke_license_and_locked_go_inputs`（L753–L780）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L755遍历`( "./apps/daemon/cmd/daemon", "./libs/computer-use", "./apps/runn…`；L770断言`text in recipe`；L771断言`"go mod edit" not in recipe and "yarn" not in recipe`；L773断言`snapshot.rstrip().endswith("USER 0:0")`；L774断言`"WORKDIR /opt/rnd/control" in snapshot`；L775断言`(profile.ROOT / "tools/daytona/Dockerfile") .read_text() .rstrip() .endswith("WORKDIR…`。 调用`(profile.ROOT / "tools/daytona/capability-runner.Dockerfile").rea…`、`(profile.ROOT / "tools/daytona/capability-snapshot.Dockerfile").r…`、`snapshot.rstrip().endswith`、`snapshot.rstrip`、`(profile.ROOT / "tools/daytona/Dockerfile") .read_text() .rstrip(…`、`(profile.ROOT / "tools/daytona/Dockerfile") .read_text() .rstrip`、`(profile.ROOT / "tools/daytona/Dockerfile") .read_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `locked_profile`（L784–L869）：接收`tmp_path`、`monkeypatch`。 控制顺序：L787遍历`base["services"].items()`。 调用`base_config`、`base["services"].items`、`tag.rsplit`、`records["api"].update`、`build.api_patch_identity`、`monkeypatch.setattr`、`profile.write_compose`、`local.private_json`、`profile.recipe_identity`等。 返回路径：L869的`tmp_path, record`。
- `locked_profile.inspect_api`（L797–L814）：接收`*args`、`**kwargs`。 控制顺序：L798断言`args == ("image", "inspect", records["api"]["image_id"])`。 调用`json.dumps`、`build.api_patch_labels`。 返回路径：L801的`json.dumps( [ { "Id": records["api"]["image_id"], "Config": { "Labels": { "org.opencontain…`。
- `test_profile_lock_roundtrip_preserves_ordinary_lock_and_rejects_compose_changes`（L872–L883）：接收`locked_profile`。 控制顺序：L878断言`actual == record`；L883断言`(directory / "compose.lock.yaml").read_bytes() == ordinary`。 调用`(directory / "compose.lock.yaml").read_bytes`、`profile.load_profile`、`profile.write_compose`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_prior_runner_recipe_is_rejected_before_current_shared_memory_admission`（L886–L900）：接收`locked_profile`。 调用`record["recipes"].update`、`profile.sha256`、`json.dumps(record["recipes"], sort_keys=True).encode`、`json.dumps`、`local.private_json`、`pytest.raises`、`profile.load_profile`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_edited_lock_cannot_select_general_or_unpinned_images`（L913–L919）：接收`locked_profile`、`mutation`。 调用`mutation`、`local.private_json`、`pytest.raises`、`profile.load_profile`、`pytest.mark.parametrize`、`record["bases"]["GO_IMAGE"].update`、`record["snapshot"].update`、`record["runner"].update`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_required_profile_verifies_image_id_and_registry_digest`（L922–L937）：接收`locked_profile`、`monkeypatch`。 控制顺序：L932断言`profile.require_profile(directory, record["snapshot"]["snapshot"]) == record`。 调用`snapshot_inspect`、`copy.deepcopy`、`monkeypatch.setattr`、`dependency_record`、`profile.require_profile`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_prepare_never_overwrites_existing_profile_or_credentials`（L940–L944）：接收`locked_profile`。 调用`pytest.raises`、`profile.prepare`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_missing_actual_engine_seccomp_is_not_default_filter_evidence`（L950–L955）：接收`inspection`、`options`。 控制顺序：L955断言`len(calls) == 2`。 调用`pytest.raises`、`profile.inspect_created_sandbox`、`len`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_daytona_capability_profile.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L955。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`36459`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_daytona_capability_profile.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "1f90ccd1086d6e0f339e0f045a35eca4d53cbc5ec547c942b86b3ed87efdd0f9"} -->
````python
# tests/test_daytona_capability_profile.py
"""Owned build/inspection contracts, not live isolation or privilege experiments."""

import copy
import difflib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts import daytona_build as build
from scripts import daytona_capability_profile as profile
from scripts import daytona_local as local
from scripts.daytona_bootstrap import snapshot_resources
from workbench.capability_isolation import ContainerInspectionRejected

RUNNER = "sha256:" + "a" * 64
SNAPSHOT = "sha256:" + "b" * 64
DIGEST = "sha256:" + "c" * 64
OUTER = "d" * 64
SANDBOX = "ea997c7d-cbb9-45eb-8352-3f8bc9e2a512"


def dependency_record():
    return {
        "schema": 1,
        "profile": "python-basic",
        "image_id": SNAPSHOT,
        "manifest_sha256": "1" * 64,
        "installed_tree_sha256": "2" * 64,
        "original_descriptors": {
            name: profile.sha256((profile.ROOT / "templates/product" / name).read_bytes())
            for name in ("pyproject.toml", "uv.lock")
        },
    }


def base_config():
    services = {
        name: {
            "image": tag,
            "environment": {"OTEL_ENABLED": "false"},
            "networks": ["daytona-network"],
        }
        for name, tag in local.IMAGES.items()
    }
    services["gateway"] = local.gateway_service()
    services["runner"]["privileged"] = True  # Existing local DinD control plane.
    services["runner"]["environment"]["INTER_SANDBOX_NETWORK_ENABLED"] = "false"
    return {"services": services, "networks": copy.deepcopy(local.NETWORKS)}


def test_profile_transformation_preserves_general_defaults_and_all_other_fields():
    original = base_config()
    original["services"]["runner"]["environment"]["RESOURCE_LIMITS_DISABLED"] = "true"
    untouched = copy.deepcopy(original)
    image = "registry:6000/rnd-python:0123456789abcdef"
    result = profile.render_profile(original, RUNNER, image)
    assert original == untouched
    assert result["name"] == profile.PROJECT
    assert result["services"]["runner"]["image"] == RUNNER
    assert result["services"]["runner"]["environment"]["USE_SNAPSHOT_ENTRYPOINT"] == "false"
    assert result["services"]["runner"]["privileged"] is True
    assert result["services"]["runner"]["environment"]["RESOURCE_LIMITS_DISABLED"] == "true"
    assert result["services"]["api"]["environment"]["DEFAULT_SNAPSHOT"] == image
    # The owned app-container patch does not alter DinD or general defaults.
    assert "USE_SNAPSHOT_ENTRYPOINT" not in original["services"]["runner"]["environment"]
    assert local.IMAGES["runner"].startswith("rnd-local/daytona-runner:")
    assert snapshot_resources({"image": image}) == (
        {"cpu": 1, "memory": 2, "disk": 5},
        True,
    )
    with pytest.raises(ValueError, match="own disposable"):
        profile.profile_directory(local.HOME)


def snapshot_inspect():
    identity, _ = profile.recipe_identity()
    return {
        "Id": SNAPSHOT,
        "Os": "linux",
        "Architecture": "amd64",
        "RepoDigests": ["127.0.0.1:6000/rnd-python@" + DIGEST],
        "Config": {
            "User": "0:0",
            "WorkingDir": profile.CONTROL_WORKDIR,
            "Entrypoint": None,
            "Cmd": None,
            "Labels": {
                "org.opencontainers.image.revision": profile.DAYTONA_SOURCE,
                "rnd.capability.profile": profile.PROFILE,
                "rnd.capability.recipe": identity,
            },
        },
    }


@pytest.mark.parametrize(
    "field,value",
    [
        ("User", "daytona"),
        ("User", ""),
        ("WorkingDir", "/home/daytona"),
        ("Entrypoint", ["unapproved"]),
        ("Cmd", ["unapproved"]),
    ],
)
def test_snapshot_requires_declared_control_identity_and_no_inherited_command(field, value):
    image = snapshot_inspect()
    identity, _ = profile.recipe_identity()
    profile.validate_image(image, identity, snapshot=True)
    image["Config"][field] = value
    with pytest.raises(ValueError, match="Snapshot must declare"):
        profile.validate_image(image, identity, snapshot=True)


def test_runner_requires_the_explicit_normal_daemon_entrypoint():
    image = snapshot_inspect()
    identity, _ = profile.recipe_identity()
    for env in ([], ["USE_SNAPSHOT_ENTRYPOINT=true"]):
        image["Config"]["Env"] = env
        with pytest.raises(ValueError, match="normal daemon"):
            profile.validate_image(image, identity, snapshot=False)
    image["Config"]["Env"] = ["USE_SNAPSHOT_ENTRYPOINT=false"]
    profile.validate_image(image, identity, snapshot=False)


def source_fixture(tmp_path, monkeypatch):
    root, context = tmp_path / "recipes", tmp_path / "context"
    context.mkdir()
    source = (
        "// Copyright Daytona; AGPL-3.0\npackage docker\nvar host = container.HostConfig{\n"
        + profile.OLD
        + "}\n"
        + profile.LIMIT_ANCHOR
        + "\n"
    )
    workspace = "go 1.25.5\n\nuse ./apps/runner\n"
    for name in profile.RECIPE_PATHS:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("recipe fixture\n")
    patch = "".join(
        difflib.unified_diff(
            source.splitlines(keepends=True),
            source.replace(profile.OLD, profile.NEW)
            .replace(profile.LIMIT_ANCHOR, profile.LIMIT_INSERT + profile.LIMIT_ANCHOR, 1)
            .splitlines(keepends=True),
            fromfile="a/" + profile.SOURCE_FILE,
            tofile="b/" + profile.SOURCE_FILE,
        )
    )
    (root / "tools/daytona/capability-runner.patch").write_text(patch)

    def export(directory, command, target):
        path = Path(target) / profile.SOURCE_FILE
        path.parent.mkdir(parents=True)
        # These stand in for Git-exported, SHA-bound bytes, not host-native
        # text files. Windows newline conversion must not alter the preimage.
        path.write_bytes(source.encode("utf-8"))
        (Path(target) / "go.work").write_bytes(workspace.encode("utf-8"))
        (Path(target) / "apps/runner/go.mod").write_bytes(b"module fixture\ngo 1.25.5\n")
        (Path(target) / "apps/runner/go.sum").write_bytes(b"fixture v1 h1:fixture\n")

    monkeypatch.setattr(profile, "ROOT", root)
    monkeypatch.setattr(profile, "export_source", export)
    monkeypatch.setattr(profile, "SOURCE_BLOB", profile.blob(source.encode()))
    monkeypatch.setattr(profile, "WORKSPACE_BLOB", profile.blob(workspace.encode()))
    return root, context, source, workspace


def test_source_preimage_and_patch_are_exact_and_module_inputs_are_preserved(tmp_path, monkeypatch):
    _, context, source, workspace = source_fixture(tmp_path, monkeypatch)
    record = profile.source_context(tmp_path, context)
    assert (context / profile.SOURCE_FILE).read_text() == source.replace(
        profile.OLD, profile.NEW
    ).replace(profile.LIMIT_ANCHOR, profile.LIMIT_INSERT + profile.LIMIT_ANCHOR, 1)
    assert (context / "go.work").read_text() == workspace
    assert (context / "apps/runner/go.mod").read_text() == "module fixture\ngo 1.25.5\n"
    assert (context / "go.work.sum").read_text() == "fixture v1 h1:fixture\n"
    assert record["source_sha"] == profile.DAYTONA_SOURCE
    assert (context / "capability-build/NOTICE").is_file()


def test_custom_source_patch_binds_only_its_reviewed_primary_bridge(tmp_path, monkeypatch):
    _, context, _, _ = source_fixture(tmp_path, monkeypatch)
    profile.source_context(tmp_path, context)
    source = (context / profile.SOURCE_FILE).read_text(encoding="utf-8")
    assignment = 'hostConfig.NetworkMode = container.NetworkMode("runner-bridge")'
    assert source.count(assignment) == 1
    custom = source.split('if strings.HasPrefix(sandboxDto.Name, "rnd-source-") {', 1)[1]
    assert custom.index(assignment) < custom.index("pidLimit := int64(256)")
    assert custom.index(assignment) < custom.index('"rnd-source-native-"')
    assert "Privileged: false" in source
    assert "NetworkMode" not in source.split("// Custom-source executions", 1)[0]


def test_custom_source_patch_pins_cpu_memory_and_no_extra_swap_independent_of_global_flag():
    custom, native = profile.LIMIT_INSERT.split(
        'if strings.HasPrefix(sandboxDto.Name, "rnd-source-native-") {', 1
    )
    assert 'if strings.HasPrefix(sandboxDto.Name, "rnd-source-") {' in custom
    assert "resourceLimitsDisabled" not in profile.LIMIT_INSERT
    assert "hostConfig.CPUPeriod = 100000" in custom
    assert "hostConfig.CPUQuota = 100000" in custom
    assert "hostConfig.Memory = 2 * 1024 * 1024 * 1024" in custom
    assert "hostConfig.CPUQuota = 200000" in native
    assert "hostConfig.Memory = 6 * 1024 * 1024 * 1024" in native
    assert native.endswith("\t\t}\n\t\thostConfig.MemorySwap = hostConfig.Memory\n\t}\n")


def test_shared_memory_patch_is_exact_and_only_changes_the_native_container_branch():
    custom, native = profile.LIMIT_INSERT.split(
        'if strings.HasPrefix(sandboxDto.Name, "rnd-source-native-") {', 1
    )
    native, after_native = native.split("\t\t}\n", 1)
    for statement in (
        'hostConfig.IpcMode = container.IpcMode("private")',
        "hostConfig.ShmSize = 67108864",
    ):
        assert native.count(statement) == 1
        assert statement not in custom + after_native + profile.NEW
    assert "/dev/shm" not in profile.LIMIT_INSERT
    assert "Binds" not in profile.LIMIT_INSERT and "Mounts" not in profile.LIMIT_INSERT
    patch = (profile.ROOT / "tools/daytona/capability-runner.patch").read_bytes()
    # Regenerated from this verified upstream Git blob, not a hand-edited hunk.
    assert profile.SOURCE_BLOB == "d5a97203afa87c3fa0065702723c41645bf284b6"
    assert (
        profile.sha256(patch) == "637d72fa9426bd186dc729c20a2f47e8b138140d6a339299e0ab59c3c18f8eed"
    )


@pytest.mark.parametrize("native", [False, True])
def test_complete_source_resource_mapping_preserves_strict_bounds(native):
    memory = (6 if native else 2) * 1024**3
    quota = 200000 if native else 100000
    tmpfs = 4294967296 if native else 1073741824
    host = {
        "CpuPeriod": 100000,
        "CpuQuota": quota,
        "Memory": memory,
        "MemorySwap": memory,
        "PidsLimit": 384 if native else 256,
        "Tmpfs": {"/tmp": f"rw,nosuid,nodev,size={tmpfs},mode=1777"},
    }
    proof = profile.require_execution_resources(host, native=native)
    assert proof["cpu_quota"] == quota
    assert proof["memory"] == proof["memory_swap"] == memory
    for field, value in (
        ("CpuPeriod", 0),
        ("CpuQuota", 0),
        ("CpuQuota", quota + 1),
        ("Memory", 0),
        ("Memory", memory + 1),
        ("MemorySwap", 0),
        ("MemorySwap", memory + 1),
        ("MemorySwap", -1),
    ):
        with pytest.raises(ContainerInspectionRejected):
            profile.require_execution_resources({**host, field: value}, native=native)


@pytest.mark.parametrize("changed", ["source", "workspace", "patch"])
def test_source_drift_fails_closed_before_any_build(tmp_path, monkeypatch, changed):
    root, context, _, _ = source_fixture(tmp_path, monkeypatch)
    if changed == "source":
        monkeypatch.setattr(profile, "SOURCE_BLOB", "0" * 40)
    elif changed == "workspace":
        monkeypatch.setattr(profile, "WORKSPACE_BLOB", "0" * 40)
    else:
        with (root / "tools/daytona/capability-runner.patch").open("a") as file:
            file.write("unreviewed change\n")
    with pytest.raises(ValueError, match="does not.*match"):
        profile.source_context(tmp_path, context)


def application_inspect():
    return {
        "Name": "/" + SANDBOX,
        "Image": SNAPSHOT,
        "State": {"Running": True},
        "Config": {
            "User": "0:0",
            "WorkingDir": profile.CONTROL_WORKDIR,
            "Entrypoint": ["/usr/local/bin/daytona"],
            "Cmd": None,
            "Env": ["SECRET=must-not-be-in-receipt"],
        },
        "HostConfig": {
            "Privileged": False,
            "NetworkMode": "runner-bridge",
            "SecurityOpt": None,
        },
        "Mounts": [
            {
                "Type": "bind",
                "RW": False,
                "Destination": "/usr/local/bin/daytona",
                "Source": "/usr/local/bin/.tmp/binaries/daemon-amd64",
            },
            {
                "Type": "bind",
                "RW": False,
                "Destination": "/usr/local/lib/daytona-computer-use",
                "Source": "/usr/local/bin/.tmp/binaries/daytona-computer-use",
            },
        ],
    }


@pytest.fixture
def inspection(tmp_path, monkeypatch):
    record = {
        "profile": profile.PROFILE,
        "runner": {"image_id": RUNNER},
        "snapshot": {
            "image_id": SNAPSHOT,
            "digest": "registry:6000/rnd-python@" + DIGEST,
            "dependency_manifest": dependency_record(),
        },
    }
    outer = {
        "Image": RUNNER,
        "State": {"Running": True},
        "Config": {
            "Labels": {
                "com.docker.compose.project": profile.PROJECT,
                "com.docker.compose.service": "runner",
            },
            "Env": ["USE_SNAPSHOT_ENTRYPOINT=false", "TOKEN=must-not-be-in-receipt"],
            "Entrypoint": ["/usr/local/bin/dind", "/usr/local/bin/rnd-runner-entry.sh"],
            "Cmd": None,
        },
    }
    inner, calls = application_inspect(), []
    monkeypatch.setattr(profile, "require_profile", lambda _: record)
    monkeypatch.setattr(profile, "compose", lambda *args: OUTER)

    def docker(*args, **kwargs):
        calls.append(args)
        if "info" in args:
            return json.dumps(inner.get("engine_security", ["name=seccomp,profile=builtin"]))
        if "network" in args:
            return json.dumps(inner["bridge_inspect"])
        return json.dumps([outer if args[0] == "container" else inner])

    monkeypatch.setattr(local, "docker", docker)
    return tmp_path, outer, inner, calls


@pytest.fixture
def execution_inspection(inspection):
    _, _, inner, _ = inspection
    inner["HostConfig"].update(
        Memory=2 * 1024**3,
        MemorySwap=2 * 1024**3,
        CpuPeriod=100000,
        CpuQuota=100000,
        PidsLimit=256,
        Tmpfs={"/tmp": "rw,nosuid,nodev,size=1073741824,mode=1777"},
    )
    inner["NetworkSettings"] = {"Networks": {"runner-bridge": {}}}
    inner["bridge_inspect"] = [
        {
            "EnableIPv6": False,
            "Driver": "bridge",
            "IPAM": {"Config": [{"Subnet": local.RUNNER_BRIDGE_SUBNET}]},
        }
    ]
    inner["Mounts"].append({"Type": "tmpfs", "Destination": "/tmp", "RW": True, "Source": ""})
    return inspection


@pytest.fixture
def native_inspection(execution_inspection, monkeypatch):
    from scripts import daytona_native_capability_profile as native

    directory, _, inner, _ = execution_inspection
    record = copy.deepcopy(profile.require_profile(directory))
    record["profile"] = native.PROFILE
    record["snapshot"]["digest"] = "registry:6000/rnd-native-fastapiadmin@" + DIGEST
    monkeypatch.setattr(native, "require_native_profile", lambda _: record)
    inner["HostConfig"].update(
        IpcMode="private",
        ShmSize=67108864,
        CpuQuota=200000,
        Memory=6 * 1024**3,
        MemorySwap=6 * 1024**3,
        PidsLimit=384,
        Tmpfs={"/tmp": "rw,nosuid,nodev,size=4294967296,mode=1777"},
    )
    return execution_inspection


def test_native_inspection_binds_private_shared_memory_without_expanding_mounts(native_inspection):
    directory, _, _, calls = native_inspection
    proof = profile.inspect_created_sandbox(
        directory, SANDBOX, require_resources=True, selection={"template": "fastapiadmin"}
    )
    assert proof["shared_memory"] == {"ipc_mode": "private", "size_bytes": 67108864}
    assert type(proof["shared_memory"]["size_bytes"]) is int
    assert proof["resource_limits"] == {
        "cpu_period": 100000,
        "cpu_quota": 200000,
        "memory": 6 * 1024**3,
        "memory_swap": 6 * 1024**3,
        "tmpfs_bytes": 4294967296,
        "pids": 384,
    }
    assert proof["trusted_readonly_binary_mounts"] is True
    assert len(calls) == 4


@pytest.mark.parametrize("require_resources", [False, True])
@pytest.mark.parametrize(
    "field,value",
    [
        ("IpcMode", None),
        ("IpcMode", ""),
        ("IpcMode", "host"),
        ("IpcMode", "shareable"),
        ("IpcMode", "container:secret-container"),
        ("IpcMode", True),
        ("ShmSize", None),
        ("ShmSize", 0),
        ("ShmSize", -1),
        ("ShmSize", 67108863),
        ("ShmSize", 67108865),
        ("ShmSize", 67108864.0),
        ("ShmSize", "67108864"),
        ("ShmSize", True),
        ("ShmSize", False),
    ],
)
def test_native_shared_memory_rejects_missing_changed_and_untyped_inspection(
    native_inspection, require_resources, field, value
):
    directory, _, inner, calls = native_inspection
    if value is None:
        inner["HostConfig"].pop(field)
    else:
        inner["HostConfig"][field] = value
    with pytest.raises(ContainerInspectionRejected, match="exact private IPC") as error:
        profile.inspect_created_sandbox(
            directory,
            SANDBOX,
            require_resources=require_resources,
            selection={"template": "fastapiadmin"},
        )
    assert error.value.diagnostic() == {
        "container_rejection": "shared_memory",
        "shared_memory_ipc_private": field != "IpcMode",
        "shared_memory_size_match": field != "ShmSize",
    }
    assert "secret" not in json.dumps(error.value.diagnostic())
    assert len(calls) == 3


@pytest.mark.parametrize("ipc_mode", [None, "", "private"])
def test_sqlite_inspection_keeps_prior_ipc_policy_without_native_shared_memory(
    execution_inspection, ipc_mode
):
    directory, _, inner, _ = execution_inspection
    if ipc_mode is not None:
        inner["HostConfig"]["IpcMode"] = ipc_mode
    proof = profile.inspect_created_sandbox(directory, SANDBOX, require_resources=True)
    assert "shared_memory" not in proof
    assert proof["resource_limits"]["memory"] == 2 * 1024**3


@pytest.mark.parametrize(
    "mutation",
    [
        lambda row: row["HostConfig"].update(Privileged=True),
        lambda row: row["HostConfig"].update(SecurityOpt=["seccomp=unconfined"]),
        lambda row: row["HostConfig"].update(CapAdd=["SYS_ADMIN"]),
        lambda row: row["HostConfig"].update(PidMode="host"),
        lambda row: row["HostConfig"].update(NetworkMode="default"),
        lambda row: row["HostConfig"].update(MemorySwap=-1),
        lambda row: row["HostConfig"].update(Tmpfs={"/dev/shm": "rw,size=67108864"}),
        lambda row: row["Mounts"].append(
            {"Type": "bind", "RW": True, "Destination": "/dev/shm", "Source": "/dev/shm"}
        ),
        lambda row: row["Mounts"].append(
            {"Type": "tmpfs", "RW": True, "Destination": "/dev/shm", "Source": ""}
        ),
    ],
)
def test_native_shared_memory_preserves_all_other_container_predicates(native_inspection, mutation):
    directory, _, inner, _ = native_inspection
    mutation(inner)
    with pytest.raises(ContainerInspectionRejected):
        profile.inspect_created_sandbox(
            directory, SANDBOX, require_resources=True, selection={"template": "fastapiadmin"}
        )


def test_execution_inspection_still_accepts_exact_resource_network_and_mount_policy(
    execution_inspection,
):
    directory, _, _, calls = execution_inspection
    proof = profile.inspect_created_sandbox(directory, SANDBOX, require_resources=True)
    assert proof["resource_limits"] == {
        "cpu_period": 100000,
        "cpu_quota": 100000,
        "memory": 2 * 1024**3,
        "memory_swap": 2 * 1024**3,
        "tmpfs_bytes": 1073741824,
        "pids": 256,
    }
    assert proof["trusted_readonly_binary_mounts"] is True
    assert len(calls) == 4


@pytest.mark.parametrize(
    "mutation,category,facts",
    [
        (
            lambda row: row["HostConfig"].update(CpuPeriod=0, CpuQuota=0, Memory=0, MemorySwap=0),
            "resource_limits",
            {"cpu_period": 0, "cpu_quota": 0, "memory": 0, "memory_swap": 0},
        ),
        (
            lambda row: row["HostConfig"].update(NetworkMode="bridge"),
            "sandbox_network",
            {
                "network_mode": "bridge",
                "network_count": 1,
                "runner_bridge_attached": True,
            },
        ),
        (
            lambda row: row["HostConfig"].update(NetworkMode="default"),
            "sandbox_network",
            {
                "network_mode": "default",
                "network_count": 1,
                "runner_bridge_attached": True,
            },
        ),
        (
            lambda row: row["NetworkSettings"]["Networks"].update({"secret-network": {}}),
            "sandbox_network",
            {
                "network_mode": "runner-bridge",
                "network_count": 2,
                "runner_bridge_attached": True,
            },
        ),
        (
            lambda row: row["HostConfig"].update(NetworkMode="secret-network"),
            "sandbox_network",
            {
                "network_mode": "other",
                "network_count": 1,
                "runner_bridge_attached": True,
            },
        ),
        (
            lambda row: row["bridge_inspect"][0].update(EnableIPv6=True),
            "runner_bridge",
            {"bridge_ipv6_disabled": False, "bridge_driver_matches": True},
        ),
        (
            lambda row: row["HostConfig"].update(MemorySwap=-1),
            "resource_limits",
            {"memory_swap": -1, "memory": 2 * 1024**3, "tmpfs_options_match": True},
        ),
        (
            lambda row: row["HostConfig"].update(Tmpfs={"/secret-path": "secret-option"}),
            "resource_limits",
            {"tmpfs_keys_match": False, "tmpfs_options_match": False},
        ),
        (
            lambda row: row["Mounts"][0].update(Source="/secret-path"),
            "binary_mounts",
            {
                "mount_sources_match": False,
                "mount_readonly_matches": True,
                "mount_count": 2,
            },
        ),
        (
            lambda row: row["Mounts"][-1].update(Destination="/secret-path", RW=False),
            "tmpfs_mounts",
            {
                "mount_destinations_match": False,
                "mount_writable_matches": False,
                "mount_count": 1,
            },
        ),
    ],
)
def test_actual_inspector_rejections_reach_receipt_without_upload_or_secret_data(
    execution_inspection, settings, mutation, category, facts
):
    from scripts.ci_capability_profile import fixed_application
    from workbench.capability_sandbox import _verify

    directory, _, inner, calls = execution_inspection
    mutation(inner)
    product = directory / "product"
    plan = fixed_application(product)
    operations = []

    def forbidden(*args, **kwargs):
        pytest.fail("Inspector rejection must stop before source upload or execution")

    sandbox = SimpleNamespace(
        id=SANDBOX,
        fs=SimpleNamespace(create_folder=forbidden, upload_file=forbidden),
        process=SimpleNamespace(exec=forbidden),
    )
    client = SimpleNamespace(
        create=lambda *a, **k: sandbox,
        delete=lambda *a, **k: operations.append("deleted"),
    )
    settings.daytona_snapshot = "fixture-owned-snapshot"
    receipt_path = directory / "receipt.json"
    result = _verify(
        product,
        plan,
        plan.scenarios,
        settings,
        plan.selection.model_dump(),
        receipt_path,
        client=client,
        aggregate=True,
        profile_record=profile.require_profile(directory),
        control_observer=lambda identifier: profile.inspect_created_sandbox(
            directory, identifier, require_resources=True
        ),
    )
    assert result["passed"] is False and result["cleanup"] == "deleted"
    assert result["kind"] == "isolation_environment" and operations == ["deleted"]
    assert "container_isolation" not in result
    diagnostic = result["isolation_diagnostic"]
    assert diagnostic["container_rejection"] == category
    assert diagnostic.items() >= facts.items()
    receipt_text = receipt_path.read_text(encoding="utf-8")
    assert json.loads(receipt_text) == result
    assert "secret" not in receipt_text.lower()
    assert "must-not-be-in-receipt" not in receipt_text
    assert len(calls) == (3 if category == "sandbox_network" else 4)


def test_inspector_diagnostics_allow_only_finite_fields_values_and_bounded_numbers():
    error = ContainerInspectionRejected(
        "secret exception text",
        category="resource_limits",
        facts={
            "memory": 2 * 1024**3,
            "memory_swap": -(2**100),
            "cpu_period": True,
            "cpu_quota": "secret quota",
            "pids_limit": 256,
            "tmpfs_options_match": "secret flag",
            "environment": {"TOKEN": "secret"},
            "mount_path": "/secret",
        },
    )
    expected = {
        "container_rejection": "resource_limits",
        "memory": 2 * 1024**3,
        "memory_swap": None,
        "cpu_period": None,
        "cpu_quota": None,
        "pids_limit": 256,
        "tmpfs_options_match": None,
    }
    assert error.diagnostic() == expected
    error._facts.update(environment="secret", cpu_quota="secret")
    assert error.diagnostic() == expected
    error._category = "secret category"
    assert error.diagnostic() == {}


def test_readonly_inspection_is_scoped_to_owned_uuid_and_redacts_everything_else(
    inspection,
):
    directory, _, _, calls = inspection
    proof = profile.inspect_created_sandbox(directory, SANDBOX)
    assert proof["privileged"] is False and proof["seccomp"] == "docker-default"
    assert proof["snapshot_image_id"] == SNAPSHOT
    assert calls == [
        ("container", "inspect", OUTER),
        (
            "exec",
            OUTER,
            "docker",
            "--host",
            "unix:///var/run/docker.sock",
            "info",
            "--format",
            "{{json .SecurityOptions}}",
        ),
        (
            "exec",
            OUTER,
            "docker",
            "--host",
            "unix:///var/run/docker.sock",
            "container",
            "inspect",
            SANDBOX,
        ),
    ]
    assert "SECRET" not in json.dumps(proof) and "TOKEN" not in json.dumps(proof)
    with pytest.raises(ValueError):
        profile.inspect_created_sandbox(directory, "--privileged")
    assert len(calls) == 3


@pytest.mark.parametrize(
    "mutation",
    [
        lambda row: row.update(Image="sha256:" + "f" * 64),
        lambda row: row["Config"].update(User="daytona"),
        lambda row: row["Config"].update(Entrypoint=["other"]),
        lambda row: row["Config"].update(Cmd=["other"]),
        lambda row: row["HostConfig"].update(Privileged=True),
        lambda row: row["HostConfig"].update(SecurityOpt=["seccomp=unconfined"]),
        lambda row: row["HostConfig"].update(CapAdd=["SYS_ADMIN"]),
        lambda row: row["HostConfig"].update(NetworkMode="host"),
        lambda row: row["HostConfig"].update(PidMode="host"),
        lambda row: row["Mounts"][0].update(RW=True),
        lambda row: row["Mounts"][0].update(Source="/var/run/docker.sock"),
        lambda row: row["Mounts"].append(
            {
                "Type": "bind",
                "RW": False,
                "Destination": "/docker.sock",
                "Source": "/var/run/docker.sock",
            }
        ),
    ],
)
def test_created_application_rejects_real_inspect_drift(inspection, mutation):
    directory, _, inner, _ = inspection
    mutation(inner)
    with pytest.raises(ValueError, match="container|mounts"):
        profile.inspect_created_sandbox(directory, SANDBOX)


def test_wrong_runner_is_rejected_before_an_inner_exec(inspection):
    directory, outer, _, calls = inspection
    outer["Image"] = "sha256:" + "f" * 64
    with pytest.raises(ValueError, match="Running Runner"):
        profile.inspect_created_sandbox(directory, SANDBOX)
    assert len(calls) == 1


def test_recipe_keeps_real_embeds_glibc_smoke_license_and_locked_go_inputs():
    recipe = (profile.ROOT / "tools/daytona/capability-runner.Dockerfile").read_text()
    for text in (
        "./apps/daemon/cmd/daemon",
        "./libs/computer-use",
        "./apps/runner/cmd/runner",
        "GOTOOLCHAIN=local",
        "GOTELEMETRY=off",
        "-mod=readonly",
        "sha256sum -c",
        "source.tar",
        "COPY LICENSE",
        "API_PORT=invalid",
        "Failed to get config",
        "USE_SNAPSHOT_ENTRYPOINT=false",
        "rnd-runner-entry.sh",
    ):
        assert text in recipe
    assert "go mod edit" not in recipe and "yarn" not in recipe
    snapshot = (profile.ROOT / "tools/daytona/capability-snapshot.Dockerfile").read_text()
    assert snapshot.rstrip().endswith("USER 0:0")
    assert "WORKDIR /opt/rnd/control" in snapshot
    assert (
        (profile.ROOT / "tools/daytona/Dockerfile")
        .read_text()
        .rstrip()
        .endswith("WORKDIR /home/daytona")
    )


@pytest.fixture
def locked_profile(tmp_path, monkeypatch):
    base = base_config()
    records = {}
    for name, service in base["services"].items():
        tag = service["image"]
        value = RUNNER if name in profile.BUILT else tag.rsplit(":", 1)[0] + "@" + DIGEST
        records[name] = {
            "tag": tag,
            "image_id" if name in profile.BUILT else "digest": value,
        }
        service["image"] = value
    records["api"].update(source_sha=build.DAYTONA_SOURCE, source_patch=build.api_patch_identity())

    def inspect_api(*args, **kwargs):
        assert args == ("image", "inspect", records["api"]["image_id"]), (
            "No Docker mutation allowed"
        )
        return json.dumps(
            [
                {
                    "Id": records["api"]["image_id"],
                    "Config": {
                        "Labels": {
                            "org.opencontainers.image.revision": build.DAYTONA_SOURCE,
                            "org.opencontainers.image.version": build.DAYTONA_VERSION,
                            **build.api_patch_labels(),
                        }
                    },
                }
            ]
        )

    monkeypatch.setattr(local, "docker", inspect_api)
    profile.write_compose(tmp_path / "compose.lock.yaml", base)
    local.private_json(tmp_path / "images.lock.json", records)
    local.private_json(
        tmp_path / "installation.json",
        {
            "source_sha": profile.DAYTONA_SOURCE,
            "release": "v" + profile.DAYTONA_VERSION,
            "deployment": "local-development-only",
            "cloud_account": False,
        },
    )
    identity, recipes = profile.recipe_identity()
    bases = {
        name: {
            "tag": tag,
            "digest": tag.rsplit(":", 1)[0] + "@" + DIGEST,
            "image_id": SNAPSHOT,
        }
        for name, tag in profile.BASES.items()
    }
    stamp = profile.sha256((identity + json.dumps(bases, sort_keys=True)).encode())[:16]
    image = {
        "dependency_manifest": dependency_record(),
        "source_hash": stamp,
        "image": "registry:6000/rnd-python:" + stamp,
        "snapshot": "rnd-python-" + stamp,
        "local_tag": "127.0.0.1:6000/rnd-python:" + stamp,
        "image_id": SNAPSHOT,
        "digest": "registry:6000/rnd-python@" + DIGEST,
        "user": "0:0",
        "working_dir": profile.CONTROL_WORKDIR,
        "recipe_sha256": recipes["tools/daytona/capability-snapshot.Dockerfile"],
    }
    record = {
        "profile": profile.PROFILE,
        "recipe_identity": identity,
        "recipes": recipes,
        "source": {"source_sha": profile.DAYTONA_SOURCE},
        "bases": bases,
        "base_compose_sha256": profile.sha256((tmp_path / "compose.lock.yaml").read_bytes()),
        "runner": {
            "tag": "rnd-local/daytona-capability-runner:" + stamp,
            "image_id": RUNNER,
            "recipe_sha256": recipes["tools/daytona/capability-runner.Dockerfile"],
        },
        "snapshot": image,
    }
    profile.write_compose(
        tmp_path / profile.COMPOSE, profile.render_profile(base, RUNNER, image["image"])
    )
    local.private_json(tmp_path / profile.LOCK, record)
    local.private_json(tmp_path / "snapshot-image.json", image)
    return tmp_path, record


def test_profile_lock_roundtrip_preserves_ordinary_lock_and_rejects_compose_changes(
    locked_profile,
):
    directory, record = locked_profile
    ordinary = (directory / "compose.lock.yaml").read_bytes()
    config, actual = profile.load_profile(directory)
    assert actual == record
    config["services"]["runner"]["environment"]["USE_SNAPSHOT_ENTRYPOINT"] = "true"
    profile.write_compose(directory / profile.COMPOSE, config)
    with pytest.raises(ValueError, match="exact allowed transformation"):
        profile.load_profile(directory)
    assert (directory / "compose.lock.yaml").read_bytes() == ordinary


def test_prior_runner_recipe_is_rejected_before_current_shared_memory_admission(locked_profile):
    directory, record = locked_profile
    # This internally consistent recipe predates the explicit native IPC/size binding.
    record["recipes"].update(
        {
            "scripts/daytona_capability_profile.py": "97d9296f6793e8f5c884c891ac87e15c0e481c1feb9fcbc425a63a8c086d7b9c",
            "tools/daytona/capability-runner.patch": "5f29b0e86b5cdff4a04d318fdcfcb1f237e4d750771f1bebcb7a0fa36e5a800c",
        }
    )
    record["recipe_identity"] = profile.sha256(
        json.dumps(record["recipes"], sort_keys=True).encode()
    )
    local.private_json(directory / profile.LOCK, record)
    with pytest.raises(ValueError, match="recipe or original installation changed"):
        profile.load_profile(directory)


@pytest.mark.parametrize(
    "mutation",
    [
        lambda record: record["bases"]["GO_IMAGE"].update(digest="golang:latest"),
        lambda record: record["snapshot"].update(image="registry:6000/rnd-python:0000000000000000"),
        lambda record: record["snapshot"].update(user="daytona"),
        lambda record: record["snapshot"].update(digest="elsewhere.example/image@" + DIGEST),
        lambda record: record["runner"].update(tag=local.IMAGES["runner"]),
    ],
)
def test_edited_lock_cannot_select_general_or_unpinned_images(locked_profile, mutation):
    directory, record = locked_profile
    mutation(record)
    local.private_json(directory / profile.LOCK, record)
    local.private_json(directory / "snapshot-image.json", record["snapshot"])
    with pytest.raises(ValueError, match="lock|identity"):
        profile.load_profile(directory)


def test_required_profile_verifies_image_id_and_registry_digest(locked_profile, monkeypatch):
    directory, record = locked_profile
    image = snapshot_inspect()
    runner = copy.deepcopy(image)
    runner["Id"] = RUNNER
    runner["Config"]["Env"] = ["USE_SNAPSHOT_ENTRYPOINT=false"]
    monkeypatch.setattr(
        profile, "inspect_image", lambda value: runner if value == RUNNER else image
    )
    monkeypatch.setattr(profile, "inspect_dependency_manifest", lambda *args: dependency_record())
    assert profile.require_profile(directory, record["snapshot"]["snapshot"]) == record
    with pytest.raises(ValueError, match="explicitly select"):
        profile.require_profile(directory, "ordinary-snapshot")
    image["RepoDigests"] = []
    with pytest.raises(ValueError, match="ID and digest"):
        profile.require_profile(directory)


def test_prepare_never_overwrites_existing_profile_or_credentials(locked_profile):
    directory, _ = locked_profile
    # locked_profile permits only the exact read-only API image inspection.
    with pytest.raises(ValueError, match="fresh local state"):
        profile.prepare(directory)


@pytest.mark.parametrize(
    "options", [None, [], ["name=seccomp,profile=unconfined"], ["name=apparmor"]]
)
def test_missing_actual_engine_seccomp_is_not_default_filter_evidence(inspection, options):
    directory, _, inner, calls = inspection
    inner["engine_security"] = options
    with pytest.raises(ValueError, match="built-in seccomp"):
        profile.inspect_created_sandbox(directory, SANDBOX)
    assert len(calls) == 2
````
