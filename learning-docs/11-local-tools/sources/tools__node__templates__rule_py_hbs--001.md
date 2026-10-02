# tools/node/templates/rule.py.hbs · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：原生业务规则的真实Plop生成入口与模板。** 固定node-plop执行受信任的add/modify动作，模板定义Python、Java、Vue之间一致的规则入口。请求只提供受校验数据；已有文件、锚点数量和生成集合都要匹配，不能执行用户脚本。

**对应关系：** workbench.scaffolding → no-network → plop-runner → 实际规则文件/表单挂载；native_coding接着验证候选。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `tools/node/templates/rule.py.hbs`；**本文件共有 1 段**。本段覆盖源文件 L1–L8。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`179`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tools/node/templates/rule.py.hbs", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "49f76998db499e9692bcbdf2e5dd29f56bf466d82b3ed2f552fbb2f07eeea556"} -->
````text
# tools/node/templates/rule.py.hbs
"""Pure single-record business predicate. Framework hooks call this function."""

def valid(data):
    return (
        # RND_RULE_BEGIN
        True
        # RND_RULE_END
    )
````
