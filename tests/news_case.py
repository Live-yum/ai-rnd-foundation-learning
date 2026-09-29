"""Regression extracted from the user's supplied failed conversation (no private transcript)."""

from workbench.domain import Plan, Requirement


def news_plan():
    return Plan(
        title="游戏资讯助手",
        data_scope="per_user",
        entities=[
            {
                "name": "news",
                "description": "个人游戏资讯",
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
                        "choices": ["资讯", "攻略", "大神"],
                        "required": False,
                        "filterable": True,
                    },
                ],
            }
        ],
        acceptance=["标题正文搜索", "分类和含边界日期区间筛选", "字段格式及长度", "逐用户隔离"],
    )


def news_requirement():
    return Requirement(
        summary="个人录入游戏资讯，采用全部已明确条件",
        users=["个人用户"],
        data_scope="per_user",
        features=["资讯CRUD", "标题正文搜索", "分类枚举", "真实日期及含边界范围"],
        acceptance=news_plan().acceptance,
        recommendations=["使用标题250字、正文3000字", "日期区间包含两端"],
        facts={
            "title_max_length": 250,
            "body_max_length": 3000,
            "date_format": "YYYY-MM-DD",
            "category": ["资讯", "攻略", "大神"],
        },
    )
