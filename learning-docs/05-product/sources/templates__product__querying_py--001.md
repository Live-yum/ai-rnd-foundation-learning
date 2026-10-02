# templates/product/querying.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：独立基础产品的组成文件。** 把搜索词、精确筛选、日期上下界转成受字段白名单约束的SQLAlchemy条件；类型和范围先验证，再通过参数绑定查询，不拼接用户SQL。

**对应关系：** generator复制 → 产品start.py/app.py；verification在独立环境复验。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `conditions`（L7–L44）：接收`table`、`entity`、`query`、`user_id`、`scoped`。 控制顺序：L11遍历`fields.items()`；L12按`field.get("filterable")`分支；L14按`field.get("date_range")`分支；L16按`set(query) - allowed`分支；L17抛异常，停止当前正常路径；L19按`len(q) > 200`分支；L20抛异常，停止当前正常路径；L21按`q`分支。后续分支沿下方源码相同行号继续阅读。 调用`fields.items`、`field.get`、`allowed.add`、`allowed.update`、`set`、`ValueError`、`query.get("q", "").strip`、`query.get`、`len`等。 返回路径：L44的`expressions, column.desc() if direction == "desc" else column.asc()`。

</details>

**创建路径：** `templates/product/querying.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L44。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`2004`。本段原文以LF换行结束。

<!-- learning-source: {"path": "templates/product/querying.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "e29a85aa48cfc92951bf5647d349c50d190480f824d57ed2ac1931ea65dc74da"} -->
````python
# templates/product/querying.py
"""Query expressions come only from frozen metadata, always under the caller's ownership."""

from fields import date_string, filter_value
from sqlalchemy import or_


def conditions(table, entity, query, user_id, scoped=True):
    fields = {field["name"]: field for field in entity["fields"]}
    expressions = [table.c.owner_id == user_id] if scoped else []
    allowed = {"q", "limit", "offset", "sort", "direction"}
    for name, field in fields.items():
        if field.get("filterable"):
            allowed.add("filter_" + name)
        if field.get("date_range"):
            allowed.update({"from_" + name, "to_" + name})
    if set(query) - allowed:
        raise ValueError("查询参数不在已批准的搜索/筛选配置中")
    q = query.get("q", "").strip()
    if len(q) > 200:
        raise ValueError("搜索词过长")
    if q:
        searchable = [name for name, field in fields.items() if field.get("searchable")]
        if not searchable:
            raise ValueError("该实体没有配置关键词搜索")
        expressions.append(
            or_(*(table.c[name].icontains(q, autoescape=True) for name in searchable))
        )
    for name, field in fields.items():
        key = "filter_" + name
        if key in query:
            expressions.append(table.c[name] == filter_value(field, query[key]))
        start, end = query.get("from_" + name), query.get("to_" + name)
        if start:
            expressions.append(table.c[name] >= date_string(start))
        if end:
            expressions.append(table.c[name] <= date_string(end))
        if start and end and start > end:
            raise ValueError("起始日期不得晚于结束日期")
    sort = query.get("sort", "id")
    direction = query.get("direction", "asc")
    if sort not in {"id", *fields} or direction not in {"asc", "desc"}:
        raise ValueError("排序字段或方向无效")
    column = table.c[sort]
    return expressions, column.desc() if direction == "desc" else column.asc()
````
