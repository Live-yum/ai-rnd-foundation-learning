"""Query expressions come only from frozen metadata, always under the caller's ownership."""

from fields import date_string, filter_value
from sqlalchemy import or_


def conditions(table, entity, query, user_id):
    fields = {field["name"]: field for field in entity["fields"]}
    expressions = [table.c.owner_id == user_id]
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
