"""Conservative, bounded prose equivalence for repeated analysis output.

There is no similarity threshold: different permissions, constraints, targets,
negations and unknown paraphrases stay distinct. Only exact normalization or
fully recognized equivalent role/CRUD phrases share a key. The ledger records
all collapsed spellings; old immutable ledger entries are never edited.
"""

import re


def _key(section, text):
    # Normalize only delimiters in recognized phrases. Unknown prose may
    # contain literal filenames, enum values or distinct compatibility glyphs.
    normalized = text.strip().replace("（", "(").replace("）", ")")
    if section == "users":
        contact = re.fullmatch(
            r"([^()，,；;]{1,60})\((?:仅作为|仅为|仅是|仅)(?:报名)?联系人\)", normalized
        )
        if contact:
            return "contact-only", contact[1]
    if section in {"features", "acceptance"}:
        # Only complete CRUD phrases, with exactly the same entity wording.
        # Extra clauses/qualifiers do not match and therefore cannot disappear.
        operation = r"(?:增删改查|新增[、,]查询[、,]修改[、,](?:和)?删除)"
        target = r"([^，,；;。()与及和]{1,100}?)"
        patterns = (
            rf"对{target}进行{operation}",
            rf"{target}支持{operation}",
            rf"(?:支持)?{target}(?:的)?{operation}",
        )
        for pattern in patterns:
            match = re.fullmatch(pattern, normalized)
            if match:
                return "crud", match[1].removesuffix("的")
    return "literal", text.strip()


def canonical_list(section, values, audit=None):
    seen, result = {}, []
    for text in values:
        key = _key(section, text)
        if key in seen:
            if audit is not None:
                audit.append({"section": section, "retained": seen[key], "duplicate": text})
        else:
            seen[key] = text
            result.append(text)
    return result


def canonicalize_requirement(data, audit=None):
    for section in ("users", "features", "acceptance"):
        data[section] = canonical_list(section, data[section], audit)
