## 显式授权的真实模型客服端到端验收

常规Actions用明确模型响应夹具验证编排，同时真实运行数据库、浏览器和本机工具。真实服务商测试是有调用成本的另一项验收，不随普通PR自动调用。它必须在可信指定分支、获准的GitHub Environment中运行；测试脚本再次核对仓库、分支、事件与目标，不允许切换服务商或模型来绕过失败。本章说明如何执行及判断结果，不预先声称任何模板已经通过。

### 环境配置如何进入模型网关

专用验收使用GitHub Environment `rnd`。环境Secret名称是`APK_KEY`，只在模型测试步骤中映射成平台读取的`API_KEY`；两个变量名各有用途，不为拼写一致复制或打印密钥。环境Variables提供`BASE_URL`和`MODE`，当前授权目标分别为`https://api.deepseek.com`和`deepseek-flash`。关键接线如下，表达式由GitHub解释，不能替换为密钥正文提交：

```yaml
environment: rnd
# 仅实际调用模型的步骤声明以下env；安装依赖的步骤不注入密钥
env:
  API_KEY: ${{ secrets.APK_KEY }}
  BASE_URL: ${{ vars.BASE_URL }}
  MODE: ${{ vars.MODE }}
```

`environment`属于job，`env`属于其模型调用step；完整可执行层级见源码附录。环境保护规则若要求批准，由有权限的人批准，不改环境、不绕过审批、不把Secret放进源码。未绑定该Environment的普通测试不能作为已取得凭据的证明。

### 在客服分支手动触发，先核对精确提交

当前客服开发分支为`feat/customer-service-acceptance`。在仓库的Actions中选择`.github/workflows/native-probe.yml`对应的工作流，打开Run workflow：

1. 在分支选择器选`feat/customer-service-acceptance`，不要使用默认分支代码代替待测客服代码。
2. 明确勾选`real_model=true`；默认false不调用付费模型。
3. `expected_sha`填写已审查的完整40位提交SHA。先在该分支用`git rev-parse HEAD`核对，再与GitHub分支头核对；不是短SHA、分支名或过去成功的提交。
4. 确认目标和费用授权后手动运行。job在模型访问之前要求`expected_sha`与这次`GITHUB_SHA`完全一致，不相等立即停止。
5. 分别查看`python-basic`、`fastapiadmin`、`yudao-vben`三行，记录每行的提交、run ID、attempt与终态。某行失败或pending时不宣布整个矩阵通过。

`.github/workflows/real-model.yml`是专用的手动真实模型入口，只声明`workflow_dispatch`，同样使用三模板矩阵和`rnd`环境。工作流是否能在界面列出，取决于GitHub已登记的默认分支入口；客服分支尚未合并时使用上面的`native-probe.yml`入口，不为显示新工作流而合并未验收代码。不要用push触发、提交消息标记或周期任务代替明确授权。

### 每个模板先测协议，再测完整交付

每行在自己的隔离job中依次运行：

```bash
uv run python -m scripts.ci_real_model --phase smoke --template python-basic
uv run python -m scripts.ci_real_model --phase full --template python-basic
```

另两行的`--template`分别为`fastapiadmin`和`yudao-vben`，对应`fastapiadmin-vue/PostgreSQL`与`vben-antd/PostgreSQL`；基础行使用`simple-admin/SQLite`。这些命令由受信任的Actions环境执行，不要在本机伪造`GITHUB_*`来绕过保护。原生行还必须准备各自固定pnpm、PostgreSQL、Redis和浏览器，Yudao另需JDK17/Maven，完整步骤以两份工作流为准。

smoke发送明确Hello请求，保留`thinking.type=enabled`、`reasoning_effort=high`与`stream=false`。HTTP200且有效回复只证明协议请求可用。同一job、同一attempt、同一commit的smoke成功之后，才进入完整阶段；脚本拒绝复用别的运行的smoke回执。

full通过真实工作台网页选择当前行的模板/前端/数据库，按顺序输入以下三个文件的全部文本：

- `examples/requirements/customer-service.md`：用户原始需求，保留原文
- `examples/requirements/customer-service-decisions.md`：明确演示默认决策
- `examples/requirements/customer-service-contract.md`：黑盒验收需要的实体、角色、字段与流程命名约定

三个文件不包含预置模型Plan。真实模型必须自己形成并通过`Requirement`、`Plan.business`与审阅校验；`examples/plans/customer-service.json`仅是确定性工具测试样例，不能读它替代模型输出。网页只勾选一次初始智能推荐，后续不追加批准或重试；要求保留客户/请求/任务、角色行范围、分配/状态、备注/审计、提醒和全部四类统计后到达`READY`。

到达`READY`后仍要实际点击下载ZIP、验证哈希、解压至新目录，并使用该产品自己的依赖和全新数据库执行HTTP、浏览器与重启检查。原生模板必须真实生成和构建自己的框架，不用Python页面冒充。每阶段有调用与时间预算，失败保留失败，不改用夹具、缩减功能或换供应商补成功。

### 只上传允许公开的机器证据与合成页面截图

每行的`reports/real-model/summary.json`只保留白名单回执：运行身份、模板、阶段、错误代码、数值HTTP状态、有限token用量、合同有效性和必要字段标记、浏览器/下载/新库/重启结果。该文件位于`real-model-sanitized-${template}-${runid}-${attempt}`产物中。不上传密钥正文、片段或哈希，不上传模型原文、推理、原始服务商错误体、生成源码包或运行数据库。真实密钥不继续传给浏览器、uv或产品子进程。

真实产品页面使用合成客户和验收账号；经过路径、名称、大小及PNG校验的截图位于`reports/real-model/screenshots/*.png`，单独保存为`customer-ui-${template}-${sha}`产物。它们只用于查看该行实际页面，不公开实际客户数据或临时密码。下载后应真正打开列表、表单、关联、处理、提醒和统计画面，结合业务章节的视觉清单检查；有截图文件不等于已完成视觉审阅。

只有某行`acceptance_scope=full_workflow`、整体`passed=true`且模板/commit/attempt吻合，才能将该行标为真实模型完整流程通过；三个模板各自满足才可称三模板通过。`smoke_only`、固定计划测试、之前其他案例或其他提交的成功都不能替代。原来`BLOCKED`的任务恢复、Aider编辑、Continue原生索引和Daytona是另外的验证范围；当前真实模型路径明确记录这些未覆盖项，不借用旧报告填充它们。
