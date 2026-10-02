# templates/business/yudao/RndBusinessQuery.java · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：芋道业务列表的声明式查询谓词。** 将配置允许的查询编译为纯Java谓词：关键词只搜索已声明字段，精确过滤按类型比较，日期上下界包含边界，多个条件取交集。无权行先由服务层排除；未知或未开放条件返回输入错误。真实Java断言和错误实现变异检查验证这些规则。

**对应关系：** RndBusinessService.page先检查角色/行权限 → 本文件匹配 → 原生Vxe列表；business-form.ts只显示批准的查询控件。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**创建路径：** `templates/business/yudao/RndBusinessQuery.java`；**本文件共有 1 段**。本段覆盖源文件 L1–L75。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`4194`。本段原文以LF换行结束。

<!-- learning-source: {"path": "templates/business/yudao/RndBusinessQuery.java", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "ba9d1cd3162035e411bf4d6f4007a16dfa45ab1ea5e1d58f0812d8b96858eb3d"} -->
````java
// templates/business/yudao/RndBusinessQuery.java
package cn.iocoder.yudao.module.infra.business;

import java.time.*;
import java.util.*;
import java.util.function.Predicate;

/** Pure query predicates; authorization and tenant filtering stay in the service. */
public final class RndBusinessQuery {
    private RndBusinessQuery() {}
    public record Field(String name, String kind, boolean searchable, boolean filterable, boolean dateRange) {}

    private static LocalDate date(Object value) {
        String text = String.valueOf(value);
        if (!text.matches("[0-9]{4}-[0-9]{2}-[0-9]{2}")) throw new IllegalArgumentException("Invalid date filter");
        try { return LocalDate.parse(text); }
        catch (DateTimeException error) { throw new IllegalArgumentException("Invalid date filter"); }
    }
    private static Object exact(Field field, Object value) {
        if (value == null) return null;
        String text = String.valueOf(value);
        return switch (field.kind()) {
            case "integer" -> Long.valueOf(text);
            case "boolean" -> {
                if (!text.equals("true") && !text.equals("false")) throw new IllegalArgumentException("Invalid boolean filter");
                yield Boolean.valueOf(text);
            }
            case "date" -> date(value);
            case "datetime" -> {
                try { yield OffsetDateTime.parse(text).toInstant(); }
                catch (DateTimeException error) { throw new IllegalArgumentException("Invalid timestamp filter"); }
            }
            default -> text;
        };
    }
    private static boolean contains(Object value, String expected) {
        return value != null && String.valueOf(value).toLowerCase(Locale.ROOT).contains(expected);
    }
    public static Predicate<Map<String,Object>> compile(List<Field> fields, Map<String,String> query) {
        Map<String,Field> byName = new HashMap<>();
        for (Field field : fields) if (byName.put(field.name(),field) != null) throw new IllegalArgumentException("Duplicate query field");
        List<Predicate<Map<String,Object>>> predicates = new ArrayList<>();
        for (var entry : query.entrySet()) {
            String key = entry.getKey(), expected = entry.getValue();
            if (Set.of("pageNo","pageSize","archived").contains(key)) continue;
            if (expected == null || expected.isEmpty()) continue;
            if (key.equals("q")) {
                List<Field> searched = fields.stream().filter(Field::searchable).toList();
                if (searched.isEmpty()) throw new IllegalArgumentException("Search is not available");
                String needle = expected.toLowerCase(Locale.ROOT);
                predicates.add(row -> searched.stream().anyMatch(field -> contains(row.get(field.name()),needle)));
                continue;
            }
            boolean from = key.endsWith("_from"), to = key.endsWith("_to");
            if (from || to) {
                String name = key.substring(0,key.length()-(from?5:3));
                Field field = byName.get(name);
                if (field == null || !field.dateRange() || !field.kind().equals("date")) throw new IllegalArgumentException("Unknown range filter");
                LocalDate bound = date(expected);
                predicates.add(row -> row.get(name) != null && (from ? !date(row.get(name)).isBefore(bound) : !date(row.get(name)).isAfter(bound)));
                continue;
            }
            Field field = byName.get(key);
            if (field == null) throw new IllegalArgumentException("Unknown query field");
            if (field.filterable()) {
                Object typed = exact(field,expected);
                predicates.add(row -> Objects.equals(exact(field,row.get(key)),typed));
            } else if (field.searchable()) {
                // Generated Vben forms use named search inputs in addition to global q.
                String needle = expected.toLowerCase(Locale.ROOT);
                predicates.add(row -> contains(row.get(key),needle));
            } else throw new IllegalArgumentException("Filtering is not available for field");
        }
        return row -> predicates.stream().allMatch(predicate -> predicate.test(row));
    }
}
````
