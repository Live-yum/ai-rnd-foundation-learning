# tests/test_yudao_installed_navigation.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：可重复的验收用例。** pytest查找test_函数并注入参数同名的fixture（例如tmp_path或monkeypatch）；assert不成立就失败。测试中构造的模型响应/SDK对象只是显式夹具，真实服务测试在ci_脚本单独运行并标明范围。

**对应关系：** 阅读下表用例名、断言和被调函数 → 运行本文件 → 对应实现；conftest定义共享隔离环境。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.filesystem`、`workbench.settings`、`workbench.yudao_navigation`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `native_sources`（L27–L45）：接收`tmp_path`。 控制顺序：L30遍历`archive.namelist()`；L31按`name.endswith("pom.xml") or name in { JAVA_ROOT + "/MenuServiceImpl.java", JAVA_ROOT …`分支；L40遍历`archive.namelist()`；L41按`name.startswith("apps/web-antd/src/") and name.endswith((".vue", ".ts"))`分支。 调用`ZipFile`、`archive.namelist`、`name.endswith`、`path.parent.mkdir`、`path.write_bytes`、`archive.read`、`name.startswith`。 返回路径：L45的`backend, frontend`。
- `seed_rows`（L48–L60）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L52遍历`source.splitlines()`；L53按`line.startswith("INSERT INTO system_menu (")`分支；L56按`row[18] == "0"`分支。 调用`ZipFile`、`archive.read("sql/postgresql/ruoyi-vue-pro.sql").decode`、`archive.read`、`source.splitlines`、`line.startswith`、`line.split`、`next`、`csv.reader`、`io.StringIO`等。 返回路径：L60的`rows`。
- `source_capabilities`（L63–L78）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L66遍历`archive.namelist()`；L67按`"/controller/admin/" not in name or not name.endswith("Controller.java")`分支；L71按`not root`分支；L75遍历`re.findall(r'@(?:Get\|Post\|Put\|Delete\|Patch)Mapping\("([^\"]+)…`。 调用`set`、`ZipFile`、`archive.namelist`、`name.endswith`、`archive.read(name).decode`、`archive.read`、`re.search`、`root[1].lstrip`、`roots.add`等。 返回路径：L78的`roots, routes, permissions`。
- `run_java`（L133–L178）：接收`tmp_path`、`source`、`harness`。 控制顺序：L135按`not java`分支；L138遍历`( ("MenuDO.java", MENU), ("RndInstalledMenuFilter.java", source),…`；L166断言`result.returncode == 0`。 调用`shutil.which`、`pytest.skip`、`path.parent.mkdir`、`path.write_text`、`paths.append`、`str`、`subprocess.run`。 返回路径：L167的`subprocess.run( [ java, "-cp", str(tmp_path), "cn.iocoder.yudao.module.system.service.perm…`。
- `test_real_java_filter_native_seed_admin_ordinary_role_and_direct_api_consistency`（L181–L222）：接收`native_sources`、`tmp_path`。 控制顺序：L186断言`pages["infra/swagger/index"]["local_endpoint"] == "/doc.html"`；L187断言`pages["infra/webSocket/index"]["local_endpoint"] == "/infra/ws"`；L188断言`pages["system/dict/index"]["local_only"] is False`；L189断言`"views/system/dict/modules/type-grid.vue" in pages["system/dict/index"]["dependency_f…`；L192遍历`("wbcustomer", "wbrequest", "wbtask")`；L214遍历`("customer", "request", "task")`；L218遍历`(("roots", roots), ("routes", routes), ("permissions", permission…`；L221断言`result.returncode == 0`。后续分支沿下方源码相同行号继续阅读。 调用`frontend_capabilities`、`installed_modules`、`seed_rows`、`(tmp_path / "menus.tsv").write_text`、`"\n".join`、`"\t".join`、`source_capabilities`、`routes.update`、`roots.add`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_overlay_is_idempotent_refreshes_generated_pages_and_preserves_seed_archives`（L225–L276）：接收`native_sources`、`tmp_path`。 控制顺序：L237断言`first["modules"] == ["infra", "system"]`；L238断言`first["after_sha256"] == second["after_sha256"]`；L239断言`first["database_mutated"] is False and first["role_grants_expanded"] is False`；L244断言`"infra/wbcustomer/index" not in first["components"]`；L245断言`"infra/wbcustomer/index" in third["components"]`；L246断言`first["after_sha256"]["RndInstalledMenuFilter.java"] != third["after_sha256"]["RndIns…`；L250断言`before == {str(path): sha(path) for path in inputs}`；L253断言`menu.count("rndInstalledMenus(") == 6`。后续分支沿下方源码相同行号继续阅读。 调用`str`、`sha`、`prepare_yudao_navigation`、`path.parent.mkdir`、`path.write_text`、`(backend / JAVA_ROOT / "MenuServiceImpl.java").read_text`、`(backend / JAVA_ROOT / "PermissionServiceImpl.java").read_text`、`menu.count`、`role.count`等。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_original_changed_overlay_context_fails_before_writing`（L279–L293）：接收`native_sources`、`tmp_path`。 控制顺序：L292断言`sha(menu) == before`；L293断言`not (backend / JAVA_ROOT / "RndInstalledMenuFilter.java").exists()`。 调用`path.write_text`、`path.read_text(encoding="utf-8").replace`、`path.read_text`、`sha`、`pytest.raises`、`prepare_yudao_navigation`、`(backend / JAVA_ROOT / "RndInstalledMenuFilter.java").exists`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_api_only_baseline_is_explicit_and_cannot_invent_frontend_capabilities`（L296–L308）：接收`native_sources`、`tmp_path`。 控制顺序：L304断言`receipt["mode"] == "api-only-baseline"`；L305断言`receipt["components"] == {}`；L307断言`"API_ONLY = true" in source`；L308断言`"normalized(root).equals(normalized(component))" in source`。 调用`shutil.rmtree`、`pytest.raises`、`prepare_yudao_navigation`、`(backend / JAVA_ROOT / "RndInstalledMenuFilter.java").read_text`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_portable_and_runtime_rebuild_use_same_current_registry_overlay`（L311–L322）：不接收显式业务参数，从已配置对象/模块读取依赖。 控制顺序：L314断言`"yudao_navigation.py" in HELPERS`；L315断言`"mappings.getHandlerMethods()" in POLICY`；L316断言`"findMergedAnnotation(handler.getMethod(), PreAuthorize.class)" in POLICY`；L317断言`"menuMapper" not in POLICY`；L319断言`runtime.index("copy_source(args.frontend_source, frontend)") < runtime.index( "instal…`；L322断言`"navigation_api_only=not args.frontend" in runtime`。 调用`(ROOT / "scripts/ci_native_runtime.py").read_text`、`runtime.index`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_actual_compiled_module_manifest_ignores_commented_business_dependencies`（L325–L331）：接收`native_sources`。 控制顺序：L327断言`installed_modules(backend) == ["infra", "system"]`；L329遍历`manifest["sources"]`；L330按`item["template"] == "yudao-vben"`分支；L331断言`sha(ROOT / "templates/vendor" / item["archive"]) == item["archive_sha256"]`。 调用`installed_modules`、`json.loads`、`(ROOT / "templates/vendor/manifest.json").read_text`、`sha`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `test_live_registered_handler_policy_ignores_unregistered_classes_and_refreshes_without_cache`（L334–L472）：接收`tmp_path`。 控制顺序：L340按`not java`分支；L435遍历`sources.items()`；L459断言`result.returncode == 0`；L471断言`result.returncode == 0`；L472断言`"live registered navigation PASS" in result.stdout`。 调用`shutil.which`、`pytest.skip`、`render_filter`、`sources.items`、`path.parent.mkdir`、`path.write_text`、`paths.append`、`str`、`subprocess.run`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `tests/test_yudao_installed_navigation.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L472。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`26301`。本段原文以LF换行结束。

<!-- learning-source: {"path": "tests/test_yudao_installed_navigation.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "ca3835e6921c43561903c5cfb1e81b7fa9406e6155fe819f1a59d3de6eca3251"} -->
````python
# tests/test_yudao_installed_navigation.py
"""Execute the real generated menu intersection against the unchanged pinned seed."""

import csv
import io
import json
import re
import shutil
import subprocess
from zipfile import ZipFile

import pytest

from workbench.filesystem import sha
from workbench.settings import ROOT
from workbench.yudao_navigation import (
    JAVA_ROOT,
    MARKER,
    POLICY,
    frontend_capabilities,
    installed_modules,
    prepare_yudao_navigation,
    render_filter,
)


@pytest.fixture
def native_sources(tmp_path):
    backend, frontend = tmp_path / "backend", tmp_path / "frontend-product"
    with ZipFile(ROOT / "templates/vendor/yudao-backend.zip") as archive:
        for name in archive.namelist():
            if name.endswith("pom.xml") or name in {
                JAVA_ROOT + "/MenuServiceImpl.java",
                JAVA_ROOT + "/PermissionServiceImpl.java",
                "sql/postgresql/ruoyi-vue-pro.sql",
            }:
                path = backend / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(archive.read(name))
    with ZipFile(ROOT / "templates/vendor/yudao-frontend.zip") as archive:
        for name in archive.namelist():
            if name.startswith("apps/web-antd/src/") and name.endswith((".vue", ".ts")):
                path = frontend / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(archive.read(name))
    return backend, frontend


def seed_rows():
    with ZipFile(ROOT / "templates/vendor/yudao-backend.zip") as archive:
        source = archive.read("sql/postgresql/ruoyi-vue-pro.sql").decode()
    rows = []
    for line in source.splitlines():
        if line.startswith("INSERT INTO system_menu ("):
            values = line.split("VALUES (", 1)[1][:-2]
            row = next(csv.reader(io.StringIO(values), quotechar="'", skipinitialspace=True))
            if row[18] == "0":
                rows.append(
                    [row[index] if row[index] != "NULL" else "" for index in (0, 5, 3, 6, 8, 2)]
                )
    return rows


def source_capabilities():
    roots, routes, permissions = set(), set(), set()
    with ZipFile(ROOT / "templates/vendor/yudao-backend.zip") as archive:
        for name in archive.namelist():
            if "/controller/admin/" not in name or not name.endswith("Controller.java"):
                continue
            source = archive.read(name).decode()
            root = re.search(r'@RequestMapping\("([^\"]+)"\)', source)
            if not root:
                continue
            root = "/" + root[1].lstrip("/")
            roots.add(root)
            for route in re.findall(r'@(?:Get|Post|Put|Delete|Patch)Mapping\("([^\"]+)"\)', source):
                routes.add(root + route)
            permissions.update(re.findall(r"hasPermission\('([^']+)'\)", source))
    return roots, routes, permissions


MENU = """package cn.iocoder.yudao.module.system.dal.dataobject.permission;
public record MenuDO(Long id, Long parentId, Integer type, String path, String component, String permission) {
 public Long getId(){return id;} public Long getParentId(){return parentId;}
 public Integer getType(){return type;} public String getPath(){return path;}
 public String getComponent(){return component;} public String getPermission(){return permission;}
}
"""

HARNESS = r"""package cn.iocoder.yudao.module.system.service.permission;
import cn.iocoder.yudao.module.system.dal.dataobject.permission.MenuDO;
import java.util.*;
import java.nio.file.*;
public class NavigationTest {
 static void check(boolean value, String name) { if (!value) throw new AssertionError(name); }
 static Set<Long> ids(List<MenuDO> rows) { Set<Long> ids=new HashSet<>();for(var row:rows)ids.add(row.getId());return ids; }
 static Set<String> lines(String root,String name)throws Exception{return new HashSet<>(Files.readAllLines(Path.of(root,name)));}
 public static void main(String[] args)throws Exception {
  List<MenuDO> all=new ArrayList<>();
  for(String line:Files.readAllLines(Path.of(args[0],"menus.tsv"))){String[] r=line.split("\t",-1);all.add(new MenuDO(Long.valueOf(r[0]),Long.valueOf(r[1]),Integer.valueOf(r[2]),r[3],r[4],r[5]));}
  var roots=lines(args[0],"roots.txt");var routes=lines(args[0],"routes.txt");var permissions=lines(args[0],"permissions.txt");var domains=Set.of("system","infra");
  var admin=RndInstalledMenuFilter.filter(all,all,routes,roots,permissions,domains);
  Set<String> top=new HashSet<>();for(var row:admin)if(row.getParentId()==0L)top.add(row.getPath());
  check(top.equals(Set.of("/system","/infra","/workbench")),"only actual installed roots: "+top);
  var adminIds=ids(admin);
  for(long id:List.of(1L,2L,4L,5L,6L,7L,8L,9L,18L,19L,20L,17L,565L,90001L,90002L,90003L,90004L,90005L))check(adminIds.contains(id),"installed positive "+id);
  for(long id:List.of(14L,15L,16L,85L,114L,148L,194L,207L,272L,347L,348L,373L,449L,480L,597L,791L,860L,959L,1348L,1418L,1476L,1637L,1894L,8000L,8200L,90006L,91001L,91002L,92001L,92002L,93001L))check(!adminIds.contains(id),"uninstalled/empty/orphan/cycle negative "+id);
  // A user's existing grant set remains a strict subset, including direct menu-ID reads.
  var grants=Set.of(90001L,90002L,90003L,480L,90006L);
  var candidates=all.stream().filter(row->grants.contains(row.getId())).toList();
  var ordinary=RndInstalledMenuFilter.filter(candidates,all,routes,roots,permissions,domains);
  check(ids(ordinary).equals(Set.of(90001L,90002L,90003L)),"ordinary ACL intersection");
  check(RndInstalledMenuFilter.filter(List.of(),all,routes,roots,permissions,domains).isEmpty(),"empty role");
  for(var row:all)check(!RndInstalledMenuFilter.filter(List.of(row),all,routes,roots,permissions,domains).isEmpty()==adminIds.contains(row.getId()),"direct get/list consistency "+row.getId());
  check(ids(RndInstalledMenuFilter.filter(List.of(all.get(all.size()-1)),all,routes,roots,permissions,domains)).isEmpty(),"unsupported individual GET");
  // Conditional controller disappearance wins even if source, component and SQL still exist.
  roots.remove("/system/user");routes.removeIf(route->route.startsWith("/system/user/"));permissions.removeIf(p->p.startsWith("system:user:"));
  check(!ids(RndInstalledMenuFilter.filter(all,all,routes,roots,permissions,domains)).contains(4L),"disabled runtime controller");
  roots.removeIf(root->root.startsWith("/system/dict"));routes.removeIf(route->route.startsWith("/system/dict"));permissions.removeIf(p->p.startsWith("system:dict:"));
  check(!ids(RndInstalledMenuFilter.filter(all,all,routes,roots,permissions,domains)).contains(9L),"composite dictionary dependency unavailable");
  check(all.size()==Files.readAllLines(Path.of(args[0],"menus.tsv")).size(),"no menu mutation");
  var oldGrants=Set.of(1L,2L,480L,9999L);var visibleGrants=Set.of(1L,2L,3L);
  check(RndInstalledMenuFilter.mergeVisibleGrants(oldGrants,Set.of(1L,2L),visibleGrants).equals(oldGrants),"no-op role save preserves hidden grants");
  check(RndInstalledMenuFilter.mergeVisibleGrants(oldGrants,Set.of(1L,3L,7777L),visibleGrants).equals(Set.of(1L,3L,480L,9999L)),"only requested visible add/remove; no hidden expansion");
  check(RndInstalledMenuFilter.mergeVisibleGrants(oldGrants,Set.of(),visibleGrants).equals(Set.of(480L,9999L)),"remove visible grants preserves hidden");
  check(oldGrants.equals(Set.of(1L,2L,480L,9999L)),"input grants remain unchanged");
  check(RndInstalledMenuFilter.mergeVisibleGrants(oldGrants,Set.of(1L,2L,480L),Set.of(1L,2L,3L,480L)).equals(oldGrants),"re-enabled module preserves prior grants");
  System.out.println("installed navigation PASS; native seed rows="+all.size()+"; visible="+admin.size());
 }
}
"""


def run_java(tmp_path, source, harness=HARNESS):
    java = shutil.which("java")
    if not java:
        pytest.skip("Java runtime absent; native Actions execute the real JDK contract")
    paths = []
    for name, body in (
        ("MenuDO.java", MENU),
        ("RndInstalledMenuFilter.java", source),
        ("NavigationTest.java", harness),
    ):
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
        paths.append(str(path))
    result = subprocess.run(
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
            *paths,
        ],
        capture_output=True,
        text=True,
        timeout=45,
    )
    assert result.returncode == 0, result.stderr
    return subprocess.run(
        [
            java,
            "-cp",
            str(tmp_path),
            "cn.iocoder.yudao.module.system.service.permission.NavigationTest",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )


def test_real_java_filter_native_seed_admin_ordinary_role_and_direct_api_consistency(
    native_sources, tmp_path
):
    backend, frontend = native_sources
    pages = frontend_capabilities(frontend, installed_modules(backend))
    assert pages["infra/swagger/index"]["local_endpoint"] == "/doc.html"
    assert pages["infra/webSocket/index"]["local_endpoint"] == "/infra/ws"
    assert pages["system/dict/index"]["local_only"] is False
    assert (
        "views/system/dict/modules/type-grid.vue" in pages["system/dict/index"]["dependency_files"]
    )
    for name in ("wbcustomer", "wbrequest", "wbtask"):
        pages["infra/" + name + "/index"] = {
            "api_groups": [],
            "local_only": False,
            "embedded_service": False,
        }
    rows = seed_rows() + [
        ["90001", "0", "1", "/workbench", "", ""],
        ["90002", "90001", "2", "wb-customer", "infra/wbcustomer/index", ""],
        ["90003", "90002", "3", "", "", "infra:wb-customer:query"],
        ["90004", "90001", "2", "wb-request", "infra/wbrequest/index", ""],
        ["90005", "90001", "2", "wb-task", "infra/wbtask/index", ""],
        ["90006", "90002", "3", "", "", "infra:wb-customer:export"],
        ["91001", "0", "1", "/system", "", ""],
        ["91002", "91001", "2", "missing", "system/not-installed/index", ""],
        ["92001", "92002", "1", "cycle", "", ""],
        ["92002", "92001", "2", "user", "system/user/index", ""],
        ["93001", "99999", "2", "user", "system/user/index", ""],
    ]
    (tmp_path / "menus.tsv").write_text("\n".join("\t".join(row) for row in rows), encoding="utf-8")
    roots, routes, permissions = source_capabilities()
    routes.update({"/doc.html", "/infra/ws"})
    for entity in ("customer", "request", "task"):
        roots.add("/infra/wb-" + entity)
        routes.add("/infra/wb-" + entity + "/page")
        permissions.add("infra:wb-" + entity + ":query")
    for name, items in (("roots", roots), ("routes", routes), ("permissions", permissions)):
        (tmp_path / (name + ".txt")).write_text("\n".join(sorted(items)), encoding="utf-8")
    result = run_java(tmp_path, render_filter(["system", "infra"], pages))
    assert result.returncode == 0, result.stderr
    assert "installed navigation PASS" in result.stdout


def test_overlay_is_idempotent_refreshes_generated_pages_and_preserves_seed_archives(
    native_sources, tmp_path
):
    backend, frontend = native_sources
    inputs = [
        ROOT / "templates/vendor/yudao-backend.zip",
        ROOT / "templates/vendor/yudao-frontend.zip",
        backend / "sql/postgresql/ruoyi-vue-pro.sql",
    ]
    before = {str(path): sha(path) for path in inputs}
    first = prepare_yudao_navigation(backend, tmp_path / "reports")
    second = prepare_yudao_navigation(backend, tmp_path / "reports")
    assert first["modules"] == ["infra", "system"]
    assert first["after_sha256"] == second["after_sha256"]
    assert first["database_mutated"] is False and first["role_grants_expanded"] is False
    path = frontend / "apps/web-antd/src/views/infra/wbcustomer/index.vue"
    path.parent.mkdir(parents=True)
    path.write_text("<template><div>Native generated component</div></template>", encoding="utf-8")
    third = prepare_yudao_navigation(backend, tmp_path / "reports")
    assert "infra/wbcustomer/index" not in first["components"]
    assert "infra/wbcustomer/index" in third["components"]
    assert (
        first["after_sha256"]["RndInstalledMenuFilter.java"]
        != third["after_sha256"]["RndInstalledMenuFilter.java"]
    )
    assert before == {str(path): sha(path) for path in inputs}
    menu = (backend / JAVA_ROOT / "MenuServiceImpl.java").read_text(encoding="utf-8")
    role = (backend / JAVA_ROOT / "PermissionServiceImpl.java").read_text(encoding="utf-8")
    assert menu.count("rndInstalledMenus(") == 6
    assert "return menus.isEmpty() ? null : menus.get(0);" in menu
    assert "@Cacheable(value = RedisKeyConstants.PERMISSION_MENU_ID_LIST" not in menu
    assert "menuService.getMenuList(granted)" in role
    assert "menuService.getMenuList(), MenuDO::getId" in role
    assert role.count(MARKER) == 1
    # A source ZIP carries the same overlay and regenerates from its own shipped
    # frontend; this is a filesystem roundtrip, not a claimed database runtime.
    archive_path = tmp_path / "product.zip"
    with ZipFile(archive_path, "w") as archive:
        for root in (backend, frontend):
            for path in root.rglob("*"):
                if path.is_file():
                    archive.write(path, path.relative_to(tmp_path).as_posix())
    restored = tmp_path / "restored"
    with ZipFile(archive_path) as archive:
        archive.extractall(restored)
    replay = prepare_yudao_navigation(restored / "backend", tmp_path / "restored-reports")
    assert replay["capability_manifest_sha256"] == third["capability_manifest_sha256"]
    assert replay["after_sha256"] == third["after_sha256"]
    assert (
        sha(restored / "backend/sql/postgresql/ruoyi-vue-pro.sql")
        == before[str(backend / "sql/postgresql/ruoyi-vue-pro.sql")]
    )


def test_original_changed_overlay_context_fails_before_writing(native_sources, tmp_path):
    backend, _ = native_sources
    path = backend / JAVA_ROOT / "PermissionServiceImpl.java"
    path.write_text(
        path.read_text(encoding="utf-8").replace(
            "roleMenuMapper.selectListByRoleId(roleIds)", "changed(roleIds)"
        ),
        encoding="utf-8",
    )
    menu = backend / JAVA_ROOT / "MenuServiceImpl.java"
    before = sha(menu)
    with pytest.raises(ValueError, match="context changed"):
        prepare_yudao_navigation(backend, tmp_path / "reports")
    assert sha(menu) == before
    assert not (backend / JAVA_ROOT / "RndInstalledMenuFilter.java").exists()


def test_api_only_baseline_is_explicit_and_cannot_invent_frontend_capabilities(
    native_sources, tmp_path
):
    backend, frontend = native_sources
    shutil.rmtree(frontend)
    with pytest.raises(ValueError, match="component source is absent"):
        prepare_yudao_navigation(backend, tmp_path / "reports")
    receipt = prepare_yudao_navigation(backend, tmp_path / "reports", api_only=True)
    assert receipt["mode"] == "api-only-baseline"
    assert receipt["components"] == {}
    source = (backend / JAVA_ROOT / "RndInstalledMenuFilter.java").read_text(encoding="utf-8")
    assert "API_ONLY = true" in source
    assert "normalized(root).equals(normalized(component))" in source


def test_portable_and_runtime_rebuild_use_same_current_registry_overlay():
    from workbench.portable import HELPERS

    assert "yudao_navigation.py" in HELPERS
    assert "mappings.getHandlerMethods()" in POLICY
    assert "findMergedAnnotation(handler.getMethod(), PreAuthorize.class)" in POLICY
    assert "menuMapper" not in POLICY
    runtime = (ROOT / "scripts/ci_native_runtime.py").read_text(encoding="utf-8")
    assert runtime.index("copy_source(args.frontend_source, frontend)") < runtime.index(
        "install_backend(args.template"
    )
    assert "navigation_api_only=not args.frontend" in runtime


def test_actual_compiled_module_manifest_ignores_commented_business_dependencies(native_sources):
    backend, _ = native_sources
    assert installed_modules(backend) == ["infra", "system"]
    manifest = json.loads((ROOT / "templates/vendor/manifest.json").read_text(encoding="utf-8"))
    for item in manifest["sources"]:
        if item["template"] == "yudao-vben":
            assert sha(ROOT / "templates/vendor" / item["archive"]) == item["archive_sha256"]


def test_live_registered_handler_policy_ignores_unregistered_classes_and_refreshes_without_cache(
    tmp_path,
):
    # Compile the unchanged generated Spring adapter against small API-shaped test
    # interfaces; actual Spring boot/jar/UI execution remains native Actions' gate.
    java = shutil.which("java")
    if not java:
        pytest.skip("Java runtime absent")
    sources = {
        "MenuDO.java": MENU,
        "RndInstalledMenuFilter.java": render_filter(
            ["system", "infra"],
            {
                "system/user/index": {
                    "api_groups": [],
                    "local_only": False,
                    "embedded_service": False,
                },
                "infra/wbcustomer/index": {
                    "api_groups": [],
                    "local_only": False,
                    "embedded_service": False,
                },
                "infra/swagger/index": {
                    "api_groups": [],
                    "local_only": False,
                    "embedded_service": True,
                    "local_endpoint": "/doc.html",
                },
                "infra/webSocket/index": {
                    "api_groups": [],
                    "local_only": False,
                    "embedded_service": False,
                    "local_endpoint": "/infra/ws",
                },
            },
        ),
        "RndInstalledMenuPolicy.java": POLICY,
        "Resource.java": 'package jakarta.annotation; public @interface Resource { String name() default ""; }',
        "Lazy.java": "package org.springframework.context.annotation; public @interface Lazy {}",
        "Component.java": "package org.springframework.stereotype; public @interface Component {}",
        "PreAuthorize.java": "package org.springframework.security.access.prepost; @java.lang.annotation.Retention(java.lang.annotation.RetentionPolicy.RUNTIME) public @interface PreAuthorize { String value(); }",
        "RequestMapping.java": "package org.springframework.web.bind.annotation; @java.lang.annotation.Retention(java.lang.annotation.RetentionPolicy.RUNTIME) public @interface RequestMapping { String[] value(); }",
        "AnnotatedElementUtils.java": "package org.springframework.core.annotation; public class AnnotatedElementUtils { public static <A extends java.lang.annotation.Annotation>A findMergedAnnotation(java.lang.reflect.AnnotatedElement e, Class<A> type){return e.getAnnotation(type);} }",
        "ApplicationContext.java": 'package org.springframework.context; public class ApplicationContext { public java.util.Map<String,org.springframework.web.servlet.handler.AbstractUrlHandlerMapping> entries=new java.util.HashMap<>(); @SuppressWarnings("unchecked") public <T> java.util.Map<String,T> getBeansOfType(Class<T> type){return (java.util.Map<String,T>)(java.util.Map<?,?>)entries;} }',
        "AbstractUrlHandlerMapping.java": "package org.springframework.web.servlet.handler; public class AbstractUrlHandlerMapping { public java.util.Map<String,Object> entries=new java.util.HashMap<>(); public java.util.Map<String,Object> getHandlerMap(){return entries;} }",
        "ResourceHttpRequestHandler.java": "package org.springframework.web.servlet.resource; public class ResourceHttpRequestHandler { public java.util.List<org.springframework.core.io.Resource> locations=new java.util.ArrayList<>(); public java.util.List<org.springframework.core.io.Resource> getLocations(){return locations;} }",
        "core/Resource.java": "package org.springframework.core.io; public interface Resource { Resource createRelative(String path) throws java.io.IOException; boolean exists(); }",
        "RequestMappingHandlerMapping.java": """package org.springframework.web.servlet.mvc.method.annotation;
import java.util.*; import java.lang.reflect.*;
public class RequestMappingHandlerMapping {
 public record Mapping(Set<String> patterns){public Set<String> getPatternValues(){return patterns;}}
 public record Handler(Class<?> type,Method method){public Class<?> getBeanType(){return type;}public Method getMethod(){return method;}}
 public Map<Mapping,Handler> entries=new HashMap<>();
 public Map<Mapping,Handler> getHandlerMethods(){return entries;}
 public void add(Class<?> type,String name,String path)throws Exception{entries.put(new Mapping(Set.of(path)),new Handler(type,type.getMethod(name)));}
}""",
        "SystemController.java": """package cn.iocoder.yudao.module.system.controller.admin;
@org.springframework.web.bind.annotation.RequestMapping("/system/user")
public class SystemController {
 @org.springframework.security.access.prepost.PreAuthorize("@ss.hasPermission('system:user:query')") public void page(){}
 @org.springframework.security.access.prepost.PreAuthorize("@ss.hasPermission('system:user:delete')") public void unregistered(){}
}""",
        "BusinessController.java": """package cn.iocoder.yudao.module.infra.controller.admin;
@org.springframework.web.bind.annotation.RequestMapping("/infra/wb-customer")
public class BusinessController { public void page(){} public void create(){} }
""",
        "NavigationTest.java": """package cn.iocoder.yudao.module.system.service.permission;
import java.util.*;import cn.iocoder.yudao.module.system.dal.dataobject.permission.MenuDO;
import org.springframework.web.servlet.mvc.method.annotation.RequestMappingHandlerMapping;
import cn.iocoder.yudao.module.system.controller.admin.SystemController;
import cn.iocoder.yudao.module.infra.controller.admin.BusinessController;
public class NavigationTest {
 static Set<Long> ids(List<MenuDO> rows){Set<Long> result=new HashSet<>();for(var r:rows)result.add(r.getId());return result;}
 static void check(boolean value){if(!value)throw new AssertionError("live registered navigation");}
 public static void main(String[] args)throws Exception{
  var mappings=new RequestMappingHandlerMapping();
  mappings.add(SystemController.class,"page","/admin-api/system/user/page");
  var policy=new RndInstalledMenuPolicy();var field=policy.getClass().getDeclaredField("mappings");field.setAccessible(true);field.set(policy,mappings);var contextField=policy.getClass().getDeclaredField("context");contextField.setAccessible(true);var context=new org.springframework.context.ApplicationContext();contextField.set(policy,context);
  var rows=List.of(new MenuDO(1L,0L,1,"/system","",""),new MenuDO(2L,1L,2,"user","system/user/index",""),new MenuDO(3L,2L,3,"","","system:user:query"),new MenuDO(4L,2L,3,"","","system:user:delete"),new MenuDO(5L,0L,1,"/workbench","",""),new MenuDO(6L,5L,2,"wb-customer","infra/wbcustomer/index",""),new MenuDO(7L,6L,3,"","","infra:wb-customer:query"),new MenuDO(8L,6L,3,"","","infra:wb-customer:create"));
  check(ids(policy.filter(rows,rows)).equals(Set.of(1L,2L,3L)));
  mappings.add(BusinessController.class,"page","/admin-api/infra/wb-customer/page");
  check(ids(policy.filter(rows,rows)).equals(Set.of(1L,2L,3L,5L,6L,7L)));
  mappings.add(BusinessController.class,"create","/admin-api/infra/wb-customer/create");
  check(ids(policy.filter(rows,rows)).equals(Set.of(1L,2L,3L,5L,6L,7L,8L)));
  check(ids(policy.filter(List.of(rows.get(6)),rows)).equals(Set.of(7L)));
  var more=new ArrayList<MenuDO>(rows);more.add(new MenuDO(9L,0L,1,"/infra","",""));more.add(new MenuDO(10L,9L,2,"swagger","infra/swagger/index",""));more.add(new MenuDO(11L,9L,2,"ws","infra/webSocket/index",""));
  check(!ids(policy.filter(more,more)).contains(10L));check(!ids(policy.filter(more,more)).contains(11L));
  var urlMapping=new org.springframework.web.servlet.handler.AbstractUrlHandlerMapping();context.entries.put("resources",urlMapping);
  urlMapping.entries.put("/infra/ws",new Object());check(ids(policy.filter(more,more)).contains(11L));urlMapping.entries.remove("/infra/ws");check(!ids(policy.filter(more,more)).contains(11L));
  var resources=new org.springframework.web.servlet.resource.ResourceHttpRequestHandler();urlMapping.entries.put("/**",resources);
  final boolean[] exists={false};resources.locations.add(new org.springframework.core.io.Resource(){public org.springframework.core.io.Resource createRelative(String path){check(path.equals("doc.html"));return this;}public boolean exists(){return exists[0];}});
  check(!ids(policy.filter(more,more)).contains(10L));exists[0]=true;check(ids(policy.filter(more,more)).contains(10L));
  context.entries.clear();check(!ids(policy.filter(more,more)).contains(10L));
  context.entries.put("resources",urlMapping);exists[0]=false;check(!ids(policy.filter(more,more)).contains(10L));
  mappings.entries.clear();check(policy.filter(rows,rows).isEmpty());
  System.out.println("live registered navigation PASS");
 }
}""",
    }
    paths = []
    for name, body in sources.items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
        paths.append(str(path))
    result = subprocess.run(
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
            *paths,
        ],
        capture_output=True,
        text=True,
        timeout=45,
    )
    assert result.returncode == 0, result.stderr
    result = subprocess.run(
        [
            java,
            "-cp",
            str(tmp_path),
            "cn.iocoder.yudao.module.system.service.permission.NavigationTest",
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    assert "live registered navigation PASS" in result.stdout
````
