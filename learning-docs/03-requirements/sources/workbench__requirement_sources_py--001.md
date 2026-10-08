# workbench/requirement_sources.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：在规划前拒绝明确来源互相冲突的分析候选。** 对能可靠定位的同一原子义务比较明确值，保留用户原文、已确认契约和模型候选来源；矛盾走已有有界分析纠错，不替用户选值或批准，未知旧文本仍保守校验。

**对应关系：** Workflow.analyse → 来源冲突诊断与需求账本 → 原有clarification关口；有效分析才进入设计。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.requirement_coverage`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

**带着一个具体问题阅读：** 先把用户原文、已确认合同和模型候选放在各自来源中比较。若同一字段被明确要求为必填，而候选却明确写成可选，应返回冲突诊断交回分析纠错；函数不替用户选择哪项约束获胜。无法可靠定位的旧文本继续保守校验，不能把猜测写成已批准事实。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `_records`（L23–L37）：接收`requirement`。 控制顺序：L24遍历`enumerate(requirement.field_requirements)`；L26遍历`value.items()`；L27按`attribute in {"entity", "field"}`分支。 调用`enumerate`、`field.model_dump`、`value.items`、`json.dumps`、`explicit_legacy_field_constraints`。使用yield把资源/结果交给调用方，继续执行后续清理语句。
- `_identity`（L40–L44）：接收`record`。 调用`{"exclusive_minimum": "minimum", "exclusive_maximum": "maximum"}.…`。 返回路径：L44的`record["entity"], record["field"], attribute`。
- `_value`（L47–L54）：接收`record`。 控制顺序：L49按`type(value) is int`分支；L51按`record["attribute"] == "choices"`分支。 调用`type`、`{"exclusive_minimum": 1, "exclusive_maximum": -1}.get`、`sorted`、`set`、`json.dumps`。 返回路径：L54的`type(value).__name__, json.dumps(value, ensure_ascii=False, sort_keys=True)`。
- `_signature`（L57–L58）：接收`record`。 调用`_identity`、`_value`。 返回路径：L58的`_identity(record), _value(record)`。
- `_initial_user_sources`（L61–L108）：接收`parsed`、`human`、`cursor`。 源码说明：Use explicit current input, never infer a historical winner by recency.。 控制顺序：L65遍历`enumerate(parsed)`；L66按`index != 0 and index < cursor`分支；L68遍历`records`；L83遍历`fresh.items()`；L100按`correction and len({_value(item) for item in prior}) <= 1 and len({_value(item) for i…`分支。 调用`defaultdict`、`enumerate`、`digest`、`(original if index == 0 else fresh)[_identity(record)].append`、`_identity`、`fresh.items`、`original.get`、`any`、`_authorized`等。 返回路径：L108的`[record for group in original.values() for record in group]`。
- `analysis_source_conflicts`（L111–L208）：接收`previous`、`candidate`、`human`、`changes`、`cursor`。 源码说明：Return exact contradictory source pairs; never rewrite or approve intent. Source indices refer to the reconciled candidate, with previous-source and original user-message indices retained separately. 。 控制顺序：L121遍历`old_records`；L128遍历`enumerate(human)`；L134遍历`parsed`；L140按`evidence not in source_by_signature[_signature(record)]`分支；L144遍历`records`；L167按`retained`分支；L184按`not previous`分支；L185遍历`_initial_user_sources(parsed_human, human, cursor)`。后续分支沿下方源码相同行号继续阅读。 调用`list`、`_records`、`Requirement.model_validate`、`defaultdict`、`old_by_signature[_signature(record)].append`、`_signature`、`enumerate`、`candidate.model_copy`、`explicit_legacy_field_constraints`等。 返回路径：L208的`diagnostics`。
- `analysis_feedback`（L211–L259）：接收`diagnostics`、`max_chars`。 源码说明：Bound prompt feedback; full source texts remain in the durable ledger. Human-message references point to the existing immutable message history. The selected excerpt is presentation only; indices and 。 控制顺序：L219遍历`diagnostics`；L221遍历`diagnostic["sources"]`；L223按`len(str(source.get("path", ""))) > 200`分支；L249按`len(json.dumps([*result, compact], ensure_ascii=False)) > max_chars - 256`分支。 调用`dict`、`len`、`str`、`source.get`、`digest`、`sources.append`、`json.dumps`、`result.append`。 返回路径：L259的`result`。

</details>

**创建路径：** `workbench/requirement_sources.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L259。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`10997`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/requirement_sources.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "b39b09edd027194762deb0226ed2f349232d1a38ec5fbeb05b442d28b24324e6"} -->
````python
# workbench/requirement_sources.py
"""Reject contradictory analysis output without choosing between requirement sources.

This guard is deliberately narrower than semantic review. Only exact typed field
obligations and the shared, conservative legacy normalizer participate. Unparsed
text is retained, and a missing user quote never authorizes removing it.

It detects contradictions within a reconciled candidate, including retained prior
requirements. On first analysis it also compares corresponding explicit scalar
obligations in the original/current user input. This is not complete semantic
grounding: prose normalization covers required, length and explicit integer bounds, using
typed, entity-qualified field vocabulary, plus named queries and explicit query closure.
Candidate query flags never authorize extra queries in original source text.
Unknown prose remains untouched.
"""

import json
from collections import defaultdict

from workbench.domain import Requirement, RequirementChange, digest
from workbench.requirement_coverage import _authorized, explicit_legacy_field_constraints


def _records(requirement):
    for index, field in enumerate(requirement.field_requirements):
        value = field.model_dump(exclude_none=True)
        for attribute, expected in value.items():
            if attribute in {"entity", "field"}:
                continue
            yield {
                "source": {"section": "field_requirements", "index": index},
                "entity": field.entity,
                "field": field.field,
                "attribute": attribute,
                "expected": expected,
                "text": json.dumps(value, ensure_ascii=False, sort_keys=True),
            }
    yield from explicit_legacy_field_constraints(requirement)


def _identity(record):
    attribute = {"exclusive_minimum": "minimum", "exclusive_maximum": "maximum"}.get(
        record["attribute"], record["attribute"]
    )
    return record["entity"], record["field"], attribute


def _value(record):
    value = record["expected"]
    if type(value) is int:
        value += {"exclusive_minimum": 1, "exclusive_maximum": -1}.get(record["attribute"], 0)
    if record["attribute"] == "choices":
        value = sorted(set(value))
    # Do not conflate True with 1 or a string number with a numeric obligation.
    return type(value).__name__, json.dumps(value, ensure_ascii=False, sort_keys=True)


def _signature(record):
    return _identity(record), _value(record)


def _initial_user_sources(parsed, human, cursor):
    """Use explicit current input, never infer a historical winner by recency."""
    original = defaultdict(list)
    fresh = defaultdict(list)
    for index, records in enumerate(parsed):
        if index != 0 and index < cursor:
            continue
        for record in records:
            item = {
                **record,
                "source": {"section": "user_messages", "index": index},
                "origin": "user_input",
                "user_sources": [
                    {
                        "user_message_index": index,
                        "sha256": digest(human[index]),
                        "fresh": index >= cursor,
                    }
                ],
                "correction_sources": [],
            }
            (original if index == 0 else fresh)[_identity(record)].append(item)
    for key, current in fresh.items():
        prior = original.get(key, [])
        # Existing explicit-change authorization is intentionally strict. A
        # correction must state the same field/property/value; a recommendation
        # or a last-message-wins policy cannot erase original input conflicts.
        correction = any(
            _authorized(
                RequirementChange(
                    section="field_requirements",
                    key=f"{item['entity'] or ''}.{item['field']}.{item['attribute']}",
                    replacement=item["expected"],
                    source_quote=human[item["source"]["index"]],
                ),
                [human[item["source"]["index"]]],
            )
            for item in current
        )
        if (
            correction
            and len({_value(item) for item in prior}) <= 1
            and len({_value(item) for item in current}) == 1
        ):
            original[key] = current
        else:
            original[key].extend(current)
    return [record for group in original.values() for record in group]


def analysis_source_conflicts(previous, candidate, human, *, changes=(), cursor=0):
    """Return exact contradictory source pairs; never rewrite or approve intent.

    Source indices refer to the reconciled candidate, with previous-source and
    original user-message indices retained separately. Human evidence is reported
    as evidence, not used to decide which conflicting obligation should win.
    """
    records = list(_records(candidate))
    old_records = list(_records(Requirement.model_validate(previous))) if previous else []
    old_by_signature = defaultdict(list)
    for record in old_records:
        old_by_signature[_signature(record)].append(record)

    # Use the candidate's declared field vocabulary and the very same parser for
    # source text. No planner defaults, guessed aliases, or model verdicts enter.
    source_by_signature = defaultdict(list)
    parsed_human = []
    for index, text in enumerate(human):
        source_requirement = candidate.model_copy(
            update={"features": [text], "acceptance": [], "facts": {}}
        )
        parsed = explicit_legacy_field_constraints(source_requirement)
        parsed_human.append(parsed)
        for record in parsed:
            evidence = {
                "user_message_index": index,
                "sha256": digest(text),
                "fresh": index >= cursor,
            }
            if evidence not in source_by_signature[_signature(record)]:
                source_by_signature[_signature(record)].append(evidence)

    groups = defaultdict(list)
    for record in records:
        # An unqualified name repeated across entities is not the same obligation
        # as any one qualified field. The shared parser leaves it unresolved.
        key = _identity(record)
        signature = _signature(record)
        matching_old = old_by_signature.get(signature, [])
        retained = next(
            (
                old
                for old in matching_old
                if old["source"]["section"] == record["source"]["section"]
                and (
                    old["text"] == record["text"]
                    or record["source"]["section"] == "field_requirements"
                )
            ),
            None,
        )
        item = {
            **record,
            "origin": "previous_requirement" if retained else "model_analysis",
            "user_sources": source_by_signature.get(signature, []),
        }
        if retained:
            item["previous_source"] = dict(retained["source"])
            item["previous_text"] = retained["text"]
        # Only reconciliation-validated edits establish explicit correction
        # provenance. Matching old or new prose alone never authorizes an edit.
        item["correction_sources"] = [
            {"source_quote": change["source_quote"], "sources": change.get("sources", [])}
            for change in changes
            if change.get("authorized")
            and change["section"] == record["source"]["section"]
            and (
                change["key"] == f"{record['entity'] or ''}.{record['field']}.{record['attribute']}"
                or change.get("replacement") == record["text"]
            )
        ]
        groups[key].append(item)

    if not previous:
        for record in _initial_user_sources(parsed_human, human, cursor):
            key = _identity(record)
            # The guard compares corresponding explicit atomic obligations. It
            # does not claim that omissions or unreliable prose were verified.
            if key in groups:
                groups[key].append(record)

    diagnostics = []
    for (entity, field, attribute), group in groups.items():
        # Keep every source, including equivalent restatements, when explaining
        # a real conflict. Equivalent wording alone never becomes a blocker.
        if len({_value(record) for record in group}) < 2:
            continue
        target = f"{entity + '.' if entity else ''}{field}.{attribute}"
        diagnostics.append(
            {
                "code": "requirement_source_conflict",
                "target": {"entity": entity, "field": field},
                "attribute": attribute,
                "sources": group,
                "message": f"需求分析来源冲突：{target} 存在不同的明确值；保留原始来源，修正分析后再设计",
            }
        )
    return diagnostics


def analysis_feedback(diagnostics, *, max_chars=16000):
    """Bound prompt feedback; full source texts remain in the durable ledger.

    Human-message references point to the existing immutable message history.
    The selected excerpt is presentation only; indices and digests, rather than
    a truncated sentence, establish provenance. Omitted diagnostics still block.
    """
    result = []
    for diagnostic in diagnostics:
        sources = []
        for record in diagnostic["sources"]:
            source = dict(record["source"])
            if len(str(source.get("path", ""))) > 200:
                source["path_sha256"] = digest(source["path"])
                source["path"] = source["path"][:200]
            sources.append(
                {
                    "source": source,
                    "expected": record["expected"],
                    "origin": record["origin"],
                    "text_sha256": digest(record["text"]),
                    "excerpt": record["text"][:200],
                    "user_sources": record["user_sources"],
                    **(
                        {"previous_source": record["previous_source"]}
                        if "previous_source" in record
                        else {}
                    ),
                }
            )
        compact = {
            "code": diagnostic["code"],
            "target": diagnostic["target"],
            "attribute": diagnostic["attribute"],
            "sources": sources,
        }
        # Reserve space for an explicit overflow marker instead of silently
        # dropping a conflict or increasing the model's context budget.
        if len(json.dumps([*result, compact], ensure_ascii=False)) > max_chars - 256:
            result.append(
                {
                    "code": "additional_source_conflicts",
                    "count": len(diagnostics) - len(result),
                    "detail": "其余来源冲突保留在本轮 requirement ledger；未解决前仍阻止设计",
                }
            )
            break
        result.append(compact)
    return result
````
