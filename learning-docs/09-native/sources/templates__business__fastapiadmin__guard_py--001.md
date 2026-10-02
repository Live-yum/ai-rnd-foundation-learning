# templates/business/fastapiadmin/guard.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：原生成CRUD入口的绕过防护。** 业务合同挂载后，原CRUD路径不能成为跳过行范围、受控字段与事件的备用写入口；这里检查当前模块身份并拒绝不允许的调用。

**对应关系：** business_fastapi改造生成控制器 → guard → 合同业务接口。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `block_generated_crud`（L4–L6）：不接收显式业务参数，从已配置对象/模块读取依赖。 源码说明：All methods, including import/export/batch, must use audited policy endpoints.。 控制顺序：L6抛异常，停止当前正常路径。 调用`HTTPException`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `templates/business/fastapiadmin/guard.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L6。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`221`。本段原文以LF换行结束。

<!-- learning-source: {"path": "templates/business/fastapiadmin/guard.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "49fdbe9bfdd52497cfdb9cc98622458ebe901a2d3d770964a5a4824c16ef49dd"} -->
````python
# templates/business/fastapiadmin/guard.py
from fastapi import HTTPException


async def block_generated_crud():
    """All methods, including import/export/batch, must use audited policy endpoints."""
    raise HTTPException(403, "Use the business workflow API")
````
