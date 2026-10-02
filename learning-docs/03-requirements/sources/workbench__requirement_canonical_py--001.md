# workbench/requirement_canonical.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：对已确认等价的需求表述进行保守去重。** 只合并完整匹配的角色或CRUD表述及规范化文本；不同权限、否定、主体、约束和未知改写不折叠。记录保留项和重复写法，旧账本不可回写。

**对应关系：** reconcile及能力恢复 → canonicalize_requirement → 新需求与新增canonicalization审计。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `_key`（L12–L36）：接收`section`、`text`。 控制顺序：L16按`section == "users"`分支；L20按`contact`分支；L22按`section in {"features", "acceptance"}`分支；L32遍历`patterns`；L34按`match`分支。 调用`text.strip().replace("（", "(").replace`、`text.strip().replace`、`text.strip`、`re.fullmatch`、`match[1].removesuffix`。 返回路径：L21的`"contact-only", contact[1]`；L35的`"crud", match[1].removesuffix("的")`；L36的`"literal", text.strip()`。
- `canonical_list`（L39–L49）：接收`section`、`values`、`audit`。 控制顺序：L41遍历`values`；L43按`key in seen`分支；L44按`audit is not None`分支。 调用`_key`、`audit.append`、`result.append`。 返回路径：L49的`result`。
- `canonicalize_requirement`（L52–L54）：接收`data`、`audit`。 控制顺序：L53遍历`("users", "features", "acceptance")`。 调用`canonical_list`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。

</details>

**创建路径：** `workbench/requirement_canonical.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L54。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`2167`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/requirement_canonical.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "cc302c7b6e87e4a0b1187d23dffbed13ce1e0f4cea57809c1f4c6f783de08c12"} -->
````python
# workbench/requirement_canonical.py
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
````
