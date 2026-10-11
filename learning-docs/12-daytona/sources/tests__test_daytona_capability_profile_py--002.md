# tests/test_daytona_capability_profile.py · 2/2

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)

[上一段](tests__test_daytona_capability_profile_py--001.md)

**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts`、`scripts.daytona_bootstrap`、`workbench.capability_isolation`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `test_prior_runner_recipe_is_rejected_before_current_shared_memory_admission`（L886–L900）：接收`locked_profile`。 调用`record["recipes"].update`、`profile.sha256`、`json.dumps(record["recipes"], sort_keys=True).encode`、`json.dumps`、`local.private_json`、`pytest.raises`、`profile.load_profile`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_edited_lock_cannot_select_general_or_unpinned_images`（L913–L919）：接收`locked_profile`、`mutation`。 调用`mutation`、`local.private_json`、`pytest.raises`、`profile.load_profile`、`pytest.mark.parametrize`、`record["bases"]["GO_IMAGE"].update`、`record["snapshot"].update`、`record["runner"].update`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_required_profile_verifies_image_id_and_registry_digest`（L922–L937）：接收`locked_profile`、`monkeypatch`。 控制顺序：L932断言`profile.require_profile(directory, record["snapshot"]["snapshot"]) == record`。 调用`snapshot_inspect`、`copy.deepcopy`、`monkeypatch.setattr`、`dependency_record`、`profile.require_profile`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_prepare_never_overwrites_existing_profile_or_credentials`（L940–L944）：接收`locked_profile`。 调用`pytest.raises`、`profile.prepare`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_missing_actual_engine_seccomp_is_not_default_filter_evidence`（L950–L955）：接收`inspection`、`options`。 控制顺序：L955断言`len(calls) == 2`。 调用`pytest.raises`、`profile.inspect_created_sandbox`、`len`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_coding_sandbox_uses_strict_runner_profile_before_upload`（L962–L1045）：接收`execution_inspection`、`settings`、`monkeypatch`、`rejection`、`original`。 源码说明：Real inspector over simulated Docker facts, never live isolation evidence.。 控制顺序：L1019按`rejection`分支；L1024断言`not uploaded and operations == ["create", "delete", "close"]`；L1025按`rejection != "egress_enabled"`分支；L1027断言`diagnostic["container_rejection"] == ( "resource_limits" if rejection == "no_limits" …`；L1030按`rejection == "legacy_name"`分支；L1031断言`diagnostic == { "container_rejection": "sandbox_network", "network_mode": "bridge", "…`；L1039断言`environment.snapshot(task.allowed_paths) == { "app.py": original.decode("utf-8"), "sl…`；L1043断言`len(uploaded) == 2`。后续分支沿下方源码相同行号继续阅读。 调用`acceptance_design`、`profile.require_profile`、`monkeypatch.setattr`、`SimpleNamespace`、`operations.append`、`product.mkdir`、`(product / "app.py").write_bytes`、`coding.coding_environment`、`plan.selection.model_dump`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_coding_sandbox_uses_strict_runner_profile_before_upload.upload`（L980–L983）：接收`content`、`path`、`**kwargs`。 控制顺序：L981断言`len(calls) == 4`。 调用`len`、`operations.append`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_coding_sandbox_uses_strict_runner_profile_before_upload.create`（L997–L1009）：接收`parameters`、`**kwargs`。 控制顺序：L998断言`parameters.network_block_all is True and parameters.public is False`；L1001断言`'if strings.HasPrefix(sandboxDto.Name, "rnd-source-") {' in profile.LIMIT_INSERT`；L1002按`not name.startswith("rnd-source-")`分支；L1004按`rejection == "extra_network"`分支；L1006按`rejection == "no_limits"`分支。 调用`name.startswith`、`inner["HostConfig"].update`、`operations.append`。 返回路径：L1009的`sandbox`。

</details>

**创建路径：** `tests/test_daytona_capability_profile.py`；**本文件共有 2 段**。本段覆盖源文件 L886–L1045。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`7343`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_daytona_capability_profile.py", "part": 2, "parts": 2, "encoding": "utf-8", "sha256": "cdef5b9cd7ef11ac933d62b0426c1205f610257b1929292c505278d09332087c"} -->
````python
# tests/test_daytona_capability_profile.py
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


@pytest.mark.parametrize(
    "rejection", [None, "legacy_name", "extra_network", "no_limits", "egress_enabled"]
)
@pytest.mark.parametrize("original", [b"# approved before-image\n", b"# approved before-image\r\n"])
def test_coding_sandbox_uses_strict_runner_profile_before_upload(
    execution_inspection, settings, monkeypatch, rejection, original
):
    """Real inspector over simulated Docker facts, never live isolation evidence."""
    from scripts.ci_live_modules import acceptance_design
    from workbench.errors import UnsupportedScope
    from workbench.infrastructure.sandbox import coding

    directory, _, inner, calls = execution_inspection
    plan = acceptance_design().implementation
    operations, uploaded = [], {}
    record = profile.require_profile(directory)
    record["recipe_identity"] = "e" * 64
    record["snapshot"]["snapshot"] = "offline-owned-snapshot"
    monkeypatch.setattr(
        coding, "capability_execution_prerequisites", lambda *a: (directory, record)
    )

    def upload(content, path, **kwargs):
        assert len(calls) == 4  # Real inspector and bridge validation precede any file upload.
        uploaded[path] = content
        operations.append("upload")

    sandbox = SimpleNamespace(
        id=SANDBOX,
        network_block_all=rejection != "egress_enabled",
        public=False,
        refresh_data=lambda: None,
        fs=SimpleNamespace(
            create_folder=lambda *a: None,
            upload_file=upload,
            download_file=lambda path, **k: uploaded[path],
        ),
    )

    def create(parameters, **kwargs):
        assert parameters.network_block_all is True and parameters.public is False
        # Emulate the pinned Runner's existing name-selected branch; do not alter it.
        name = "rnd-agent-old" if rejection == "legacy_name" else parameters.name
        assert 'if strings.HasPrefix(sandboxDto.Name, "rnd-source-") {' in profile.LIMIT_INSERT
        if not name.startswith("rnd-source-"):
            inner["HostConfig"].update(NetworkMode="bridge", CpuQuota=0, Memory=0)
        if rejection == "extra_network":
            inner["NetworkSettings"]["Networks"]["unexpected"] = {}
        if rejection == "no_limits":
            inner["HostConfig"].update(CpuQuota=0, Memory=0)
        operations.append("create")
        return sandbox

    client = SimpleNamespace(create=create, delete=lambda *a, **k: operations.append("delete"))
    monkeypatch.setattr(coding, "client_for", lambda *a: client)
    monkeypatch.setattr(coding, "close_client", lambda *a: operations.append("close"))
    product = directory / "coding-product"
    product.mkdir()
    (product / "app.py").write_bytes(original)
    task = plan.tasks[0]
    context = coding.coding_environment(settings, task, plan.selection.model_dump(), product)
    if rejection:
        error = UnsupportedScope if rejection == "egress_enabled" else ContainerInspectionRejected
        with pytest.raises(error) as captured:
            with context:
                pytest.fail("rejected isolation must not expose the file channel")
        assert not uploaded and operations == ["create", "delete", "close"]
        if rejection != "egress_enabled":
            diagnostic = captured.value.diagnostic()
            assert diagnostic["container_rejection"] == (
                "resource_limits" if rejection == "no_limits" else "sandbox_network"
            )
            if rejection == "legacy_name":
                assert diagnostic == {
                    "container_rejection": "sandbox_network",
                    "network_mode": "bridge",
                    "network_count": 1,
                    "runner_bridge_attached": True,
                }
    else:
        with context as environment:
            assert environment.snapshot(task.allowed_paths) == {
                "app.py": original.decode("utf-8"),
                "sla.py": "",
            }
        assert len(uploaded) == 2
        assert uploaded[coding.REMOTE + "/app.py"] == original
        assert operations[-2:] == ["delete", "close"]
````
