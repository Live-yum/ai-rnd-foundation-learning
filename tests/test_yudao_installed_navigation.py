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
