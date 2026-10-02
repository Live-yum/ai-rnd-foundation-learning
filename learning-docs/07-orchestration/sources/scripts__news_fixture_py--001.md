# scripts/news_fixture.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：资讯需求与智能推荐的显式测试响应。** 保存固定资讯规格及能力说明，故意让首轮把无关限制误当阻塞，检查后续是否根据真实反馈修正并保留字段。它只被测试导入，不是生产未配模型时的默认响应。

**对应关系：** ci_guided_browser/Daytona资讯验收 → 显式夹具 → 正常工作流。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `news_spec`（L16–L61）：不接收显式业务参数，从已配置对象/模块读取依赖。 返回路径：L17的`{ "title": "游戏资讯助手", "data_scope": "per_user", "entities": [ { "name": "news", "descriptio…`。
- `news_requirement`（L64–L91）：接收`autonomous`。 调用`news_spec`。 返回路径：L65的`{ "summary": "泰拉瑞瑞亚游戏资讯的登录后个人管理页面", "users": ["登录后管理自己资讯的用户"], "data_scope": "per_user", "…`。
- `assert_resolution`（L94–L99）：接收`payload`。 控制顺序：L95断言`payload["autonomous"] is True`；L96断言`payload["original_request"]`；L97断言`payload["resolution_feedback"]["unsupported"] == LIMITATIONS`；L98断言`payload["resolution_feedback"]["questions"] == [QUESTION]`；L99断言`payload["current_requirement"]["facts"] == news_requirement()["facts"]`。 调用`news_requirement`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `assert_approved`（L102–L106）：接收`payload`。 控制顺序：L104断言`approved["unsupported"] == [] and approved["questions"] == []`；L105断言`approved["limitations"] == LIMITATIONS`；L106断言`approved["facts"] == news_requirement()["facts"]`。 调用`news_requirement`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `NewsFixture`（L109–L128）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `NewsFixture.__init__`（L110–L111）：不接收显式业务参数，从已配置对象/模块读取依赖。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `NewsFixture.complete`（L113–L128）：接收`run_id`、`key`、`instruction`、`payload`、`schema`。 控制顺序：L117按`schema is Requirement`分支；L118按`payload["autonomous"]`分支；L121按`schema is Plan`分支；L124断言`context["repo_map"]["provider"] == "aider-cli-repo-map"`；L125断言`context["repo_map"]["network"] == "disabled"`；L126断言`context["retrieval"]["mode"].startswith("ast+continue-fts5")`；L128抛异常，停止当前正常路径。 调用`self.calls.append`、`assert_resolution`、`Requirement.model_validate`、`news_requirement`、`assert_approved`、`context["retrieval"]["mode"].startswith`、`Plan.model_validate`、`news_spec`、`AssertionError`。 返回路径：L120的`Requirement.model_validate(news_requirement(payload["autonomous"]))`；L127的`Plan.model_validate(news_spec())`。

</details>

**创建路径：** `scripts/news_fixture.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L128。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`5013`。本段原文以LF换行结束。

<!-- learning-source: {"path": "scripts/news_fixture.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "5a95d665f086237cbdd9f2711e74abfd4145731e3f95c2d72ca51b65d31e072f"} -->
````python
# scripts/news_fixture.py
"""Explicit deterministic model fixtures for CI, never production fallback models.

The first response deliberately reproduces the reported erroneous template-boundary
list. The next response can resolve it only after receiving stored scope and
recommendation feedback. Real processes, databases and tools remain unmocked.
"""

LIMITATIONS = [
    "自动从外部网站采集或抓取游戏资讯不受当前模板支持。",
    "面向无需登录的公众开放浏览不受当前模板支持。",
]
QUESTION = "需要个人资讯管理页面，还是无需登录的公众网站？如无特别说明，按个人管理页面规划。"
ORIGINAL_REQUEST = "泰拉瑞瑞亚游戏资讯"


def news_spec():
    return {
        "title": "游戏资讯助手",
        "data_scope": "per_user",
        "entities": [
            {
                "name": "news",
                "description": "游戏资讯",
                "fields": [
                    {
                        "name": "title",
                        "kind": "text",
                        "required": True,
                        "min_length": 1,
                        "max_length": 250,
                        "searchable": True,
                    },
                    {
                        "name": "body",
                        "kind": "text",
                        "required": True,
                        "min_length": 1,
                        "max_length": 3000,
                        "searchable": True,
                    },
                    {
                        "name": "published_on",
                        "kind": "date",
                        "required": True,
                        "filterable": True,
                        "date_range": True,
                    },
                    {
                        "name": "category",
                        "kind": "enum",
                        "required": False,
                        "choices": ["资讯", "攻略", "大神"],
                        "filterable": True,
                    },
                ],
            }
        ],
        "acceptance": ["标题正文搜索", "分类筛选", "真实日期及含边界日期区间", "逐用户隔离"],
        "custom_rules": [],
        "unsupported": [],
    }


def news_requirement(autonomous=False):
    return {
        "summary": "泰拉瑞瑞亚游戏资讯的登录后个人管理页面",
        "users": ["登录后管理自己资讯的用户"],
        "data_scope": "per_user",
        "features": [
            "标题与正文必填",
            "发布日期是真实日期",
            "分类可选",
            "资讯增删改查",
            "标题正文搜索",
            "分类与含边界日期区间组合筛选",
        ],
        "acceptance": news_spec()["acceptance"],
        "questions": [] if autonomous else [QUESTION],
        "unsupported": [] if autonomous else LIMITATIONS,
        "limitations": LIMITATIONS if autonomous else [],
        "recommendations": [
            "未要求采集或公众浏览，采用登录后个人手动录入管理；标题250字，正文3000字，日期区间含边界"
        ],
        "assumptions": ["用户没有明确要求采集或匿名公开网站"],
        "facts": {
            "标题长度上限": "250字符",
            "正文长度上限": "3000字符",
            "分类是否必填": "否",
            "日期区间": "包含起始日和结束日",
        },
    }


def assert_resolution(payload):
    assert payload["autonomous"] is True
    assert payload["original_request"]
    assert payload["resolution_feedback"]["unsupported"] == LIMITATIONS
    assert payload["resolution_feedback"]["questions"] == [QUESTION]
    assert payload["current_requirement"]["facts"] == news_requirement()["facts"]


def assert_approved(payload):
    approved = payload["approved_requirement"]
    assert approved["unsupported"] == [] and approved["questions"] == []
    assert approved["limitations"] == LIMITATIONS
    assert approved["facts"] == news_requirement()["facts"]


class NewsFixture:
    def __init__(self):
        self.calls = []

    def complete(self, run_id, key, instruction, payload, schema):
        from workbench.domain import Plan, Requirement

        self.calls.append(key)
        if schema is Requirement:
            if payload["autonomous"]:
                assert_resolution(payload)
            return Requirement.model_validate(news_requirement(payload["autonomous"]))
        if schema is Plan:
            assert_approved(payload)
            context = payload["code_context"]["contexts"][0]
            assert context["repo_map"]["provider"] == "aider-cli-repo-map"
            assert context["repo_map"]["network"] == "disabled"
            assert context["retrieval"]["mode"].startswith("ast+continue-fts5")
            return Plan.model_validate(news_spec())
        raise AssertionError("Deterministic news CRUD needs no coding model: " + key)
````
