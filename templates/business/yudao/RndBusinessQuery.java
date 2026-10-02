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
