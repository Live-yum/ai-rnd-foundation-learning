# tests/test_daytona_dependency_build.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `scripts`、`scripts.daytona_native_capability_profile`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `uv_cli`（L27–L58）：接收`tmp_path`。 源码说明：Exercise the installed uv, with no user config, credentials or network.。 控制顺序：L30断言`executable`。 调用`shutil.which`、`env.update`、`str`。 返回路径：L58的`invoke`。
- `uv_cli.invoke`（L46–L56）：接收`command`、`cwd`、`extra`。 控制顺序：L55断言`result.returncode == 0`。 调用`subprocess.run`。 返回路径：L56的`result`。
- `metadata_wheel`（L61–L73）：接收`directory`、`name`。 源码说明：A data-only wheel: no source, backend, importable code or install hooks.。 调用`name.replace`、`zipfile.ZipFile`、`archive.writestr`。 返回路径：L73的`path`。
- `test_reviewed_bundled_native_graph_includes_required_sdists_and_exact_default_groups`（L76–L97）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L85断言`"sqlglot[rs]==27.8.0" in tomllib.loads(project.decode())["project"]["dependencies"]`；L86断言`tomllib.loads(project.decode())["tool"]["uv"]["default-groups"] == ["dev"]`；L89遍历`spec["sdists"]`；L90断言`packages[record["name"]]["version"] == record["version"]`；L91断言`packages[record["name"]]["sdist"]["hash"] == "sha256:" + record["sha256"]`；L92断言`packages[record["name"]]["sdist"]["url"] == record["url"]`；L93断言`{row["name"] for row in spec["sdists"]} == { "crcmod", "esdk-obs-python", "sqlglotrs"…`。 调用`zipfile.ZipFile`、`build.normalize`、`archive.read`、`build.validate_python`、`build.validate_node`、`tomllib.loads`、`project.decode`、`json.loads`、`(ROOT / "scripts/daytona_dependency_build.lock.json").read_bytes`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_candidate_build_backends_and_local_configuration_rejected`（L108–L113）：接收`extra`。 调用`pytest.raises`、`build.validate_python`、`('[project]\nname="fixture"\nversion="1"\n' + extra).encode`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_local_and_workspace_lock_packages_rejected`（L120–L125）：接收`source`。 调用`pytest.raises`、`build.validate_python`、`('[[package]]\nname="evil"\nsource=' + source + "\n").encode`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_registry_authentication_and_unreviewed_hosts_rejected`（L137–L139）：接收`url`。 调用`pytest.raises`、`build.public_url`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_node_hooks_local_sources_and_unhashed_artifacts_rejected`（L161–L163）：接收`package`、`lock`。 调用`pytest.raises`、`build.validate_node`、`json.dumps(package).encode`、`json.dumps`、`lock.encode`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_source_archive_does_not_extract_links_traversal_or_cargo_hooks`（L176–L189）：接收`tmp_path`、`kind`、`name`。 控制顺序：L189断言`not (tmp_path / "output").exists()`。 调用`tarfile.open`、`tarfile.TarInfo`、`archive.addfile`、`io.BytesIO`、`pytest.raises`、`build.extract_source`、`(tmp_path / "output").exists`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_built_wheel_replacement_preserves_other_hashes_and_markers`（L192–L211）：接收`tmp_path`。 控制顺序：L208断言`"crcmod @ " + wheel.as_uri() + ' ; python_version >= "3.14"' in replaced`；L209断言`"c" * 64 in replaced and "a" * 64 not in replaced and "b" * 64 in replaced`。 调用`(tmp_path / "crcmod-1.7-cp314-cp314-linux_x86_64.whl").absolute`、`str`、`build.replace_source_requirements`、`wheel.as_uri`、`pytest.raises`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_install_uses_locked_export_runtime_groups_no_project_hooks_or_sdists`（L215–L242）：接收`tmp_path`、`monkeypatch`、`uv_cli`、`mode`。 控制顺序：L237断言`"--locked" in calls[0] and "--no-emit-project" in calls[0]`；L238断言`("--no-dev" in calls[0]) is (mode == "basic")`；L239断言`("--all-extras" in calls[0]) is (mode == "harness")`；L240断言`str(project / ".venv") in calls[1]`；L241断言`"--require-hashes" in calls[2] and "--no-build" in calls[2]`；L242断言`calls[2][-1] == str(tmp_path / "runtime-requirements.lock.txt")`。 调用`project.mkdir`、`(project / "pyproject.toml").write_text`、`(project / "uv.lock").write_text`、`monkeypatch.setattr`、`(tmp_path / "source-builds.json").write_text`、`build.install`、`str`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_install_uses_locked_export_runtime_groups_no_project_hooks_or_sdists.run`（L226–L233）：接收`command`、`cwd`、`**kwargs`。 控制顺序：L230按`command[1] == "export"`分支。 调用`calls.append`、`uv_cli`、`(tmp_path / (project.name + "-requirements.lock.txt")).write_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_install_real_uv_offline_hashed_wheel_dry_run`（L254–L328）：接收`tmp_path`、`monkeypatch`、`uv_cli`、`mode`、`expected`。 控制顺序：L284遍历`wheels.items()`；L322遍历`wheels.items()`；L323断言`("fixture-" + group in requirements) is (group in expected)`；L324断言`(build.sha(wheel) in requirements) is (group in expected)`；L325断言`("fixture-runtime @ " in requirements) is (mode == "native")`；L326断言`f"Would install {len(expected)} package" in results[-1].stderr`；L327断言`original == {name: build.sha(project / name) for name in original}`；L328断言`not list((project / ".venv").rglob("fixture*.dist-info"))`。 调用`project.mkdir`、`wheelhouse.mkdir`、`metadata_wheel`、`(project / "pyproject.toml").write_text`、`wheels.items`、`build.sha`、`wheel.stat`、`(project / "uv.lock").write_text`、`(tmp_path / "source-builds.json").write_text`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_install_real_uv_offline_hashed_wheel_dry_run.run`（L310–L317）：接收`command`、`cwd`、`**kwargs`。 调用`str`、`results.append`、`uv_cli`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_fetch_real_uv_parser_keeps_install_requirements_flag`（L331–L365）：接收`tmp_path`、`monkeypatch`、`uv_cli`。 控制顺序：L362断言`command[1:3] == ["pip", "install"]`；L363断言`command[-2:] == ["-r", str(tmp_path / "build-tools.txt")]`；L364断言`{"--no-deps", "--no-build", "--require-hashes", "--no-index"} <= set(command)`；L365断言`kwargs == {"offline": True}`。 调用`project.mkdir`、`(project / "uv.lock").write_text`、`metadata_wheel`、`lock.write_text`、`json.dumps`、`build.sha`、`monkeypatch.setattr`、`build.fetch`、`str`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_fetch_real_uv_parser_keeps_install_requirements_flag.run`（L355–L357）：接收`command`、`cwd`、`**kwargs`。 调用`calls.append`、`uv_cli`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_source_build_real_uv_parser_without_executing_backend`（L369–L391）：接收`tmp_path`、`monkeypatch`、`uv_cli`、`package`。 调用`(tmp_path / "sources.json").write_text`、`json.dumps`、`str`、`monkeypatch.setattr`、`pytest.raises`、`build.build_sources`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_source_build_real_uv_parser_without_executing_backend.ParserChecked`（L377–L378）：继承`Exception`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_source_build_real_uv_parser_without_executing_backend.run`（L380–L387）：接收`command`、`cwd`、`**kwargs`。 控制顺序：L382断言`command[1:4] == ["build", "--wheel", "--no-build-isolation"]`；L383断言`"--offline" in command and kwargs == {"offline": True}`；L384按`package == "sqlglotrs"`分支；L385断言`command[-3:-1] == ["--config-setting", "build-args=--locked --offline"]`；L386断言`Path(command[-1]).name == "never-execute"`；L387抛异常，停止当前正常路径。 调用`uv_cli`、`Path`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_every_dependency_subprocess_uses_the_bounded_nonroot_runner`（L394–L406）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L406断言`calls == [("run", "run")]`。 调用`ast.parse`、`inspect.getsource`、`isinstance`、`ast.walk`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `metadata_image`（L410–L453）：接收`tmp_path`、`monkeypatch`、`request`。 源码说明：Map only fixed image paths; descriptor reads and hashes remain real.。 控制顺序：L428遍历`{ "runtime/python-basic": ("pyproject.toml", "uv.lock"), "runtime…`；L438遍历`names`。 调用`getattr`、`builder.mkdir`、`interpreter.parent.mkdir`、`interpreter.write_bytes`、`interpreter.chmod`、`{ "runtime/python-basic": ("pyproject.toml", "uv.lock"), "runtime…`、`path.parent.mkdir`、`path.write_bytes`、`path.chmod`等。 返回路径：L453的`image, descriptors`。
- `metadata_image.image_path`（L415–L419）：接收`value`。 控制顺序：L417按`path.is_relative_to("/opt/rnd")`分支。 调用`Path`、`path.is_relative_to`、`path.relative_to`。 返回路径：L418的`image / path.relative_to("/opt/rnd")`；L419的`path`。
- `assert_metadata_config_paths`（L456–L464）：接收`env`、`path_type`。 控制顺序：L458遍历`( ("npm_config_userconfig", "user.npmrc"), ("npm_config_globalcon…`；L463断言`config.parent == home`；L464断言`config.name == filename`。 调用`path_type`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_metadata_config_paths_require_exact_home_and_filename_on_both_platforms`（L475–L501）：接收`path_type`、`home`、`key`。 控制顺序：L494按`path_type is PureWindowsPath`分支；L499遍历`rejected_paths`。 调用`path_type`、`str`、`assert_metadata_config_paths`、`home.with_name`、`home.relative_to`、`pytest.raises`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_collect_preserves_interpreter_command_path_flavor`（L511–L528）：接收`tmp_path`、`monkeypatch`、`interpreter`。 调用`inputs.write_text`、`monkeypatch.setattr`、`pytest.raises`、`build.collect`、`pytest.mark.parametrize`、`PurePosixPath`、`PureWindowsPath`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_collect_preserves_interpreter_command_path_flavor.ProbeChecked`（L516–L517）：继承`Exception`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `test_collect_preserves_interpreter_command_path_flavor.probe`（L519–L524）：接收`command`、`cwd`、`**kwargs`。 控制顺序：L520断言`command[0] == str(interpreter)`；L521断言`command[1:5] == ["-I", "-S", "-B", "-c"]`；L522断言`cwd == build.BUILD`；L523断言`kwargs == {"offline": True, "metadata": True}`；L524抛异常，停止当前正常路径。 调用`str`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_collect_all_probes_are_offline_bounded_and_do_not_inherit_configuration`（L533–L638）：接收`tmp_path`、`monkeypatch`、`metadata_image`、`capsys`、`native`。 控制顺序：L538遍历`( "UV_CACHE_DIR", "UV_CONFIG_FILE", "HOME", "XDG_CONFIG_HOME", "P…`；L559按`native`分支；L611断言`collected["toolchain"]["python"] == str(build.PYTHON_BUILD.resolve(strict=True))`；L612断言`collected["original_descriptors"] == original["original_descriptors"]`；L613断言`collected["normalized_descriptors"] == original["normalized_descriptors"]`；L614按`native`分支；L615断言`collected["descriptor_roles"] == build.native_descriptor_roles()`；L616断言`"source_descriptor_bytes" not in collected`。后续分支沿下方源码相同行号继续阅读。 调用`monkeypatch.setenv`、`next`、`iter`、`descriptors.values`、`build.native_descriptor_roles`、`next(iter(descriptors)).read_bytes`、`roles.values`、`hashes.update`、`dict.fromkeys`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_collect_all_probes_are_offline_bounded_and_do_not_inherit_configuration.probe`（L575–L605）：接收`command`、`**kwargs`。 控制顺序：L577断言`kwargs["cwd"].parent == image / "build"`；L578断言`kwargs["cwd"].name.startswith("metadata-")`；L579断言`not list(kwargs["cwd"].iterdir())`；L580断言`kwargs["timeout"] == 60`；L581断言`kwargs["check"] is True and kwargs["capture_output"] is True`；L582断言`kwargs["text"] is True and kwargs["preexec_fn"] is build.limits`；L584断言`secret not in json.dumps(env)`；L585断言`env["UV_CACHE_DIR"] == str(image / "build/uv-cache")`。后续分支沿下方源码相同行号继续阅读。 调用`calls.append`、`kwargs["cwd"].name.startswith`、`list`、`kwargs["cwd"].iterdir`、`json.dumps`、`str`、`assert_metadata_config_paths`、`subprocess.CompletedProcess`。 返回路径：L605的`subprocess.CompletedProcess(command, 0, stdout=stdout, stderr=secret)`。
- `test_native_source_descriptor_line_endings_require_exact_byte_hash_identity`（L645–L683）：接收`tmp_path`、`monkeypatch`、`metadata_image`、`field`。 控制顺序：L655断言`changed_hash != expected_hash`；L656断言`set(descriptors.values()) == {expected_hash}`；L668断言`build.validate_native_descriptor_inputs(original) == roles`；L673遍历`original["source_descriptor_bytes"]`；L683断言`not output.exists()`。 调用`next(iter(descriptors)).read_bytes`、`next`、`iter`、`payload.replace`、`hashlib.sha256(payload).hexdigest`、`hashlib.sha256`、`hashlib.sha256(changed).hexdigest`、`set`、`descriptors.values`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_metadata_and_dependency_commands_cannot_run_as_root`（L687–L690）：接收`monkeypatch`、`tmp_path`、`metadata`。 调用`monkeypatch.setattr`、`pytest.raises`、`build.run`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_collect_probe_failures_leave_no_manifest_or_raw_output`（L694–L714）：接收`tmp_path`、`monkeypatch`、`metadata_image`、`capsys`、`failure`。 控制顺序：L711断言`private not in str(error.value)`；L712断言`not output.exists()`；L713断言`not list((image / "build").glob("metadata-*"))`；L714断言`capsys.readouterr() == ("", "")`。 调用`inputs.write_text`、`monkeypatch.setattr`、`pytest.raises`、`build.collect`、`str`、`output.exists`、`list`、`(image / "build").glob`、`capsys.readouterr`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_collect_probe_failures_leave_no_manifest_or_raw_output.fail`（L703–L706）：接收`command`、`**kwargs`。 控制顺序：L704按`failure == "timeout"`分支；L705抛异常，停止当前正常路径；L706抛异常，停止当前正常路径。 调用`subprocess.TimeoutExpired`、`subprocess.CalledProcessError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_build_commands_keep_existing_limits_and_validated_project_configuration`（L717–L733）：接收`tmp_path`、`monkeypatch`。 调用`monkeypatch.setattr`、`build.run`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_build_commands_keep_existing_limits_and_validated_project_configuration.execute`（L722–L730）：接收`command`、`**kwargs`。 控制顺序：L723断言`kwargs["timeout"] == 1800`；L724断言`kwargs["cwd"] == tmp_path`；L725断言`kwargs["preexec_fn"] is build.limits`；L726断言`kwargs["capture_output"] is False`；L727断言`"UV_NO_CONFIG" not in kwargs["env"]`；L728断言`kwargs["env"]["UV_OFFLINE"] == "1"`；L729断言`kwargs["env"]["CARGO_NET_OFFLINE"] == "true"`。 调用`subprocess.CompletedProcess`。 返回路径：L730的`subprocess.CompletedProcess(command, 0)`。
- `test_metadata_real_uv_and_python_ignore_unwritable_cache_config_and_secrets`（L740–L836）：接收`tmp_path`、`monkeypatch`、`capsys`。 控制顺序：L744断言`uv`；L756遍历`( "HOME", "UV_CACHE_DIR", "XDG_CONFIG_HOME", "XDG_CACHE_HOME", "P…`；L789断言`control.returncode != 0 and "Permission denied" in control.stderr`；L794断言`watcher >= 0`；L795遍历`(inherited, config)`；L796断言`libc.inotify_add_watch(watcher, os.fsencode(path), 0x00000FFF) >= 0`；L798断言`version.stdout.startswith("uv ")`；L819断言`result.stdout.strip() == "isolated"`。后续分支沿下方源码相同行号继续阅读。 调用`shutil.which`、`inherited.mkdir`、`config.write_text`、`config.chmod`、`inherited.chmod`、`config.read_bytes`、`config.stat`、`inherited.stat`、`builder.mkdir`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_recipes_separate_nonroot_offline_build_and_never_relocate_environments`（L839–L849）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L842断言`"AS dependency-builder" in base and "AS dependency-builder" in native`；L843断言`"RUN --network=none /opt/rnd/bin/python-build" in native`；L844断言`"USER daytona" in native.split("RUN --network=none")[0]`；L845断言`"PYO3_USE_ABI3_FORWARD_COMPATIBILITY" not in native`；L846断言`"rm -rf .venv" not in base and "rm -rf /opt/rnd/prewarm" not in native`；L847断言`"--mount=" not in native and "--mount=" not in base`；L848断言`"chown -R" not in native and "chmod -R" not in native`；L849断言`"--ignore-scripts" in native and "--package-import-method=copy" in native`。 调用`(ROOT / "tools/daytona/capability-snapshot.Dockerfile").read_text`、`(ROOT / "tools/daytona/capability-native-snapshot.Dockerfile").re…`、`native.split`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_source_build_does_not_silently_accept_pure_python_fallback`（L852–L863）：接收`tmp_path`。 控制顺序：L862断言`len(outputs["native_extensions"]) == 1`；L863断言`outputs["wheel_tags"] == ["py3-none-any"]`。 调用`zipfile.ZipFile`、`archive.writestr`、`pytest.raises`、`build.wheel_outputs`、`len`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_profile_workflows_execute_real_dependency_cli_checks_before_image_builds`（L866–L886）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L869遍历`("capability-profile.yml", "native-capability-profile.yml")`；L882断言`"tests/test_daytona_dependency_build.py" in preflight["run"]`；L883断言`"tests/test_daytona_dependency_image.py" in preflight["run"]`；L884断言`preflight["env"]["RND_REQUIRE_LANDLOCK"] == "1"`；L885断言`preflight["env"]["RND_REQUIRE_SECCOMP_BPF"] == "1"`；L886断言`steps.index(preflight) < steps.index(build_images)`。 调用`yaml.safe_load`、`(ROOT / ".github/workflows" / name).read_text`、`next`、`step.get`、`steps.index`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_native_fetch_and_install_both_copy_the_virtual_store`（L889–L904）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L892遍历`recipe.replace("\\\n", " ").split("&&")`；L894按`len(words) > 1 and words[0] == "pnpm" and words[1] in {"fetch", "install"}`分支；L895断言`words[1] not in commands`；L897断言`set(commands) == {"fetch", "install"}`；L898遍历`commands.values()`；L901断言`"--package-import-method=copy" in command`；L902断言`"--ignore-scripts" in command`；L903断言`"--frozen-lockfile" in command`。后续分支沿下方源码相同行号继续阅读。 调用`(ROOT / "tools/daytona/capability-native-snapshot.Dockerfile").re…`、`recipe.replace("\\\n", " ").split`、`recipe.replace`、`clause.split`、`len`、`set`、`commands.values`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_daytona_dependency_build.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L904。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`36368`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_daytona_dependency_build.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "ffd87a22143619a120fdd90b4a1cde370dc634272f1baba39e31930bbeeb901c"} -->
````python
# tests/test_daytona_dependency_build.py
"""Locked dependency build contracts; never execute source hooks in these tests."""

import ast
import base64
import ctypes
import hashlib
import inspect
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tomllib
import zipfile
from pathlib import Path, PurePosixPath, PureWindowsPath

import pytest

from scripts import daytona_dependency_build as build
from scripts import daytona_dependency_image as dependency_image
from scripts.daytona_native_capability_profile import ROOT


@pytest.fixture
def uv_cli(tmp_path):
    """Exercise the installed uv, with no user config, credentials or network."""
    executable = shutil.which("uv")
    assert executable, "Install the official uv CLI required by the repository test workflow"
    env = {key: os.environ[key] for key in ("PATH", "SYSTEMROOT", "WINDIR") if key in os.environ}
    env.update(
        HOME=str(tmp_path),
        USERPROFILE=str(tmp_path),
        TMP=str(tmp_path),
        TEMP=str(tmp_path),
        UV_CACHE_DIR=str(tmp_path / "uv-cache"),
        UV_PYTHON=sys.executable,
        UV_PYTHON_DOWNLOADS="never",
        UV_OFFLINE="1",
        UV_NO_CONFIG="1",
        UV_NO_PROGRESS="1",
        UV_LINK_MODE="copy",
    )

    def invoke(command, cwd, *, extra=()):
        result = subprocess.run(
            [executable, *command[1:], *extra, "--offline", "--no-config"],
            cwd=cwd,
            env=env,
            text=True,
            capture_output=True,
            timeout=60,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        return result

    return invoke


def metadata_wheel(directory, name):
    """A data-only wheel: no source, backend, importable code or install hooks."""
    path = directory / (name.replace("-", "_") + "-1.0-py3-none-any.whl")
    dist_info = name.replace("-", "_") + "-1.0.dist-info/"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(
            dist_info + "METADATA", f"Metadata-Version: 2.3\nName: {name}\nVersion: 1.0\n"
        )
        archive.writestr(
            dist_info + "WHEEL", "Wheel-Version: 1.0\nRoot-Is-Purelib: true\nTag: py3-none-any\n"
        )
        archive.writestr(dist_info + "RECORD", "")
    return path


def test_reviewed_bundled_native_graph_includes_required_sdists_and_exact_default_groups():
    with zipfile.ZipFile(ROOT / "templates/vendor/fastapiadmin.zip") as archive:
        project = build.normalize(archive.read("backend/pyproject.toml"))
        lock = build.normalize(archive.read("backend/uv.lock"))
        parsed = build.validate_python(project, lock)
        build.validate_node(
            archive.read("frontend/web/package.json"),
            archive.read("frontend/web/pnpm-lock.yaml"),
        )
    assert "sqlglot[rs]==27.8.0" in tomllib.loads(project.decode())["project"]["dependencies"]
    assert tomllib.loads(project.decode())["tool"]["uv"]["default-groups"] == ["dev"]
    spec = json.loads((ROOT / "scripts/daytona_dependency_build.lock.json").read_bytes())
    packages = {row["name"]: row for row in parsed["package"]}
    for record in spec["sdists"]:
        assert packages[record["name"]]["version"] == record["version"]
        assert packages[record["name"]]["sdist"]["hash"] == "sha256:" + record["sha256"]
        assert packages[record["name"]]["sdist"]["url"] == record["url"]
    assert {row["name"] for row in spec["sdists"]} == {
        "crcmod",
        "esdk-obs-python",
        "sqlglotrs",
    }


@pytest.mark.parametrize(
    "extra",
    [
        '[build-system]\nrequires=["untrusted"]\nbuild-backend="payload"\n',
        '[tool.uv.sources]\nfoo={path="../workspace"}\n',
        '[tool.uv]\nconfig-settings={hook="payload"}\n',
    ],
)
def test_candidate_build_backends_and_local_configuration_rejected(extra):
    with pytest.raises(ValueError, match="backend|configuration"):
        build.validate_python(
            ('[project]\nname="fixture"\nversion="1"\n' + extra).encode(),
            b"version=1\n",
        )


@pytest.mark.parametrize(
    "source",
    ['{path="../local"}', '{git="https://example.test/repo"}', '{virtual="../other"}'],
)
def test_local_and_workspace_lock_packages_rejected(source):
    with pytest.raises(ValueError, match="hashed registry"):
        build.validate_python(
            b'[project]\nname="fixture"\nversion="1"\n',
            ('[[package]]\nname="evil"\nsource=' + source + "\n").encode(),
        )


@pytest.mark.parametrize(
    "url",
    [
        "http://pypi.org/simple",
        "https://name:secret@pypi.org/simple",
        "https://pypi.org/simple?token=x",
        "https://evil.test/simple",
    ],
)
def test_registry_authentication_and_unreviewed_hosts_rejected(url):
    with pytest.raises(ValueError, match="official registry"):
        build.public_url(url, {"pypi.org"})


@pytest.mark.parametrize(
    "package,lock",
    [
        ({"dependencies": {"evil": "file:../payload"}}, "lockfileVersion: '9.0'"),
        (
            {"dependencies": {"evil": "https://evil.test/a.tgz"}},
            "lockfileVersion: '9.0'",
        ),
        (
            {"pnpm": {"patchedDependencies": {"a": "evil.patch"}}},
            "lockfileVersion: '9.0'",
        ),
        (
            {},
            "packages:\n  evil:\n    resolution:\n      tarball: https://evil.test/a.tgz\n",
        ),
        ({}, "importers:\n  ../workspace: {}\n"),
    ],
)
def test_node_hooks_local_sources_and_unhashed_artifacts_rejected(package, lock):
    with pytest.raises(ValueError):
        build.validate_node(json.dumps(package).encode(), lock.encode())


@pytest.mark.parametrize(
    "kind,name",
    [
        ("symlink", "package/link"),
        ("hardlink", "package/link"),
        ("file", "../escape"),
        ("file", "/absolute"),
        ("file", "package/.cargo/config.toml"),
    ],
)
def test_source_archive_does_not_extract_links_traversal_or_cargo_hooks(tmp_path, kind, name):
    path = tmp_path / "source.tar.gz"
    with tarfile.open(path, "w:gz") as archive:
        item = tarfile.TarInfo(name)
        item.type = {
            "file": tarfile.REGTYPE,
            "symlink": tarfile.SYMTYPE,
            "hardlink": tarfile.LNKTYPE,
        }[kind]
        item.linkname = "/outside"
        archive.addfile(item, io.BytesIO())
    with pytest.raises(ValueError, match="Unsafe"):
        build.extract_source(path, tmp_path / "output")
    assert not (tmp_path / "output").exists()


def test_built_wheel_replacement_preserves_other_hashes_and_markers(tmp_path):
    wheel = (tmp_path / "crcmod-1.7-cp314-cp314-linux_x86_64.whl").absolute()
    raw = (
        'crcmod==1.7 ; python_version >= "3.14" \\\n    --hash=sha256:'
        + "a" * 64
        + "\nother==1 \\\n    --hash=sha256:"
        + "b" * 64
        + "\n"
    )
    item = {
        "name": "crcmod",
        "version": "1.7",
        "wheel": str(wheel),
        "wheel_sha256": "c" * 64,
    }
    replaced = build.replace_source_requirements(raw, [item])
    assert "crcmod @ " + wheel.as_uri() + ' ; python_version >= "3.14"' in replaced
    assert "c" * 64 in replaced and "a" * 64 not in replaced and "b" * 64 in replaced
    with pytest.raises(ValueError, match="selected exactly once"):
        build.replace_source_requirements("other==1\n", [item])


@pytest.mark.parametrize("mode", ["basic", "native", "harness"])
def test_install_uses_locked_export_runtime_groups_no_project_hooks_or_sdists(
    tmp_path, monkeypatch, uv_cli, mode
):
    project = tmp_path / "runtime"
    project.mkdir()
    (project / "pyproject.toml").write_text('[project]\nname="test"\nversion="1"\n')
    (project / "uv.lock").write_text("version=1\n")
    calls = []
    monkeypatch.setattr(build, "BUILD", tmp_path)
    (tmp_path / "source-builds.json").write_text("[]")

    def run(command, cwd, **kwargs):
        calls.append(command)
        # Let the actual parser reject invalid argument names and mappings.
        uv_cli(command, cwd, extra=("--help",))
        if command[1] == "export":
            (tmp_path / (project.name + "-requirements.lock.txt")).write_text(
                "package==1 --hash=sha256:" + "a" * 64 + "\n"
            )

    monkeypatch.setattr(build, "run", run)
    build.install(project, basic=mode == "basic", harness=mode == "harness")
    assert "--locked" in calls[0] and "--no-emit-project" in calls[0]
    assert ("--no-dev" in calls[0]) is (mode == "basic")
    assert ("--all-extras" in calls[0]) is (mode == "harness")
    assert str(project / ".venv") in calls[1]
    assert "--require-hashes" in calls[2] and "--no-build" in calls[2]
    assert calls[2][-1] == str(tmp_path / "runtime-requirements.lock.txt")


@pytest.mark.skipif(os.name == "nt", reason="Image builder uses Linux venv interpreter paths")
@pytest.mark.parametrize(
    "mode,expected",
    [
        ("basic", {"runtime"}),
        ("native", {"runtime", "dev"}),
        ("harness", {"runtime", "dev", "extra"}),
    ],
)
def test_install_real_uv_offline_hashed_wheel_dry_run(
    tmp_path, monkeypatch, uv_cli, mode, expected
):
    project = tmp_path / "project"
    project.mkdir()
    wheelhouse = tmp_path / "wheels"
    wheelhouse.mkdir()
    wheels = {
        group: metadata_wheel(wheelhouse, "fixture-" + group)
        for group in ("runtime", "dev", "extra")
    }
    (project / "pyproject.toml").write_text(
        '[project]\nname="fixture"\nversion="1"\nrequires-python=">=3.14"\n'
        'dependencies=["fixture-runtime==1.0"]\n'
        '[project.optional-dependencies]\nextra=["fixture-extra==1.0"]\n'
        '[dependency-groups]\ndev=["fixture-dev==1.0"]\n'
        "[tool.uv]\npackage=false\n"
    )
    lock = (
        'version=1\nrevision=3\nrequires-python=">=3.14"\n'
        '[[package]]\nname="fixture"\nversion="1"\nsource={virtual="."}\n'
        'dependencies=[{name="fixture-runtime"}]\n'
        '[package.optional-dependencies]\nextra=[{name="fixture-extra"}]\n'
        '[package.dev-dependencies]\ndev=[{name="fixture-dev"}]\n'
        "[package.metadata]\nrequires-dist=["
        '{name="fixture-runtime",specifier="==1.0"},'
        '{name="fixture-extra",specifier="==1.0",marker="extra == \'extra\'"}]\n'
        'provides-extras=["extra"]\n'
        '[package.metadata.requires-dev]\ndev=[{name="fixture-dev",specifier="==1.0"}]\n'
    )
    for group, wheel in wheels.items():
        lock += (
            f'[[package]]\nname="fixture-{group}"\nversion="1.0"\n'
            'source={registry="https://pypi.org/simple"}\n'
            f'wheels=[{{url="https://files.pythonhosted.org/packages/{wheel.name}",'
            f'hash="sha256:{build.sha(wheel)}",size={wheel.stat().st_size}}}]\n'
        )
    (project / "uv.lock").write_text(lock)
    original = {name: build.sha(project / name) for name in ("pyproject.toml", "uv.lock")}
    wheel = wheels["runtime"]
    (tmp_path / "source-builds.json").write_text(
        json.dumps(
            [
                {
                    "name": "fixture-runtime",
                    "version": "1.0",
                    "wheel": str(wheel),
                    "wheel_sha256": build.sha(wheel),
                }
            ]
        )
    )
    monkeypatch.setattr(build, "BUILD", tmp_path)
    monkeypatch.setattr(build, "PYTHON", sys.executable)
    results = []

    def run(command, cwd, **kwargs):
        # Only metadata-only local wheels can be resolved; nothing is installed.
        extra = (
            ("--dry-run", "--no-index", "--find-links", str(wheelhouse))
            if command[1:3] == ["pip", "sync"]
            else ()
        )
        results.append(uv_cli(command, cwd, extra=extra))

    monkeypatch.setattr(build, "run", run)
    build.install(project, basic=mode == "basic", harness=mode == "harness")
    requirements = (tmp_path / "project-requirements.lock.txt").read_text()
    for group, wheel in wheels.items():
        assert ("fixture-" + group in requirements) is (group in expected)
        assert (build.sha(wheel) in requirements) is (group in expected)
    assert ("fixture-runtime @ " in requirements) is (mode == "native")
    assert f"Would install {len(expected)} package" in results[-1].stderr
    assert original == {name: build.sha(project / name) for name in original}
    assert not list((project / ".venv").rglob("fixture*.dist-info"))


def test_fetch_real_uv_parser_keeps_install_requirements_flag(tmp_path, monkeypatch, uv_cli):
    project = tmp_path / "project"
    project.mkdir()
    (project / "uv.lock").write_text("package=[]\n")
    wheel = metadata_wheel(tmp_path, "fixture-tool")
    lock = tmp_path / "tools.json"
    lock.write_text(
        json.dumps(
            {
                "tools": [
                    {
                        "url": "https://files.pythonhosted.org/" + wheel.name,
                        "sha256": build.sha(wheel),
                    }
                ],
                "sdists": [],
            }
        )
    )
    calls = []
    monkeypatch.setattr(build, "BUILD", tmp_path)
    monkeypatch.setattr(build.os, "geteuid", lambda: 1000, raising=False)
    monkeypatch.setattr(build, "download", lambda *args: wheel)

    def run(command, cwd, **kwargs):
        calls.append((command, kwargs))
        uv_cli(command, cwd, extra=("--help",))

    monkeypatch.setattr(build, "run", run)
    build.fetch(lock, project)
    command, kwargs = calls[-1]
    assert command[1:3] == ["pip", "install"]
    assert command[-2:] == ["-r", str(tmp_path / "build-tools.txt")]
    assert {"--no-deps", "--no-build", "--require-hashes", "--no-index"} <= set(command)
    assert kwargs == {"offline": True}


@pytest.mark.parametrize("package", ["crcmod", "esdk-obs-python", "sqlglotrs"])
def test_source_build_real_uv_parser_without_executing_backend(
    tmp_path, monkeypatch, uv_cli, package
):
    (tmp_path / "sources.json").write_text(
        json.dumps([{"name": package, "source": str(tmp_path / "never-execute")}])
    )
    monkeypatch.setattr(build, "BUILD", tmp_path)

    class ParserChecked(Exception):
        pass

    def run(command, cwd, **kwargs):
        uv_cli(command, cwd, extra=("--help",))
        assert command[1:4] == ["build", "--wheel", "--no-build-isolation"]
        assert "--offline" in command and kwargs == {"offline": True}
        if package == "sqlglotrs":
            assert command[-3:-1] == ["--config-setting", "build-args=--locked --offline"]
        assert Path(command[-1]).name == "never-execute"
        raise ParserChecked

    monkeypatch.setattr(build, "run", run)
    with pytest.raises(ParserChecked):
        build.build_sources()


def test_every_dependency_subprocess_uses_the_bounded_nonroot_runner():
    tree = ast.parse(inspect.getsource(build))
    calls = [
        (function.name, node.func.attr)
        for function in tree.body
        if isinstance(function, ast.FunctionDef)
        for node in ast.walk(function)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id == "subprocess"
    ]
    assert calls == [("run", "run")]


@pytest.fixture
def metadata_image(tmp_path, monkeypatch, request):
    """Map only fixed image paths; descriptor reads and hashes remain real."""
    image = tmp_path / "image"
    descriptor_bytes = b"descriptor-content-must-not-be-emitted" + getattr(request, "param", b"\n")

    def image_path(value):
        path = Path(value)
        if path.is_relative_to("/opt/rnd"):
            return image / path.relative_to("/opt/rnd")
        return path

    builder = image / "build"
    builder.mkdir(parents=True)
    interpreter = image / "bin/python-build"
    interpreter.parent.mkdir()
    interpreter.write_bytes(b"sealed interpreter identity")
    interpreter.chmod(0o444)
    descriptors = {}
    for profile, names in {
        "runtime/python-basic": ("pyproject.toml", "uv.lock"),
        "runtime/fastapiadmin": (
            "backend/pyproject.toml",
            "backend/uv.lock",
            "frontend/package.json",
            "frontend/pnpm-lock.yaml",
        ),
        "harness": ("pyproject.toml", "uv.lock"),
    }.items():
        for name in names:
            path = image / profile / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(descriptor_bytes)
            path.chmod(0o444)
            descriptors[path] = build.sha(path)
    (image / "bin/dependency-build.lock.json").write_text('{"tools": []}')
    (image / "build-tools-manifest.json").write_text(
        json.dumps({"installed_tree_sha256": "a" * 64})
    )
    (builder / "source-builds.json").write_text("[]")
    monkeypatch.setattr(build, "BUILD", builder)
    monkeypatch.setattr(build, "PYTHON_BUILD", interpreter)
    monkeypatch.setattr(build, "Path", image_path)
    monkeypatch.setattr(build.os, "geteuid", lambda: 1000, raising=False)
    return image, descriptors


def assert_metadata_config_paths(env, path_type=Path):
    home = path_type(env["HOME"])
    for key, filename in (
        ("npm_config_userconfig", "user.npmrc"),
        ("npm_config_globalconfig", "global.npmrc"),
    ):
        config = path_type(env[key])
        assert config.parent == home
        assert config.name == filename


@pytest.mark.parametrize(
    "path_type,home",
    [
        (PurePosixPath, "/tmp/build/metadata-fresh"),
        (PureWindowsPath, r"C:\Users\runner\Temp\build\metadata-fresh"),
    ],
)
@pytest.mark.parametrize("key", ["npm_config_userconfig", "npm_config_globalconfig"])
def test_metadata_config_paths_require_exact_home_and_filename_on_both_platforms(
    path_type, home, key
):
    home = path_type(home)
    env = {
        "HOME": str(home),
        "npm_config_userconfig": str(home / "user.npmrc"),
        "npm_config_globalconfig": str(home / "global.npmrc"),
    }
    assert_metadata_config_paths(env, path_type)
    filename = path_type(env[key]).name
    rejected_paths = [
        home.parent / filename,
        home.with_name(home.name + "-other") / filename,
        home / "nested" / filename,
        home / ".." / filename,
        home / (filename + ".other"),
        path_type(filename),
    ]
    if path_type is PureWindowsPath:
        rejected_paths += [
            path_type("D:/") / home.relative_to(home.anchor) / filename,
            path_type("//server/share") / home.relative_to(home.anchor) / filename,
        ]
    for rejected in rejected_paths:
        with pytest.raises(AssertionError):
            assert_metadata_config_paths({**env, key: str(rejected)}, path_type)


@pytest.mark.parametrize(
    "interpreter",
    [
        PurePosixPath("/opt/rnd/bin/python-build"),
        PureWindowsPath(r"C:\image\bin\python-build"),
    ],
)
def test_collect_preserves_interpreter_command_path_flavor(tmp_path, monkeypatch, interpreter):
    inputs = tmp_path / "inputs.json"
    inputs.write_text('{"normalized_descriptors": {}}')
    monkeypatch.setattr(build, "PYTHON_BUILD", interpreter)

    class ProbeChecked(Exception):
        pass

    def probe(command, cwd, **kwargs):
        assert command[0] == str(interpreter)
        assert command[1:5] == ["-I", "-S", "-B", "-c"]
        assert cwd == build.BUILD
        assert kwargs == {"offline": True, "metadata": True}
        raise ProbeChecked

    monkeypatch.setattr(build, "run", probe)
    with pytest.raises(ProbeChecked):
        build.collect(inputs, tmp_path / "must-not-exist.json")


@pytest.mark.parametrize("native", [False, True])
@pytest.mark.parametrize("metadata_image", [b"\n", b"\r\n"], indirect=True, ids=["lf", "crlf"])
def test_collect_all_probes_are_offline_bounded_and_do_not_inherit_configuration(
    tmp_path, monkeypatch, metadata_image, capsys, native
):
    image, descriptors = metadata_image
    secret = "inherited-secret-must-not-be-emitted"
    for name in (
        "UV_CACHE_DIR",
        "UV_CONFIG_FILE",
        "HOME",
        "XDG_CONFIG_HOME",
        "PYTHONPATH",
        "NODE_OPTIONS",
        "NPM_TOKEN",
        "npm_config_userconfig",
        "RUSTUP_HOME",
        "RUSTC_WRAPPER",
        "LD_PRELOAD",
        "HTTP_PROXY",
    ):
        monkeypatch.setenv(name, secret)
    prefix = "backend/" if native else ""
    inputs = tmp_path / "inputs.json"
    hashes = {
        prefix + name: next(iter(descriptors.values())) for name in ("pyproject.toml", "uv.lock")
    }
    original = {"original_descriptors": hashes, "normalized_descriptors": hashes}
    if native:
        roles = build.native_descriptor_roles()
        original["descriptor_roles"] = roles
        payload = next(iter(descriptors)).read_bytes()
        names = [name for paths in roles.values() for name in paths]
        hashes.update(dict.fromkeys(names, next(iter(descriptors.values()))))
        original["source_descriptor_bytes"] = {
            name: base64.b64encode(payload).decode("ascii")
            for name in [*roles["portable_launcher"], *roles["auxiliary_source"]]
        }
        original["harness_descriptors"] = {
            name: build.sha(image / "harness" / name) for name in ("pyproject.toml", "uv.lock")
        }
    inputs.write_text(json.dumps(original))
    calls = []

    def probe(command, **kwargs):
        calls.append(command)
        assert kwargs["cwd"].parent == image / "build"
        assert kwargs["cwd"].name.startswith("metadata-")
        assert not list(kwargs["cwd"].iterdir())
        assert kwargs["timeout"] == 60
        assert kwargs["check"] is True and kwargs["capture_output"] is True
        assert kwargs["text"] is True and kwargs["preexec_fn"] is build.limits
        env = kwargs["env"]
        assert secret not in json.dumps(env)
        assert env["UV_CACHE_DIR"] == str(image / "build/uv-cache")
        assert env["HOME"] == str(kwargs["cwd"])
        assert env["UV_OFFLINE"] == env["UV_NO_CONFIG"] == "1"
        assert env["CARGO_NET_OFFLINE"] == "true"
        assert env["UV_PYTHON_DOWNLOADS"] == "never"
        assert env["RUSTUP_AUTO_INSTALL"] == env["COREPACK_ENABLE_NETWORK"] == "0"
        assert env["DISABLE_V8_COMPILE_CACHE"] == env["NODE_DISABLE_COMPILE_CACHE"] == "1"
        assert_metadata_config_paths(env)
        if command[0] == str(build.PYTHON_BUILD):
            assert command[1:5] == ["-I", "-S", "-B", "-c"]
            stdout = json.dumps({"version": [3, 14, 7], "machine": "x86_64", "system": "Linux"})
        else:
            stdout = {
                build.UV: "uv 0.12.20",
                "/usr/local/bin/node": "v22.23.2",
                "/usr/bin/dpkg-query": "package=1",
                "/usr/local/cargo/bin/rustc": "rustc 1.85.1",
                "/usr/bin/cc": "cc (Debian) 12.2.0",
                "/usr/local/bin/pnpm": "9.15.3",
            }[command[0]]
        return subprocess.CompletedProcess(command, 0, stdout=stdout, stderr=secret)

    monkeypatch.setattr(build.subprocess, "run", probe)
    output = tmp_path / "output.json"
    build.collect(inputs, output, native=native)
    collected = json.loads(output.read_text())
    assert collected["toolchain"]["python"] == str(build.PYTHON_BUILD.resolve(strict=True))
    assert collected["original_descriptors"] == original["original_descriptors"]
    assert collected["normalized_descriptors"] == original["normalized_descriptors"]
    if native:
        assert collected["descriptor_roles"] == build.native_descriptor_roles()
        assert "source_descriptor_bytes" not in collected
        assert not (image / "runtime/fastapiadmin/frontend/app").exists()
        assert not (image / "runtime/fastapiadmin/frontend/docs").exists()
    assert {path: build.sha(path) for path in descriptors} == descriptors
    assert len(calls) == (7 if native else 4)
    assert not any(command[1:3] == ["python", "find"] for command in calls)
    assert secret not in output.read_text()
    assert "descriptor-content-must-not-be-emitted" not in output.read_text()
    profile = "fastapiadmin" if native else "python-basic"
    record = {
        **collected,
        "recipe_identity": "a" * 64,
        "roots": dependency_image.ROOTS[profile],
        "groups": dependency_image.GROUPS[profile],
        "entries": {},
        "installed_tree_sha256": dependency_image.digest({}),
    }
    assert (
        dependency_image.validate_manifest({"schema": 1, "profiles": {profile: record}}, profile)
        == record
    )
    assert not list((image / "build").glob("metadata-*"))
    assert capsys.readouterr() == ("", "")


@pytest.mark.parametrize("metadata_image", [b"\n", b"\r\n"], indirect=True, ids=["lf", "crlf"])
@pytest.mark.parametrize(
    "field", ["source_descriptor_bytes", "original_descriptors", "normalized_descriptors"]
)
def test_native_source_descriptor_line_endings_require_exact_byte_hash_identity(
    tmp_path, monkeypatch, metadata_image, field
):
    _, descriptors = metadata_image
    payload = next(iter(descriptors)).read_bytes()
    changed = (
        payload.replace(b"\r\n", b"\n") if b"\r\n" in payload else payload.replace(b"\n", b"\r\n")
    )
    expected_hash = hashlib.sha256(payload).hexdigest()
    changed_hash = hashlib.sha256(changed).hexdigest()
    assert changed_hash != expected_hash
    assert set(descriptors.values()) == {expected_hash}
    roles = build.native_descriptor_roles()
    hashes = {name: expected_hash for paths in roles.values() for name in paths}
    original = {
        "descriptor_roles": roles,
        "original_descriptors": hashes,
        "normalized_descriptors": dict(hashes),
        "source_descriptor_bytes": {
            name: base64.b64encode(payload).decode("ascii")
            for name in [*roles["portable_launcher"], *roles["auxiliary_source"]]
        },
    }
    assert build.validate_native_descriptor_inputs(original) == roles
    monkeypatch.setattr(
        build, "run", lambda *a, **kw: pytest.fail("Executed before descriptor data validation")
    )
    inputs, output = tmp_path / "inputs.json", tmp_path / "must-not-exist.json"
    for name in original["source_descriptor_bytes"]:
        replacement = (
            base64.b64encode(changed).decode("ascii")
            if field == "source_descriptor_bytes"
            else changed_hash
        )
        drifted = {**original, field: {**original[field], name: replacement}}
        inputs.write_text(json.dumps(drifted))
        with pytest.raises(ValueError, match="source-only descriptor bytes or immutable hashes"):
            build.collect(inputs, output, native=True)
        assert not output.exists()


@pytest.mark.parametrize("metadata", [False, True])
def test_metadata_and_dependency_commands_cannot_run_as_root(monkeypatch, tmp_path, metadata):
    monkeypatch.setattr(build.os, "geteuid", lambda: 0, raising=False)
    with pytest.raises(ValueError, match="non-root"):
        build.run(["must-not-execute"], tmp_path, metadata=metadata)


@pytest.mark.parametrize("failure", ["timeout", "exit"])
def test_collect_probe_failures_leave_no_manifest_or_raw_output(
    tmp_path, monkeypatch, metadata_image, capsys, failure
):
    image, _ = metadata_image
    inputs = tmp_path / "inputs.json"
    inputs.write_text('{"normalized_descriptors": {}}')
    output = tmp_path / "output.json"
    private = "private-subprocess-output"

    def fail(command, **kwargs):
        if failure == "timeout":
            raise subprocess.TimeoutExpired(command, 60, output=private, stderr=private)
        raise subprocess.CalledProcessError(1, command, output=private, stderr=private)

    monkeypatch.setattr(build.subprocess, "run", fail)
    with pytest.raises((subprocess.TimeoutExpired, subprocess.CalledProcessError)) as error:
        build.collect(inputs, output)
    assert private not in str(error.value)
    assert not output.exists()
    assert not list((image / "build").glob("metadata-*"))
    assert capsys.readouterr() == ("", "")


def test_build_commands_keep_existing_limits_and_validated_project_configuration(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(build.os, "geteuid", lambda: 1000, raising=False)

    def execute(command, **kwargs):
        assert kwargs["timeout"] == 1800
        assert kwargs["cwd"] == tmp_path
        assert kwargs["preexec_fn"] is build.limits
        assert kwargs["capture_output"] is False
        assert "UV_NO_CONFIG" not in kwargs["env"]
        assert kwargs["env"]["UV_OFFLINE"] == "1"
        assert kwargs["env"]["CARGO_NET_OFFLINE"] == "true"
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(build.subprocess, "run", execute)
    build.run([build.UV, "build", "--offline"], tmp_path, offline=True)


@pytest.mark.skipif(
    sys.platform != "linux" or getattr(os, "geteuid", lambda: 0)() == 0,
    reason="Actual read-only Linux builder regression requires a non-root process",
)
def test_metadata_real_uv_and_python_ignore_unwritable_cache_config_and_secrets(
    tmp_path, monkeypatch, capsys
):
    uv = shutil.which("uv")
    assert uv, "Install the official uv CLI required by the repository test workflow"
    inherited = tmp_path / "inherited-readonly"
    inherited.mkdir()
    config = inherited / "uv.toml"
    config.write_text("invalid configuration must never be read = [\n")
    config.chmod(0o444)
    inherited.chmod(0o555)
    original = (config.read_bytes(), config.stat().st_mtime_ns, inherited.stat().st_mtime_ns)
    builder = tmp_path / "build"
    builder.mkdir()
    monkeypatch.setattr(build, "BUILD", builder)
    secret = "inherited-secret-must-not-be-emitted"
    for key in (
        "HOME",
        "UV_CACHE_DIR",
        "XDG_CONFIG_HOME",
        "XDG_CACHE_HOME",
        "PYTHONHOME",
        "PYTHONPATH",
        "CARGO_HOME",
        "RUSTUP_HOME",
    ):
        monkeypatch.setenv(key, str(inherited))
    monkeypatch.setenv("UV_CONFIG_FILE", str(config))
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", secret)
    monkeypatch.setenv("NODE_OPTIONS", "--require=" + str(config))
    monkeypatch.setenv("npm_config_userconfig", str(config))
    monkeypatch.setenv("HTTPS_PROXY", "https://" + secret + ".invalid")
    watcher = -1
    try:
        # Negative control: a read-only uv lookup itself tries to initialize its
        # inherited cache. The fixed metadata path must not use this operation.
        control = subprocess.run(
            [uv, "python", "find", sys.executable],
            cwd=builder,
            env={
                "UV_CACHE_DIR": str(inherited),
                "UV_NO_CONFIG": "1",
                "UV_OFFLINE": "1",
                "UV_PYTHON_DOWNLOADS": "never",
            },
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert control.returncode != 0 and "Permission denied" in control.stderr
        # Observe actual opens/reads/writes, rather than infer isolation only
        # from a successful return code and unchanged bytes.
        libc = ctypes.CDLL(None, use_errno=True)
        watcher = libc.inotify_init1(os.O_NONBLOCK | os.O_CLOEXEC)
        assert watcher >= 0
        for path in (inherited, config):
            assert libc.inotify_add_watch(watcher, os.fsencode(path), 0x00000FFF) >= 0
        version = build.run([uv, "--version"], builder, metadata=True)
        assert version.stdout.startswith("uv ")
        result = build.run(
            [
                sys.executable,
                "-I",
                "-S",
                "-B",
                "-c",
                "import os,resource,sys; "
                "assert os.geteuid() != 0; "
                "assert sys.flags.isolated and sys.flags.no_site and sys.dont_write_bytecode; "
                "assert not any(key in os.environ for key in "
                "('AWS_SECRET_ACCESS_KEY','NODE_OPTIONS','UV_CONFIG_FILE','HTTPS_PROXY',"
                "'PYTHONHOME','PYTHONPATH')); "
                "assert resource.getrlimit(resource.RLIMIT_CPU) == (1800,1800); "
                "assert resource.getrlimit(resource.RLIMIT_AS) == (6*1024**3,6*1024**3); "
                "print('isolated')",
            ],
            builder,
            metadata=True,
        )
        assert result.stdout.strip() == "isolated"
        with pytest.raises(BlockingIOError):
            os.read(watcher, 65536)
        assert not list(builder.iterdir())
        assert list(inherited.iterdir()) == [config]
        assert original == (
            config.read_bytes(),
            config.stat().st_mtime_ns,
            inherited.stat().st_mtime_ns,
        )
        assert config.stat().st_mode & 0o777 == 0o444
        assert inherited.stat().st_mode & 0o777 == 0o555
        assert capsys.readouterr() == ("", "")
    finally:
        if watcher >= 0:
            os.close(watcher)
        # Restore only this test fixture for pytest cleanup, never image paths.
        inherited.chmod(0o755)


def test_recipes_separate_nonroot_offline_build_and_never_relocate_environments():
    base = (ROOT / "tools/daytona/capability-snapshot.Dockerfile").read_text()
    native = (ROOT / "tools/daytona/capability-native-snapshot.Dockerfile").read_text()
    assert "AS dependency-builder" in base and "AS dependency-builder" in native
    assert "RUN --network=none /opt/rnd/bin/python-build" in native
    assert "USER daytona" in native.split("RUN --network=none")[0]
    assert "PYO3_USE_ABI3_FORWARD_COMPATIBILITY" not in native
    assert "rm -rf .venv" not in base and "rm -rf /opt/rnd/prewarm" not in native
    assert "--mount=" not in native and "--mount=" not in base
    assert "chown -R" not in native and "chmod -R" not in native
    assert "--ignore-scripts" in native and "--package-import-method=copy" in native


def test_native_source_build_does_not_silently_accept_pure_python_fallback(tmp_path):
    path = tmp_path / "crcmod.whl"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("crcmod-1.7.dist-info/WHEEL", "Wheel-Version: 1.0\nTag: py3-none-any\n")
        archive.writestr("crcmod/__init__.py", "# pure fallback")
    with pytest.raises(ValueError, match="no native extension"):
        build.wheel_outputs(path, "crcmod")
    with zipfile.ZipFile(path, "a") as archive:
        archive.writestr("crcmod/_crcfunext.cpython-314-x86_64-linux-gnu.so", b"fixture ELF")
    outputs = build.wheel_outputs(path, "crcmod")
    assert len(outputs["native_extensions"]) == 1
    assert outputs["wheel_tags"] == ["py3-none-any"]


def test_profile_workflows_execute_real_dependency_cli_checks_before_image_builds():
    import yaml

    for name in ("capability-profile.yml", "native-capability-profile.yml"):
        document = yaml.safe_load((ROOT / ".github/workflows" / name).read_text(encoding="utf-8"))
        steps = document["jobs"]["local-service"]["steps"]
        preflight = next(
            step
            for step in steps
            if step.get("name") == "Check ordinary launcher behavior and strict receipt contracts"
        )
        build_images = next(
            step
            for step in steps
            if step.get("name") == "Build pinned release locally and lock immutable images"
        )
        assert "tests/test_daytona_dependency_build.py" in preflight["run"]
        assert "tests/test_daytona_dependency_image.py" in preflight["run"]
        assert preflight["env"]["RND_REQUIRE_LANDLOCK"] == "1"
        assert preflight["env"]["RND_REQUIRE_SECCOMP_BPF"] == "1"
        assert steps.index(preflight) < steps.index(build_images)


def test_native_fetch_and_install_both_copy_the_virtual_store():
    recipe = (ROOT / "tools/daytona/capability-native-snapshot.Dockerfile").read_text()
    commands = {}
    for clause in recipe.replace("\\\n", " ").split("&&"):
        words = clause.split()
        if len(words) > 1 and words[0] == "pnpm" and words[1] in {"fetch", "install"}:
            assert words[1] not in commands
            commands[words[1]] = words
    assert set(commands) == {"fetch", "install"}
    for command in commands.values():
        # fetch has already materialized node_modules/.pnpm. Adding copy only to
        # the subsequent install cannot undo existing links to the package store.
        assert "--package-import-method=copy" in command
        assert "--ignore-scripts" in command
        assert "--frozen-lockfile" in command
    assert "--offline" in commands["install"]
````
