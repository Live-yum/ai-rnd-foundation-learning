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
