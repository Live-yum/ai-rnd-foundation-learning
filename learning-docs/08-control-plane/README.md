# 08 · API、CLI与操作台

[总目录](../README.md) · [上一阶段](../07-orchestration/README.md) · [下一阶段](../09-native/README.md)

## 一套内核，三种入口

`api.create_app` 把 Store 和 Runtime 接到FastAPI生命周期，启动时迁移并取得平台访问令牌；可选启动一个内置Worker。关闭时通知Worker停下、等待线程退出、释放数据库。`/health` 说明进程能回答，`/ready` 进一步检查数据库与要求中的Worker是否可用，它们不能互相替代。

所有数据接口和下载都依赖本机Bearer令牌；TrustedHost限制可信主机名，防止把本地服务当开放网络API。写操作继续要求 `Idempotency-Key`，不是到了HTTP层就丢掉上一站的重复提交保护。`/catalog` 来自固定模板组合，`/models` 和运行模型回执只显示安全摘要，不展示Key原文。

`cli.py` 是另一位HTTP客户端：只连接回环平台，读取本机令牌，创建项目/运行后轮询等待点。网页 `workbench/web` 做同样的事。两者都必须先确定模板、兼容前端和数据库，再提交需求。按钮“智能推荐”修改的是持续委托状态，不是一次普通模型提示；“恢复人工确认”在后续关卡恢复人工决策。

## 先测API，不要求真实账号

```bash
# .learning/commands/08-api.sh
uv run pytest tests/test_api.py tests/test_guided_selection.py -q
uv run rnd --help
uv run rnd doctor
```

API测试使用 `create_app(..., start_worker=False)` 和临时Store。应验证错误令牌得到401、恶意Host得到400、重复幂等请求返回同一项目、缺幂等键得到422。帮助应列出实际已有命令。`doctor` 在没有配置真实模型时如实显示missing，这是此时允许的诊断结果，不叫模型验证通过。

`rnd init` 在当前实现中还会解压两类原生模板。若你按阶段从空目录写到这里，vendor文件要到第09站准备；现在先不运行 `init`。真实启动所需的 `.env` 可以在原生初始化完成后由 `init` 创建，或在你已经理解配置内容后从 `.env.example` 复制。不要在缺归档时改坏 `init`，也不要把实际Key写进书中练习或Git。

`workbench/native.py` 在这一站先创建，因为 `/templates` 接口需要其中的catalog来列出模板定义与配置状态。这里只读取目录信息，不需要ZIP或PostgreSQL；真正准备上游源码、运行原生生成器和验收仍在第09站。

## 真实操作台的第一次启动

完成第09站的原生归档准备并填写自己的 `BASE_URL`、`API_KEY`、`MODE` 后，才执行下列真实启动命令。它们是后续回到本节的操作，不是本阶段无Key测试的隐藏前提。

```bash
# .learning/commands/08-live-start.sh
uv run rnd init
uv run rnd models
uv run rnd start
```

另一个同目录终端执行 `uv run rnd token`，把输出填入 `http://127.0.0.1:8000/` 的本机页面，不分享给别人。浏览器选择 python-basic/simple-admin/SQLite 后，再输入需求。CLI的等价入口是 `uv run rnd chat --template python-basic --frontend simple-admin --database sqlite`。没有模型配置时 `start` 应拒绝；生产入口不能静默改用测试夹具。

记录你看到的run_id，并练习用 `uv run rnd show 运行UUID` 查看同一任务。等待、失败、预算暂停各有真实含义；页面存在下载按钮也仍需后面的交付证据。平台只监听本机，并没有公网多用户身份体系，不要为了让别人访问而改为 `0.0.0.0`。

## 本阶段源码和后续依赖

本阶段首次创建 10 个源文件，完整位置见[文件落盘顺序](files.md)。已在前站创建的模块不重复覆盖；本章深入使用已有模块时回到[总索引](../source-index.md)查找。只有各步骤写明的检查代表本阶段成果，完整平台和外部服务验收留到最后一站。
