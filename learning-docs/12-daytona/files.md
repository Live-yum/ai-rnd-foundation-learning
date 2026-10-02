# 本机沙箱与镜像：本阶段文件

[返回阶段导读](README.md)

按导读先后理解；同一组需全部写完再导入或运行测试。以下路径相对学生项目根目录，不是教材目录。所有文件逐字节收录，代码分段的第一行路径注释需删除。锁文件与截图编码在 sources/locks 和 sources/assets 下，先读实现模块，需要校对时再打开资源。

- [scripts/ci_daytona_local.py](sources/scripts__ci_daytona_local_py--001.md)：真实本机Daytona中的资讯端到端验收；1 段
- [scripts/ci_daytona_matrix.py](sources/scripts__ci_daytona_matrix_py--001.md)：数据库与模板矩阵的沙箱验收入口；1 段
- [scripts/daytona_bootstrap.py](sources/scripts__daytona_bootstrap_py--001.md)：真实本机身份认证与快照注册；1 段
- [scripts/daytona_build.py](sources/scripts__daytona_build_py--001.md)：从固定来源构建并锁定本机镜像；1 段
- [scripts/daytona_diagnostics.py](sources/scripts__daytona_diagnostics_py--001.md)：保留有界且脱敏的失败诊断；1 段
- [scripts/daytona_gateway.py](sources/scripts__daytona_gateway_py--001.md)：固定端口的本机网络入口；1 段
- [scripts/daytona_local.py](sources/scripts__daytona_local_py--001.md)：安装和管理本机Daytona开发服务；1 段
- [scripts/daytona_matrix_image.py](sources/scripts__daytona_matrix_image_py--001.md)：为每个技术栈制作离线依赖快照；1 段
- [scripts/daytona_matrix_probe.py](sources/scripts__daytona_matrix_probe_py--001.md)：沙箱内独立数据库和产品验收；1 段
- [tests/test_daytona_bootstrap_contract.py](sources/tests__test_daytona_bootstrap_contract_py--001.md)：可重复的验收用例；1 段
- [tests/test_daytona_build.py](sources/tests__test_daytona_build_py--001.md)：可重复的验收用例；1 段
- [tests/test_daytona_download.py](sources/tests__test_daytona_download_py--001.md)：可重复的验收用例；1 段
- [tests/test_daytona_gateway.py](sources/tests__test_daytona_gateway_py--001.md)：可重复的验收用例；1 段
- [tests/test_daytona_matrix.py](sources/tests__test_daytona_matrix_py--001.md)：可重复的验收用例；1 段
- [tests/test_daytona_sessions.py](sources/tests__test_daytona_sessions_py--001.md)：可重复的验收用例；1 段
- [tests/test_daytona_snapshot.py](sources/tests__test_daytona_snapshot_py--001.md)：可重复的验收用例；1 段
- [tests/test_daytona_startup_diagnostics.py](sources/tests__test_daytona_startup_diagnostics_py--001.md)：可重复的验收用例；1 段
- [tests/test_local_only.py](sources/tests__test_local_only_py--001.md)：可重复的验收用例；1 段
- [tools/daytona/Dockerfile](sources/tools__daytona__Dockerfile--001.md)：本机Daytona的预热镜像；1 段
- [tools/daytona/matrix.Dockerfile](sources/tools__daytona__matrix_Dockerfile--001.md)：本机Daytona的预热镜像；1 段
- [tools/daytona/minio.Dockerfile](sources/tools__daytona__minio_Dockerfile--001.md)：本机对象存储服务镜像；1 段
- [tools/daytona/runner-entry.sh](sources/tools__daytona__runner-entry_sh--001.md)：本机Runner启动顺序与退出清理；1 段
- [tools/daytona/runner.Dockerfile](sources/tools__daytona__runner_Dockerfile--001.md)：本机Runner服务镜像；1 段
- [tools/daytona/warm.py](sources/tools__daytona__warm_py--001.md)：本机Daytona的预热镜像；1 段
- [workbench/daytona_diagnostics.py](sources/workbench__daytona_diagnostics_py--001.md)：本次自有沙箱的有界启动诊断；1 段
- [workbench/daytona_sessions.py](sources/workbench__daytona_sessions_py--001.md)：长时间沙箱检查的单次异步提交；1 段
- [workbench/daytona_worker.py](sources/workbench__daytona_worker_py--001.md)：SDK专用的本机网络子进程；1 段
