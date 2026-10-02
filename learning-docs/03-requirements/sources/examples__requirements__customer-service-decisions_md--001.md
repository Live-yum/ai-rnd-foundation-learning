# examples/requirements/customer-service-decisions.md · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：客服演示的明确默认决策。** 将站内提醒、合成验收数据、角色范围、统计口径和三套原生风格明确写入需求；它是可见输入，不是失败后暗中降低要求的补丁。

**对应关系：** customer-service.md之后输入 → 需求事实与设计 → 三模板独立验收。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `examples/requirements/customer-service-decisions.md`；**本文件共有 1 段**。本段覆盖源文件 L1–L9。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`1020`。本段原文以LF换行结束。

<!-- learning-source: {"path": "examples/requirements/customer-service-decisions.md", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "7a4fdbc422d66250e3a81809a9d9914d4179c02cf57cc0d5ccb5f9e5ef91c25b"} -->
````markdown
<!-- examples/requirements/customer-service-decisions.md -->
# 客户服务演示的明确默认决策

以下是为了可执行演示而明确记录的默认决策，不替代或删减上面的原始需求：
- 提醒仅使用持久化站内消息，不连接邮件、短信或真实客户联系方式。
- 验收只创建合成账号与客户数据。
- 管理人员管理团队业务、分配与统计；服务人员处理被授权的负责范围；普通员工提交并查看自己创建的请求。具体动作和行权限由审批后的可执行设计明确记录。
- 处理效率包含创建到解决的耗时；统计还包括数量、客户分组和时间趋势，均按当前角色的数据范围计算。
- 三类界面分别保留 Python 轻量管理页、FastapiAdmin 原生 Vue/Fa/Element Plus、Yudao 原生 Java/Vben5 Ant Design 风格；api-only 选择没有界面，不冒充界面验收。
- 必须在真正独立的交付数据库、锁定依赖、浏览器与重启测试中验证完整流程，不把独立 CRUD 或新闻案例成功当作本案例完成。
````
