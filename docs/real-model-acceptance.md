## 显式授权的真实模型端到端验收

常规Actions用明确的模型响应夹具验证编排，同时真实运行数据库、浏览器和本机工具。真实服务商测试是另外一项有调用成本的可选验收，不随普通PR自动调用。它必须在可信的指定分支、获准的GitHub Environment中运行；测试脚本再次核对仓库、分支、事件与目标，不允许切换服务商或模型来绕过失败。

### 环境配置如何进入模型网关

本次专用验收使用GitHub Environment `rnd`。环境Secret的名称为`APK_KEY`，在模型测试步骤中映射成平台读取的`API_KEY`；这是两个明确不同的变量名，不应为了拼写一致复制或打印密钥。环境Variables提供`BASE_URL`和`MODE`：本次目标分别是`https://api.deepseek.com`和`deepseek-flash`。工作流的关键接线如下，表达式由GitHub解释，不能把它替换成密钥正文提交：

```yaml
environment: rnd
# 仅实际调用模型的步骤声明以下env；安装依赖的步骤不注入密钥
env:
  API_KEY: ${{ secrets.APK_KEY }}
  BASE_URL: ${{ vars.BASE_URL }}
  MODE: ${{ vars.MODE }}
```

`environment`属于job，`env`属于该job中的模型调用step，上面是层级关系示意，完整可执行工作流以附录文件为准。环境保护规则若要求批准，必须由有权限的人批准；不要改成其他环境、绕过审批或把环境Secret复制到源码。直接绑定该Environment的job才能取得其配置；不能把未绑定环境的普通测试误认为已经拿到了密钥。

### 先测协议，再测完整交付

最终工作流为`.github/workflows/real-model.yml`，只声明`workflow_dispatch`，不包含push触发、提交消息标记或周期调度。它是直接绑定`rnd`的独立job，不通过未绑定环境的可复用调用间接猜测配置。在GitHub Actions选择该工作流的手动运行入口，确认受信任分支及待测提交后执行。测试先运行`uv run python -m scripts.ci_real_model --phase smoke`，向已授权目标发送明确的Hello请求，保留`thinking.type=enabled`、`reasoning_effort=high`和`stream=false`。HTTP200且有效回复只说明该请求可用，不说明平台已完成交付。

默认分支已经有旧工作流入口而新独立入口尚未合并时，也可以使用`.github/workflows/native-probe.yml`的手动兼容入口：只有明确设置`real_model=true`，并把`expected_sha`填写为已审查的完整40位提交SHA，才会进入直接绑定`rnd`的付费模型job。该job在模型访问前检查输入SHA与本次`GITHUB_SHA`完全相等；不匹配就停止。`real_model`默认false，普通PR及默认模板完整性检查不调用付费模型。独立`real-model.yml`在合并后是清晰的常规手动入口；不要通过push触发、提交消息标记或周期任务维持付费测试。需要验证全套CI与真实模型属于同一批代码时，分别核对两类报告的完整提交身份。

同一job、同一attempt和同一commit的smoke成功后，才安装固定浏览器并执行`--phase full`；脚本拒绝复用其他运行的smoke回执。full通过真实网页选择Python基础模板、simple-admin和SQLite，输入明确的资讯字段约束，并且只勾选一次初始智能推荐。之后不点击追加批准或重试，要求实际模型驱动流程到`READY`。随后从页面下载ZIP，核对哈希与原字段要求，解压到独立目录和新依赖环境/数据库，再执行产品的HTTP、真实浏览器与重启验证。各阶段使用明确调用与时间预算，失败保留失败，不改用夹具响应或其他模型补成功。

### 本次真实案例的范围

实际输入是明确补齐字段约束的资讯管理案例：唯一实体`news`；`title`必填、1至250字符且可搜索；`body`必填、1至3000字符且可搜索；`published_on`为必填真实日期，支持单日与含两端日期范围；`category`为可选枚举，三个选项为资讯、攻略、大神，可精确筛选。要求关键词/分类/日期组合、清除条件、逐用户隔离及CRUD，明确不要求采集、匿名公众访问或支付。

因此该真实验收证明的是这份明确合同下的一次智能推荐完整交付，不等于仅输入一句含糊的游戏名称也必然得到同一结果。原先已处于BLOCKED的任务如何保留事实并恢复，仍由专门的恢复夹具与流程测试覆盖；不能把本次新建任务的成功算作旧任务已经恢复。结构化事实里的false（例如可选字段的required=false）是明确的布尔约束，不能按字符串存在就解释为true。

### 只读允许公开的机器证据

产物只上传`reports/real-model/summary.json`中的白名单回执：运行身份、成功/失败阶段和错误代码、数值HTTP状态、有限token用量、结构化合同有效性及必要的字段标记、浏览器/下载/新库/重启结果。不会上传密钥正文、片段或哈希，不上传模型原文、推理文本、原始服务商错误体、生成源码包或运行数据库。环境变量读取后，真实密钥不继续传给浏览器、uv和产品子进程。

只有`acceptance_scope=full_workflow`并且整体`passed=true`，才能把这次真实模型完整流程标为通过；`smoke_only`不能替代它。该路径明确不测试Aider编辑、Continue原生索引、Daytona或旧阻塞任务的真实模型恢复；这些能力仍以各自独立验收为准。每次查看报告都核对commit与attempt，不把先前一次Hello成功或旧提交的报告当作当前完整验收。
