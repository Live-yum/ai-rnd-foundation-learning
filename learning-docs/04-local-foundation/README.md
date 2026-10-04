# 04 · 文件安全与源码检索

[总目录](../README.md) · [上一阶段](../03-requirements/README.md) · [下一阶段](../05-product/README.md)

## 检索要能回答“证据在哪一行”

`filesystem.py` 是其他工具的共同入口：解析目标必须留在授权根目录内，遍历时排除敏感配置、运行数据和日志，写入使用原子替换，解压检查危险路径。它看起来比模型调用普通，却决定后面索引和交付包会不会把 `.env`、数据库或运行日志当源码带走。先跟踪 `inside → files → manifest`，再看生成器、上下文和打包器怎样共同使用这些函数。

`symbols.py` 负责多语言语法；Python使用AST，Java/TypeScript/JavaScript/HTML使用固定Tree-sitter语法。`knowledge.build_index` 保存文件SHA、符号及起止行，第二次只重用指纹未变的文件。`retrieval.py` 再生成FTS索引、检索片段和紧凑仓库地图。它们不是同一个黑箱：解析告诉你“这个定义在哪”，全文检索告诉你“哪些位置含相关词”，新鲜度检查告诉你“现在还能不能信这个索引”。

`tools.py` 只接收明确的字符串参数数组，清理子进程环境、设置期限并清理本次进程组。它是可信固定工具的执行器，不是可接收任意模型 shell 的安全沙箱。`rules.py` 允许有限AST节点，按自己的解释器计算单记录规则；第07站实现的 `coding.py` 会进一步把改动锁定到 `custom_rules.py` 和正确前像SHA。规则通过也只证明那段受限业务表达式有效，不能由此授权改鉴权、测试或启动器。

## 观察真实索引的生命周期

保存为 `.learning/checks/04_index.py`：

```python
# .learning/checks/04_index.py
from pathlib import Path
from tempfile import TemporaryDirectory
from workbench.knowledge import build_index
from workbench.retrieval import query
from workbench.rules import Rules, UnsafeRule

with TemporaryDirectory(prefix="rnd-learning-index-") as temporary:
    root = Path(temporary)
    source, index = root / "source", root / "index"
    source.mkdir()
    file = source / "demo.py"
    file.write_text("def model_for(stage):\n    return stage\n", encoding="utf-8")
    assert build_index(source, index)["files"] == 1
    assert build_index(source, index)["reused"] == 1
    assert any(hit["path"] == "demo.py" for hit in query(source, index, "model_for")["matches"])
    file.write_text("def model_for(stage):\n    return 'changed'\n", encoding="utf-8")
    try:
        query(source, index, "model_for")
    except ValueError:
        pass
    else:
        raise AssertionError("stale index was accepted")
rule = Rules(
    "def validate(entity, data):\n    if data['quantity'] < 0:\n        raise ValueError('nonnegative')\n    return None\n"
)
rule.validate("request", {"quantity": 0})
try:
    rule.validate("request", {"quantity": -1})
except ValueError:
    pass
else:
    raise AssertionError("negative example was accepted")
try:
    Rules("import os\n")
except UnsafeRule:
    pass
else:
    raise AssertionError("arbitrary code was accepted")
print("04 PASS: source-backed retrieval, stale rejection and bounded rules")
```

```bash
# .learning/commands/04-check.sh
uv run python .learning/checks/04_index.py
```

应打印 `04 PASS`。其中 `demo.py` 只被当源码解析，没有执行它。索引和源码是并列目录，因为把输出放进被扫描的目录会产生自我索引。现在的检索不需要Node和向量服务，切换更多引擎要等第11站。

学习时随手打开命中的文件，看行号对应的真实函数；然后把 `query` 的字符预算调得过小，观察明确拒绝，而不是让上下文静默截断。上下文预算与来源指纹共同保护规划：模型收到的是可追溯的源码证据，源码注释也仍然是不可信数据，不能覆盖用户批准。

## 本阶段源码和后续依赖

本阶段首次创建 23 个源文件，完整位置见[文件落盘顺序](files.md)。已在前站创建的模块不重复覆盖；本章深入使用已有模块时回到[总索引](../source-index.md)查找。只有各步骤写明的检查代表本阶段成果，完整平台和外部服务验收留到最后一站。
