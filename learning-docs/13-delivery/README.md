# 13 · 独立交付与重启

[总目录](../README.md) · [上一阶段](../12-daytona/README.md) · [下一阶段](../14-acceptance/README.md)

## 最后一次验证要离开原工作台

`verification.package_basic` 并不在得到一个passed后马上返回下载链接。它先重算文件manifest，确认报告绑定当前源码，再写临时ZIP；随后在新临时目录安全解压，检查包中文件是否与通过验证的文件一致，安装独立产品环境，再跑真实迁移、HTTP、重启和浏览器。全部成立后才原子替换成正式 `delivery.zip` 并保存 `delivery.json`。

这条链解决一个常见错觉：原生成目录能运行，可能因为借用了平台venv、环境变量或未打包文件。干净解压要清楚证明产品自身代码与锁文件足够。`install_products=False` 的开发测试能验证很多行为，但其回执会明确说明没有隔离安装；不能把它当成完整独立交付证据。

原生交付由 `portable.py` 冻结必需帮助模块、原生源码、SQL和菜单种子，`templates/deployment` 提供独立启动器。`portable_checks.py` 检查恢复后的数据与行为，`native_delivery.py` 对原生运行、业务、页面风格、来源身份和报告作交付门禁。它们可能因09层的导入闭包而提前写入，但只有这一站完整讨论“去掉原平台后还剩什么”。

## 先跑真实独立环境验收

```bash
# .learning/commands/13-clean-install.sh
uv run python -m scripts.ci_clean_install
uv run pytest tests/test_delivery_clearance.py tests/test_native_delivery_boundaries.py tests/test_native_delivery_diagnostics.py -q
```

第一条需要第06站浏览器准备和正常依赖下载环境，成功应输出 `PASS: genuine product venv + separate clean-room venv; HTTP CRUD/isolation/restart; fixture model only`，并产生 `reports/clean-install.json`。报告中的模型是明确夹具，但两个独立venv、HTTP/浏览器和重启是真执行。第二条检查拒绝边界与诊断，不代替两种原生真实新库运行。

真实任务达到READY后，用 `rnd show` 检查报告再下载。下列 `运行UUID` 要替换为你的实际任务标识：

```bash
# .learning/commands/13-download.sh
uv run rnd show 运行UUID
uv run rnd download 运行UUID
```

把得到的ZIP解压到一个全新目录，进入含 `start.py` 的产品根目录；下面的命令不在平台根目录执行：

```bash
# .learning/commands/13-product-start.sh
uv run --no-project --python 3.14 python start.py
```

基础SQLite产品会安装自己的锁定依赖并迁移启动。基础PostgreSQL产品使用自己的Docker Compose随机凭据与持久卷，或明确的本机 `PRODUCT_DATABASE_URL`。原生产品按自身启动器建立新的独立数据库与服务，并打印实际前端地址；需要专用空库时按启动器契约配置 `NATIVE_DELIVERY_DATABASE_URL`，绝不能用生成器开发库冒充新库验收。

## 数据必须能留住，也必须不被带走

客服产品先在产品目录执行 `uv run python manage.py bootstrap-admin --username manager`，在隐藏终端输入中设置管理员密码。重复执行不能覆盖原管理员，重复启动不能重置业务记录和密码。手工创建一条请求、停止后重新启动，再确认仍可登录且记录存在；内置验收也要记录重启结果。

源码ZIP包含初始化/迁移语句，不包含实际用户数据库、`.env`、模型密钥或运行日志。它不是业务备份。不要用“删除数据库后成功启动”替代恢复性验证；原生 `--skip-build` 只适合同一个产品此前确已构建成功的情况，也不是第一次交付省略构建的快捷方式。即使所有开发验收通过，回执仍明确 `production_ready=false`，不把本机开发产品当作公网生产部署认证。

## 平台自己的wheel也必须带上操作台

上面的业务交付ZIP和这里的平台Python wheel是两种产物。平台的可编辑前端源在 `ui/`，生产静态资产在 `workbench/web/`；`rnd start` 从包内提供它们，而不是去找你的Vite开发服务器。因此先按第08站用lock构建，再做打包和干净安装验证；只有原仓目录能打开页面不能证明wheel完整。

静态资产作为教材的精确快照只是为了独立恢复。最终目录验收会从还原的ui源重新执行npm ci、单元测试、类型检查与生产构建，然后核对整个workbench/web文件集合和逐字节内容。多一个旧chunk、漏一个CSS、或bundle与源不一致都应失败；不能选择忽略压缩文件差异来获得通过。发生差异先核对实际Node版本、锁文件和构建配置，并保留原报告，不能把源代码缺项误报成“平台环境已验证”。

## 本阶段源码和后续依赖

本阶段首次创建 35 个源文件，完整位置见[文件落盘顺序](files.md)。已在前站创建的模块不重复覆盖；本章深入使用已有模块时回到[总索引](../source-index.md)查找。只有各步骤写明的检查代表本阶段成果，完整平台和外部服务验收留到最后一站。
