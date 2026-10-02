# tests/test_yudao_business_queries.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.settings`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `run_java`（L57–L93）：接收`tmp_path`、`source`。 控制顺序：L59按`java is None`分支；L84按`compilation.returncode`分支。 调用`shutil.which`、`pytest.skip`、`target.write_text`、`source.rsplit`、`subprocess.run`、`str`。 返回路径：L85的`compilation`；L86的`subprocess.run( [java, "-cp", str(tmp_path), "cn.iocoder.yudao.module.infra.business.RndBu…`。
- `test_actual_java_predicates_cover_search_exact_combination_date_and_rejection`（L96–L100）：接收`tmp_path`。 控制顺序：L99断言`result.returncode == 0`；L100断言`result.stdout.strip() == "passed=38"`。 调用`(ROOT / "templates/business/yudao/RndBusinessQuery.java").read_te…`、`run_java`、`result.stdout.strip`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_real_java_probe_rejects_ignored_filters_substring_exact_and_or_combination`（L117–L124）：接收`tmp_path`、`before`、`after`。 控制顺序：L121断言`before in source`；L123断言`result.returncode != 0`；L124断言`"AssertionError: query case" in result.stderr`。 调用`(ROOT / "templates/business/yudao/RndBusinessQuery.java").read_te…`、`run_java`、`source.replace`、`pytest.mark.parametrize`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_service_enforces_scope_before_query_and_returns_validation_error`（L127–L133）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L130断言`page.index('if(!hasAction(name,"read"))') < page.index("RndBusinessQuery.compile")`；L131断言`page.index('if(!allowed(name,row,"read")') < page.index("predicate.test")`；L132断言`'new ServiceException(BAD_REQUEST.getCode(),"Invalid business query")' in page`；L133断言`"contains(expected)" not in page`。 调用`(ROOT / "templates/business/yudao/RndBusinessService.java").read_…`、`source.split("public Object page(", 1)[1].split`、`source.split`、`page.index`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_invalid_relation_validation_maps_to_native_client_error_without_catching_acl`（L136–L145）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L139断言`'require(target,linked,"read")' in validation`；L140断言`'new ServiceException(BAD_REQUEST.getCode(),"Invalid business relation")' in validati…`；L141断言`"catch(IllegalArgumentException error)" in validation`；L142断言`"catch(AccessDeniedException" not in validation and "catch(Exception" not in validati…`；L144断言`'new ServiceException(BAD_REQUEST.getCode(),"Invalid business assignee")' in action`；L145断言`action.index("require(name,row,action)") < action.index('if(action.equals("assign"))'…`。 调用`(ROOT / "templates/business/yudao/RndBusinessService.java").read_…`、`source.split("private Object validate(", 1)[1].split`、`source.split`、`source.split("public Object action(", 1)[1].split`、`action.index`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_yudao_business_queries.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L145。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`7808`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_yudao_business_queries.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "306b8a2ee1f703791e31d4a5702f21a7ef18384f1be6055057c581d5aaba90b1"} -->
````python
# tests/test_yudao_business_queries.py
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
````
