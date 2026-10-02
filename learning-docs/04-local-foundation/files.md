# 文件安全与源码检索：本阶段文件

[返回阶段导读](README.md)

按导读先后理解；同一组需全部写完再导入或运行测试。以下路径相对学生项目根目录，不是教材目录。所有文件逐字节收录，代码分段的第一行路径注释需删除。锁文件与截图编码在 sources/locks 和 sources/assets 下，先读实现模块，需要校对时再打开资源。

- [workbench/context_mcp.py](sources/workbench__context_mcp_py--001.md)：只读本机MCP适配器；1 段
- [workbench/filesystem.py](sources/workbench__filesystem_py--001.md)：限定文件路径、归档成员和写入范围；1 段
- [workbench/knowledge.py](sources/workbench__knowledge_py--001.md)：建立可追溯的源码索引和设计包；1 段
- [workbench/owned_lifecycle.py](sources/workbench__owned_lifecycle_py--001.md)：只控制本次启动的服务并核实退出；1 段
- [workbench/retrieval.py](sources/workbench__retrieval_py--001.md)：本机代码检索及可选本机向量融合；1 段
- [workbench/rules.py](sources/workbench__rules_py--001.md)：解释受限的业务表达式；1 段
- [workbench/symbols.py](sources/workbench__symbols_py--001.md)：从真实语法树提取代码符号；1 段
- [workbench/tools.py](sources/workbench__tools_py--001.md)：有界子进程、清洁环境与失败证据；1 段
