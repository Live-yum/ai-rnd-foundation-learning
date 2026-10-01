"""Positive, read-only installed-menu boundary for the copied native Yudao product.

The upstream seed intentionally covers modules absent from cloud-mini. Never delete
those rows or rewrite role grants: intersect reads with registered runtime handlers
and the Vben components actually shipped in this product. Rebuild this manifest on
every build, including the baseline -> generated and standalone ZIP transitions.
"""

import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from workbench.filesystem import atomic_text, inside, sha, write_json

JAVA_ROOT = (
    "yudao-module-system/yudao-module-system-server/src/main/java/"
    "cn/iocoder/yudao/module/system/service/permission"
)
MARKER = "// Workbench installed-capability read boundary v1"
ASSIGN_MARKER = "// Workbench visible-menu assignment preserves hidden existing grants"


def installed_modules(backend):
    ns = {"m": "http://maven.apache.org/POM/4.0.0"}
    pom = ET.parse(Path(backend) / "yudao-server/pom.xml")
    result = []
    for dependency in pom.findall("m:dependencies/m:dependency", ns):
        artifact = dependency.findtext("m:artifactId", "", ns)
        match = re.fullmatch(r"yudao-module-([a-z][a-z0-9-]*)-server", artifact)
        if match and dependency.findtext("m:scope", "compile", ns) not in {"test", "provided"}:
            module = match[1]
            if not (Path(backend) / f"yudao-module-{module}/{artifact}/pom.xml").is_file():
                raise ValueError("Installed Yudao module source is absent: " + module)
            result.append(module)
    if "system" not in result or not result:
        raise ValueError("Installed Yudao system capability is missing")
    return sorted(set(result))


def frontend_capabilities(frontend, modules):
    """Trace bounded local imports before classifying any composite page as local.

    Components and helpers can contain the page's real transport dependency. Each
    API group needs a registered route at runtime; source existence is insufficient.
    """
    source = Path(frontend) / "apps/web-antd/src"
    if not (source / "views").is_dir():
        raise ValueError("Installed Vben component source is absent")
    parsed = {}

    def urls(body):
        values = re.findall(r"['\"`](/(?:[a-z][a-z0-9-]*/)+[^'\"`\s]*)", body)
        return sorted({value.split("?", 1)[0].split("${", 1)[0].rstrip("/") for value in values})

    def resolve(name):
        for suffix in ("", ".vue", ".ts", "/index.vue", "/index.ts"):
            candidate = inside(source, name + suffix)
            if candidate.is_file() and candidate.suffix in {".vue", ".ts", ".tsx"}:
                return candidate
        return None

    def parse(path):
        if path in parsed:
            return parsed[path]
        body = path.read_text(encoding="utf-8")
        if len(body) > 2_000_000:
            raise ValueError("Vben capability dependency exceeds source bound")
        groups, children, unresolved = [], [], []
        imports = set(re.findall(r"(?:from\s+|import\(\s*)['\"]([^'\"]+)['\"]", body))
        for name in sorted(imports):
            if name.startswith("#/api/"):
                api = resolve(name[2:])
                routes = urls(
                    body
                    if name == "#/api/request"
                    else api.read_text(encoding="utf-8")
                    if api
                    else ""
                )
                if routes:
                    groups.append(routes)
                else:
                    unresolved.append(name)
            elif name.startswith(("./", "../", "#/views/")):
                if name.startswith("#/"):
                    relative = name[2:]
                else:
                    candidate = (path.parent / name).resolve()
                    try:
                        relative = candidate.relative_to(source.resolve()).as_posix()
                    except ValueError as exc:
                        raise ValueError("Vben capability dependency escapes source") from exc
                child = resolve(relative)
                if child is not None:
                    children.append(child)
                elif not name.endswith((".css", ".scss", ".svg", ".png")):
                    unresolved.append(name)
        parsed[path] = (body, groups, children, unresolved)
        return parsed[path]

    result = {}
    for module in modules:
        for path in sorted((source / "views" / module).rglob("*.vue")):
            groups, bodies, unresolved, seen, pending = [], [], [], set(), [path]
            while pending:
                dependency = pending.pop()
                if dependency in seen:
                    continue
                seen.add(dependency)
                if len(seen) > 512:
                    raise ValueError("Vben capability dependency graph exceeds bound")
                body, direct_groups, children, unknown = parse(dependency)
                unresolved.extend(unknown)
                bodies.append(body)
                groups.extend(direct_groups)
                pending.extend(children)
            component = path.relative_to(source / "views").as_posix().removesuffix(".vue")
            combined = "\n".join(bodies)
            embedded = bool(re.search(r"<(?:IFrame|iframe)\b", combined))
            network = bool(
                re.search(
                    r"\b(?:requestClient|fetch|XMLHttpRequest|useWebSocket|WebSocket)\b", combined
                )
            )
            endpoint = re.search(r"VITE_BASE_URL\}(/[a-zA-Z0-9/_-]+(?:\.html)?)", combined)
            result[component] = {
                "api_groups": [list(group) for group in sorted({tuple(group) for group in groups})],
                "local_only": not groups and not unresolved and not embedded and not network,
                "unresolved_dependencies": sorted(set(unresolved)),
                "embedded_service": embedded,
                "local_endpoint": endpoint[1] if endpoint else "",
                "sha256": sha(path),
                "dependency_files": sorted(
                    dependency.relative_to(source).as_posix() for dependency in seen
                ),
            }
    return result


FILTER = r"""package cn.iocoder.yudao.module.system.service.permission;

import cn.iocoder.yudao.module.system.dal.dataobject.permission.MenuDO;
import java.util.*;

/** Pure capability intersection. It never mutates menus, users, roles or grants. */
final class RndInstalledMenuFilter {
    static final Set<String> MODULES = Set.of(__MODULES__);
    static final boolean API_ONLY = __API_ONLY__;
    record Page(List<Set<String>> apiGroups, boolean localOnly, boolean embedded, String endpoint) {}
    static final Map<String, Page> PAGES = new HashMap<>();
    static Set<Long> mergeVisibleGrants(Set<Long> existing, Set<Long> submitted, Set<Long> visible) {
        Set<Long> result = new HashSet<>(existing);
        result.removeAll(visible);
        if (submitted != null) for (Long id : submitted) if (visible.contains(id)) result.add(id);
        return result;
    }
    static {
__PAGES__
    }
    private static String component(MenuDO menu) {
        String value = menu.getComponent();
        return value == null ? "" : value.replaceFirst("^/", "").replaceFirst("\\.vue$", "");
    }
    private static String normalized(String value) {
        return value.replaceFirst("/index$", "").replaceAll("[^a-zA-Z0-9]", "").toLowerCase(Locale.ROOT);
    }
    private static boolean page(MenuDO menu, Set<String> routes, Set<String> roots, Set<String> domains) {
        String component = component(menu);
        Page page = PAGES.get(component);
        if (!domains.contains(component.split("/", 2)[0])) return false;
        if (API_ONLY) return roots.stream().anyMatch(root -> normalized(root).equals(normalized(component)));
        if (page == null || (page.embedded() && page.endpoint().isEmpty())) return false;
        if (!page.endpoint().isEmpty() && !routes.contains(page.endpoint())) return false;
        if (!page.apiGroups().isEmpty()) return page.apiGroups().stream().allMatch(group ->
                group.stream().anyMatch(route -> routes.contains(route)));
        if (page.localOnly()) return true;
        if (!page.endpoint().isEmpty()) return true;
        return roots.stream().anyMatch(root -> normalized(root).equals(normalized(component)));
    }
    private static boolean directory(MenuDO menu, Set<String> domains) {
        if (!(Objects.equals(menu.getType(), 1) || (Objects.equals(menu.getType(), 2) && component(menu).isEmpty()))) return false;
        String path = menu.getPath() == null ? "" : menu.getPath();
        if (path.contains(":") || path.contains("..")) return false;
        if (Objects.equals(menu.getParentId(), 0L)) {
            return path.equals("/workbench") || domains.stream().anyMatch(domain -> path.equals("/" + domain));
        }
        return !path.startsWith("/") || domains.stream().anyMatch(domain -> path.equals("/" + domain) || path.startsWith("/" + domain + "/"));
    }
    static List<MenuDO> filter(List<MenuDO> candidates, List<MenuDO> all,
                              Set<String> routes, Set<String> roots, Set<String> permissions,
                              Set<String> domains) {
        Map<Long, MenuDO> byId = new HashMap<>();
        for (MenuDO menu : all) byId.put(menu.getId(), menu);
        Set<Long> pages = new HashSet<>();
        for (MenuDO menu : all) if (Objects.equals(menu.getType(), 2) && page(menu, routes, roots, domains)) pages.add(menu.getId());
        Set<Long> eligible = new HashSet<>();
        for (MenuDO menu : all) {
            boolean leaf = pages.contains(menu.getId()) || (Objects.equals(menu.getType(), 3) && permissions.contains(menu.getPermission()));
            if (!leaf) continue;
            Set<Long> chain = new HashSet<>();
            MenuDO current = menu;
            boolean valid = true;
            while (current != null) {
                if (!chain.add(current.getId())) { valid = false; break; }
                if (current != menu && !pages.contains(current.getId()) && !directory(current, domains)) { valid = false; break; }
                if (Objects.equals(current.getParentId(), 0L)) break;
                current = byId.get(current.getParentId());
                if (current == null) valid = false;
            }
            if (valid) eligible.addAll(chain);
        }
        // An ACL-filtered candidate list remains an intersection: do not add parents.
        List<MenuDO> result = new ArrayList<>();
        for (MenuDO menu : candidates) if (eligible.contains(menu.getId())) result.add(menu);
        return result;
    }
}
"""


POLICY = r"""package cn.iocoder.yudao.module.system.service.permission;

import cn.iocoder.yudao.module.system.dal.dataobject.permission.MenuDO;
import jakarta.annotation.Resource;
import org.springframework.context.annotation.Lazy;
import org.springframework.context.ApplicationContext;
import org.springframework.core.annotation.AnnotatedElementUtils;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.stereotype.Component;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.servlet.mvc.method.annotation.RequestMappingHandlerMapping;
import org.springframework.web.servlet.handler.AbstractUrlHandlerMapping;
import org.springframework.web.servlet.resource.ResourceHttpRequestHandler;
import java.util.*;
import java.util.regex.*;

/** Registered Spring MVC handlers, including conditionals, are the live authority. */
@Component
public class RndInstalledMenuPolicy {
    @Resource(name = "requestMappingHandlerMapping")
    @Lazy
    private RequestMappingHandlerMapping mappings;
    @Resource
    private ApplicationContext context;

    public List<MenuDO> filter(List<MenuDO> candidates, List<MenuDO> all) {
        Set<String> routes = new HashSet<>(), roots = new HashSet<>(), permissions = new HashSet<>(), domains = new HashSet<>();
        Pattern modulePattern = Pattern.compile("\\.module\\.([a-z][a-z0-9]*)\\.controller\\.admin\\.");
        Pattern permissionPattern = Pattern.compile("'([a-z][a-z0-9-]*(?::[a-zA-Z0-9_-]+){2,})'");
        mappings.getHandlerMethods().forEach((mapping, handler) -> {
            for (String value : mapping.getPatternValues()) routes.add(value.replaceFirst("^/admin-api", ""));
            Matcher module = modulePattern.matcher(handler.getBeanType().getName());
            if (!module.find() || !RndInstalledMenuFilter.MODULES.contains(module.group(1))) return;
            domains.add(module.group(1));
            RequestMapping root = AnnotatedElementUtils.findMergedAnnotation(handler.getBeanType(), RequestMapping.class);
            if (root != null) for (String value : root.value()) roots.add("/" + value.replaceFirst("^/", ""));
            for (String value : mapping.getPatternValues()) {
                String route = value.replaceFirst("^/admin-api", "");
                routes.add(route);
                // Owned Workbench facades use business-service ACL checks instead of @PreAuthorize.
                // Retain only existing menu grants backed by an actual registered CRUD endpoint.
                Matcher generated = Pattern.compile("^/infra/(wb-[a-z0-9-]+)/(page|get|create|update|delete|export-excel)$").matcher(route);
                if (generated.matches()) {
                    String action = generated.group(2);
                    if (action.equals("page") || action.equals("get")) action = "query";
                    if (action.equals("export-excel")) action = "export";
                    permissions.add("infra:" + generated.group(1) + ":" + action);
                }
            }
            PreAuthorize annotation = AnnotatedElementUtils.findMergedAnnotation(handler.getMethod(), PreAuthorize.class);
            if (annotation == null) annotation = AnnotatedElementUtils.findMergedAnnotation(handler.getBeanType(), PreAuthorize.class);
            if (annotation != null) {
                Matcher permission = permissionPattern.matcher(annotation.value());
                while (permission.find()) permissions.add(permission.group(1));
            }
        });
        // Exact registered transports and actually served static resources can
        // back native tools without an admin Controller (e.g. Knife4j, WebSocket).
        // A jar/POM or an arbitrary external iframe URL is never sufficient.
        for (AbstractUrlHandlerMapping mapping : context.getBeansOfType(AbstractUrlHandlerMapping.class).values()) {
            mapping.getHandlerMap().forEach((path, handler) -> {
                if (!path.contains("*") && !path.contains("{")) routes.add(path);
                if (!path.equals("/**") || !(handler instanceof ResourceHttpRequestHandler resources)) return;
                for (RndInstalledMenuFilter.Page page : RndInstalledMenuFilter.PAGES.values()) {
                    String endpoint = page.endpoint();
                    if (!endpoint.matches("/[a-zA-Z0-9/_-]+\\.html")) continue;
                    for (org.springframework.core.io.Resource location : resources.getLocations()) {
                        try {
                            if (location.createRelative(endpoint.substring(1)).exists()) routes.add(endpoint);
                        } catch (java.io.IOException unavailable) { /* no positive capability */ }
                    }
                }
            });
        }
        return RndInstalledMenuFilter.filter(candidates, all, routes, roots, permissions, domains);
    }
}
"""


def render_filter(modules, pages, *, api_only=False):
    entries = []
    for component, page in sorted(pages.items()):
        groups = [
            "Set.of(" + ", ".join(map(json.dumps, group)) + ")" for group in page["api_groups"]
        ]
        entries.append(
            "        PAGES.put("
            + json.dumps(component)
            + ", new Page(List.of("
            + ", ".join(groups)
            + "), "
            + str(page["local_only"]).lower()
            + ", "
            + str(page["embedded_service"]).lower()
            + ", "
            + json.dumps(page.get("local_endpoint", ""))
            + "));"
        )
    return (
        FILTER.replace("__MODULES__", ", ".join(map(json.dumps, modules)))
        .replace("__PAGES__", "\n".join(entries))
        .replace("__API_ONLY__", str(api_only).lower())
    )


def _replace(source, old, new):
    if source.count(old) != 1:
        raise ValueError("Pinned Yudao installed-menu overlay context changed")
    return source.replace(old, new, 1)


def prepare_yudao_navigation(backend, reports, *, api_only=False):
    backend, reports = Path(backend), Path(reports)
    modules = installed_modules(backend)
    pages = {} if api_only else frontend_capabilities(backend.parent / "frontend-product", modules)
    menu_path = inside(backend, JAVA_ROOT + "/MenuServiceImpl.java")
    role_path = inside(backend, JAVA_ROOT + "/PermissionServiceImpl.java")
    menu, role = menu_path.read_text(encoding="utf-8"), role_path.read_text(encoding="utf-8")
    originals = {
        "MenuServiceImpl.java": sha(menu_path),
        "PermissionServiceImpl.java": sha(role_path),
    }
    if MARKER not in menu:
        menu = _replace(
            menu,
            "public class MenuServiceImpl implements MenuService {",
            "public class MenuServiceImpl implements MenuService {\n\n    "
            + MARKER
            + "\n    @Resource\n    private RndInstalledMenuPolicy rndInstalledMenuPolicy;\n\n    private List<MenuDO> rndInstalledMenus(List<MenuDO> candidates) {\n        return rndInstalledMenuPolicy.filter(candidates, menuMapper.selectList());\n    }",
        )
        for old, new in (
            (
                "return menuMapper.selectList();",
                "return rndInstalledMenus(menuMapper.selectList());",
            ),
            (
                "return menuMapper.selectList(reqVO);",
                "return rndInstalledMenus(menuMapper.selectList(reqVO));",
            ),
            (
                "List<MenuDO> menus = menuMapper.selectListByPermission(permission);",
                "List<MenuDO> menus = rndInstalledMenus(menuMapper.selectListByPermission(permission));",
            ),
            (
                "return menuMapper.selectById(id);",
                "List<MenuDO> menus = rndInstalledMenus(menuMapper.selectByIds(Collections.singleton(id)));\n        return menus.isEmpty() ? null : menus.get(0);",
            ),
            (
                "return menuMapper.selectByIds(ids);",
                "return rndInstalledMenus(menuMapper.selectByIds(ids));",
            ),
            (
                '    @Cacheable(value = RedisKeyConstants.PERMISSION_MENU_ID_LIST, key = "#permission")',
                "    // Live capability intersection must not reuse pre-overlay or disabled-service Redis entries.",
            ),
        ):
            menu = _replace(menu, old, new)
    if MARKER not in role:
        role = _replace(
            role,
            "return convertSet(roleMenuMapper.selectListByRoleId(roleIds), RoleMenuDO::getMenuId);",
            MARKER
            + "\n        Set<Long> granted = convertSet(roleMenuMapper.selectListByRoleId(roleIds), RoleMenuDO::getMenuId);\n        return convertSet(menuService.getMenuList(granted), MenuDO::getId);",
        )
    if ASSIGN_MARKER not in role:
        role = _replace(
            role,
            "Set<Long> menuIdList = CollUtil.emptyIfNull(menuIds);",
            ASSIGN_MARKER
            + "\n        Set<Long> assignableMenuIds = convertSet(menuService.filterDisableMenus(\n"
            "                menuService.getMenuListByTenant(new cn.iocoder.yudao.module.system.controller.admin.permission.vo.menu.MenuListReqVO()\n"
            "                        .setStatus(CommonStatusEnum.ENABLE.getStatus()))), MenuDO::getId);\n"
            "        Set<Long> menuIdList = RndInstalledMenuFilter.mergeVisibleGrants(dbMenuIds, menuIds, assignableMenuIds);",
        )
    # Validate both patches before writing any source; a changed upstream fails closed.
    for path, body in (
        (menu_path, menu),
        (role_path, role),
        (
            inside(backend, JAVA_ROOT + "/RndInstalledMenuFilter.java"),
            render_filter(modules, pages, api_only=api_only),
        ),
        (inside(backend, JAVA_ROOT + "/RndInstalledMenuPolicy.java"), POLICY),
    ):
        atomic_text(path, body)
    capability_path = inside(
        backend,
        "yudao-module-system/yudao-module-system-server/src/main/resources/"
        "rnd-installed-navigation.json",
    )
    write_json(
        capability_path,
        {
            "format": 1,
            "mode": "api-only-baseline" if api_only else "native-vben-product",
            "modules": modules,
            "components": pages,
            "runtime_authority": "registered-spring-mvc-handlers",
        },
    )
    receipt = {
        "format": 1,
        "mode": "api-only-baseline" if api_only else "native-vben-product",
        "authority": "registered-spring-mvc-handlers-intersected-with-existing-acl",
        "modules": modules,
        "components": pages,
        "database_mutated": False,
        "role_grants_expanded": False,
        "capability_manifest_sha256": sha(capability_path),
        "before_sha256": originals,
        "after_sha256": {
            name: sha(inside(backend, JAVA_ROOT + "/" + name))
            for name in (
                "MenuServiceImpl.java",
                "PermissionServiceImpl.java",
                "RndInstalledMenuFilter.java",
                "RndInstalledMenuPolicy.java",
            )
        },
    }
    write_json(reports / "installed-navigation.json", receipt)
    return receipt
