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
