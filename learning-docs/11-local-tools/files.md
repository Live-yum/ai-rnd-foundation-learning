# Continue、Plop与Aider：本阶段文件

[返回阶段导读](README.md)

按导读先后理解；同一组需全部写完再导入或运行测试。以下路径相对学生项目根目录，不是教材目录。所有文件逐字节收录，代码分段的第一行路径注释需删除。锁文件在 sources/locks，截图及Vue构建快照编码在 sources/assets 下，先读实现模块，需要校对时再打开资源。

- [scripts/ci_aider_workflow.py](sources/scripts__ci_aider_workflow_py--001.md)：基础产品实际Aider编排验收；1 段
- [scripts/ci_local_embeddings.py](sources/scripts__ci_local_embeddings_py--001.md)：固定真实权重的本机推理验收和服务；1 段
- [scripts/ci_native_tools.py](sources/scripts__ci_native_tools_py--001.md)：原生Plop/Aider修复与可恢复中断验收；1 段
- [scripts/ci_toolchain.py](sources/scripts__ci_toolchain_py--001.md)：实际解析、Continue、MCP和Aider串联验收；1 段
- [tests/test_aider_offline.py](sources/tests__test_aider_offline_py--001.md)：可重复的验收用例；1 段
- [tests/test_continue_index.py](sources/tests__test_continue_index_py--001.md)：可重复的验收用例；1 段
- [tests/test_local_embeddings.py](sources/tests__test_local_embeddings_py--001.md)：可重复的验收用例；1 段
- [tests/test_native_tools.py](sources/tests__test_native_tools_py--001.md)：可重复的验收用例；1 段
- [tests/test_toolchain.py](sources/tests__test_toolchain_py--001.md)：可重复的验收用例；1 段
- [tools/aider/.python-version](sources/tools__aider___python-version--001.md)：Aider独立运行环境；1 段
- [tools/aider/offline_runner.py](sources/tools__aider__offline_runner_py--001.md)：Aider本机禁网入口；1 段
- [tools/aider/pyproject.toml](sources/tools__aider__pyproject_toml--001.md)：Aider独立运行环境；1 段
- [tools/aider/uv.lock](sources/locks/tools__aider__uv_lock--001.md)：精确依赖锁；1 段
- [tools/browser/Dockerfile](sources/tools__browser__Dockerfile--001.md)：项目根配置或说明；1 段
- [tools/browser/LICENSE.playwright](sources/tools__browser__LICENSE_playwright--001.md)：项目根配置或说明；1 段
- [tools/browser/SECCOMP-REVIEW.md](sources/tools__browser__SECCOMP-REVIEW_md--001.md)：项目根配置或说明；1 段
- [tools/browser/review-only-v2/README.md](sources/tools__browser__review-only-v2__README_md--001.md)：项目根配置或说明；1 段
- [tools/browser/review-only-v2/chromium141-docker28-native-amd64.proposal.json](sources/tools__browser__review-only-v2__chromium141-docker28-native-amd64_proposal_json--001.md)：项目根配置或说明；1 段
- [tools/browser/review-only-v2/proposal-manifest.json](sources/tools__browser__review-only-v2__proposal-manifest_json--001.md)：项目根配置或说明；1 段
- [tools/browser/review-only-v2/review_profile.py](sources/tools__browser__review-only-v2__review_profile_py--001.md)：项目根配置或说明；1 段
- [tools/browser/review-only/LICENSE.moby](sources/tools__browser__review-only__LICENSE_moby--001.md)：项目根配置或说明；1 段
- [tools/browser/review-only/README.md](sources/tools__browser__review-only__README_md--001.md)：项目根配置或说明；1 段
- [tools/browser/review-only/chromium141-docker28-amd64.proposal.json](sources/tools__browser__review-only__chromium141-docker28-amd64_proposal_json--001.md)：项目根配置或说明；1 段
- [tools/browser/review-only/moby-v28.0.4-default.json](sources/tools__browser__review-only__moby-v28_0_4-default_json--001.md)：项目根配置或说明；1 段
- [tools/browser/review-only/proposal-manifest.json](sources/tools__browser__review-only__proposal-manifest_json--001.md)：项目根配置或说明；1 段
- [tools/browser/seccomp.playwright-1.56.1.json](sources/tools__browser__seccomp_playwright-1_56_1_json--001.md)：项目根配置或说明；1 段
- [tools/embeddings/pyproject.toml](sources/tools__embeddings__pyproject_toml--001.md)：真实本机向量模型的独立验证环境；1 段
- [tools/embeddings/uv.lock](sources/locks/tools__embeddings__uv_lock--001.md)：精确依赖锁；1 段
- [tools/node/build.mjs](sources/tools__node__build_mjs--001.md)：本机Node索引运行边界；1 段
- [tools/node/continue-host.mjs](sources/tools__node__continue-host_mjs--001.md)：本机Node索引运行边界；1 段
- [tools/node/continue-runner.mjs](sources/tools__node__continue-runner_mjs--001.md)：本机Node索引运行边界；1 段
- [tools/node/no-network.cjs](sources/tools__node__no-network_cjs--001.md)：本机Node索引运行边界；1 段
- [tools/node/package-lock.json](sources/locks/tools__node__package-lock_json--001.md)：本机Node索引运行边界；1 段
- [tools/node/package.json](sources/tools__node__package_json--001.md)：本机Node索引运行边界；1 段
- [tools/node/plop-runner.mjs](sources/tools__node__plop-runner_mjs--001.md)：原生业务规则的真实Plop生成入口与模板；1 段
- [tools/node/templates/rule.java.hbs](sources/tools__node__templates__rule_java_hbs--001.md)：原生业务规则的真实Plop生成入口与模板；1 段
- [tools/node/templates/rule.py.hbs](sources/tools__node__templates__rule_py_hbs--001.md)：原生业务规则的真实Plop生成入口与模板；1 段
- [tools/node/templates/rule.vue.hbs](sources/tools__node__templates__rule_vue_hbs--001.md)：原生业务规则的真实Plop生成入口与模板；1 段
- [tools/node/upstream/FullTextSearchCodebaseIndex.ts](sources/tools__node__upstream__FullTextSearchCodebaseIndex_ts--001.md)：固定的Continue开源全文索引组件及许可证；1 段
- [tools/node/upstream/LICENSE](sources/tools__node__upstream__LICENSE--001.md)：固定的Continue开源全文索引组件及许可证；1 段
- [tools/node/upstream/manifest.json](sources/tools__node__upstream__manifest_json--001.md)：固定的Continue开源全文索引组件及许可证；1 段
