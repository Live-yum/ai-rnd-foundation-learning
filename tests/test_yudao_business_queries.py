"""Compile and execute the real generated Java query predicates, without Spring mocks."""

import shutil
import subprocess

import pytest

from workbench.settings import ROOT

JAVA_TEST = r"""
    private static int checks;
    private static void check(boolean value) { checks++; if(!value) throw new AssertionError("query case "+checks); }
    private static void invalid(List<Field> fields, Map<String,String> query) {
        boolean refused=false; try { compile(fields,query); } catch(IllegalArgumentException expected) { refused=true; }
        check(refused);
    }
    public static void main(String[] args) {
        List<Field> fields=List.of(
            new Field("name","text",true,false,false),
            new Field("organization","text",true,false,false),
            new Field("category","enum",false,true,false),
            new Field("serviceDate","date",false,true,true),
            new Field("count","integer",false,true,false),
            new Field("enabled","boolean",false,true,false),
            new Field("privateNote","text",false,false,false));
        Map<String,Object> a=new HashMap<>(Map.of("name","MiXeD alpha","organization","first", "category","企业", "serviceDate","2024-02-29", "count",12,"enabled",true,"privateNote","secret"));
        Map<String,Object> b=new HashMap<>(Map.of("name","second","organization","MIXED beta", "category","个人", "serviceDate","2024-03-01", "count",2,"enabled",false,"privateNote","hidden"));
        Map<String,Object> c=new HashMap<>(Map.of("name","unrelated","organization","third", "category","企业集团", "serviceDate","2024-02-28", "count",120,"enabled",true,"privateNote","MIXED"));
        var search=compile(fields,Map.of("q","mixed")); check(search.test(a));check(search.test(b));check(!search.test(c));
        var named=compile(fields,Map.of("name","mIxEd"));check(named.test(a));check(!named.test(b));
        var exact=compile(fields,Map.of("category","企业"));check(exact.test(a));check(!exact.test(c));
        check(!compile(fields,Map.of("category","企")).test(a));
        var and=compile(fields,Map.of("q","mixed","category","企业"));check(and.test(a));check(!and.test(b));check(!and.test(c));
        var mismatch=compile(fields,Map.of("name","alpha","organization","beta"));check(!mismatch.test(a));check(!mismatch.test(b));
        var inclusive=compile(fields,Map.of("serviceDate_from","2024-02-29","serviceDate_to","2024-02-29"));check(inclusive.test(a));check(!inclusive.test(b));check(!inclusive.test(c));
        check(compile(fields,Map.of("serviceDate_from","2024-02-29")).test(b));
        check(compile(fields,Map.of("serviceDate_to","2024-02-29")).test(c));
        check(!compile(fields,Map.of("serviceDate_from","2024-03-02","serviceDate_to","2024-02-01")).test(a));
        check(compile(fields,Map.of("count","12")).test(a));check(!compile(fields,Map.of("count","12")).test(c));
        check(compile(fields,Map.of("enabled","true")).test(a));check(!compile(fields,Map.of("enabled","true")).test(b));
        a.put("name",null); check(!compile(fields,Map.of("name","null")).test(a));
        a.put("serviceDate",null);check(!inclusive.test(a));
        check(compile(fields,Map.of("pageNo","1","pageSize","20","archived","false")).test(a));
        invalid(fields,Map.of("privateNote","secret"));invalid(fields,Map.of("unknown","anything"));
        invalid(fields,Map.of("count","12x"));invalid(fields,Map.of("enabled","1"));
        invalid(fields,Map.of("serviceDate_from","2024-02-30"));invalid(fields,Map.of("serviceDate_to","bad"));
        invalid(fields,Map.of("serviceDate_from","2024-2-9"));invalid(fields,Map.of("name_from","2024-01-01"));
        invalid(List.of(new Field("category","enum",false,true,false)),Map.of("q","企业"));
        var literal=compile(fields,Map.of("q","%_"));check(!literal.test(b));
        var dual=List.of(new Field("name","text",true,true,false));
        check(!compile(dual,Map.of("name","sec")).test(b));check(compile(dual,Map.of("q","sec")).test(b));
        System.out.println("passed="+checks);
    }
"""


def run_java(tmp_path, source):
    java = shutil.which("java")
    if java is None:
        pytest.skip("Java source launcher is covered by native Actions with installed JDK")
    target = tmp_path / "RndBusinessQuery.java"
    target.write_text(source.rsplit("}", 1)[0] + JAVA_TEST + "}\n", encoding="utf-8")
    compilation = subprocess.run(
        [
            java,
            "-m",
            "jdk.compiler/com.sun.tools.javac.Main",
            "-source",
            "17",
            "-target",
            "17",
            "-encoding",
            "UTF-8",
            "-d",
            str(tmp_path),
            str(target),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
        check=False,
    )
    if compilation.returncode:
        return compilation
    return subprocess.run(
        [java, "-cp", str(tmp_path), "cn.iocoder.yudao.module.infra.business.RndBusinessQuery"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=30,
        check=False,
    )


def test_actual_java_predicates_cover_search_exact_combination_date_and_rejection(tmp_path):
    source = (ROOT / "templates/business/yudao/RndBusinessQuery.java").read_text(encoding="utf-8")
    result = run_java(tmp_path, source)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "passed=38"


@pytest.mark.parametrize(
    "before,after",
    [
        (
            "return row -> predicates.stream().allMatch(predicate -> predicate.test(row));",
            "return row -> true;",
        ),
        (
            "Objects.equals(exact(field,row.get(key)),typed)",
            "String.valueOf(row.get(key)).contains(String.valueOf(typed))",
        ),
        ("predicates.stream().allMatch", "predicates.stream().anyMatch"),
    ],
)
def test_real_java_probe_rejects_ignored_filters_substring_exact_and_or_combination(
    tmp_path, before, after
):
    source = (ROOT / "templates/business/yudao/RndBusinessQuery.java").read_text(encoding="utf-8")
    assert before in source
    result = run_java(tmp_path, source.replace(before, after))
    assert result.returncode != 0
    assert "AssertionError: query case" in result.stderr


def test_service_enforces_scope_before_query_and_returns_validation_error():
    source = (ROOT / "templates/business/yudao/RndBusinessService.java").read_text(encoding="utf-8")
    page = source.split("public Object page(", 1)[1].split("public void archive(", 1)[0]
    assert page.index('if(!hasAction(name,"read"))') < page.index("RndBusinessQuery.compile")
    assert page.index('if(!allowed(name,row,"read")') < page.index("predicate.test")
    assert 'new ServiceException(BAD_REQUEST.getCode(),"Invalid business query")' in page
    assert "contains(expected)" not in page


def test_invalid_relation_validation_maps_to_native_client_error_without_catching_acl():
    source = (ROOT / "templates/business/yudao/RndBusinessService.java").read_text(encoding="utf-8")
    validation = source.split("private Object validate(", 1)[1].split("private void apply(", 1)[0]
    assert 'require(target,linked,"read")' in validation
    assert 'new ServiceException(BAD_REQUEST.getCode(),"Invalid business relation")' in validation
    assert "catch(IllegalArgumentException error)" in validation
    assert "catch(AccessDeniedException" not in validation and "catch(Exception" not in validation
    action = source.split("public Object action(", 1)[1].split("public Object related(", 1)[0]
    assert 'new ServiceException(BAD_REQUEST.getCode(),"Invalid business assignee")' in action
    assert action.index("require(name,row,action)") < action.index('if(action.equals("assign"))')
