# 确定性生成与独立验证：本阶段文件

[返回阶段导读](README.md)

按导读先后理解；同一组需全部写完再导入或运行测试。以下路径相对学生项目根目录，不是教材目录。所有文件逐字节收录，代码分段的第一行路径注释需删除。锁文件在 sources/locks，截图及Vue构建快照编码在 sources/assets 下，先读实现模块，需要校对时再打开资源。

- [tests/test_generation_preservation.py](sources/tests__test_generation_preservation_py--001.md)：可重复的验收用例；1 段
- [tests/test_product_browser_gate.py](sources/tests__test_product_browser_gate_py--001.md)：可重复的验收用例；1 段
- [workbench/generator.py](sources/workbench__generator_py--001.md)：确定性生成基础FastAPI产品；1 段
- [workbench/postgres_lab.py](sources/workbench__postgres_lab_py--001.md)：基础产品真实PostgreSQL验收环境；1 段
- [workbench/product_sql.py](sources/workbench__product_sql_py--001.md)：从同一Plan生成可读SQL交付资料；1 段
- [workbench/verification.py](sources/workbench__verification_py--001.md)：基础产品的真实验收和干净解压复验；1 段
