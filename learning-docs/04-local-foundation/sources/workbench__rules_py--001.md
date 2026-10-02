# workbench/rules.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：解释受限的业务表达式。** Rules先解析表达式AST，只接纳允许节点、操作符和变量，再解释它，而非调用Python eval执行模型产生的任意代码。输入、输出与示例均受Plan约束，拒绝导入、反射和文件系统操作。

**对应关系：** coding/aider_tool校验 + 成品对应规则解释器；test_safety及业务例子复验。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `UnsafeRule`（L11–L12）：继承`ValueError`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `Rules`（L29–L190）：继承`object`。把同一职责的方法放在一个对象中；`self`表示该对象，实例字段保存其依赖或状态。
- `Rules.__init__`（L30–L56）：接收`source`。 控制顺序：L31按`len(source) > 30000`分支；L32抛异常，停止当前正常路径；L34按`len(list(ast.walk(tree))) > 400`分支；L35抛异常，停止当前正常路径；L36按`len(tree.body) != 1 or not isinstance(tree.body[0], ast.FunctionDef)`分支；L37抛异常，停止当前正常路径；L40按`fn.name != "validate" or [a.arg for a in args.args] != ["entity", "data"] or args.def…`分支；L54抛异常，停止当前正常路径。 调用`len`、`UnsafeRule`、`ast.parse`、`list`、`ast.walk`、`isinstance`、`any`、`self._statements`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `Rules._statements`（L58–L94）：接收`body`、`depth`。 控制顺序：L59按`depth > 20`分支；L60抛异常，停止当前正常路径；L61遍历`body`；L62按`isinstance(node, ast.If)`分支；L66按`isinstance(node, ast.Raise)`分支；L68按`node.cause or not isinstance(call, ast.Call) or not isinstance(call.func, ast.Name) o…`分支；L78抛异常，停止当前正常路径；L80按`isinstance(node, ast.Return)`分支。后续分支沿下方源码相同行号继续阅读。 调用`UnsafeRule`、`isinstance`、`self._expression`、`self._statements`、`len`、`type`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `Rules._expression`（L96–L143）：接收`node`、`depth`。 控制顺序：L97按`depth > 25`分支；L98抛异常，停止当前正常路径；L100按`isinstance(node, ast.Constant)`分支；L101按`type(node.value) not in {str, int, bool, type(None)}`分支；L102抛异常，停止当前正常路径；L103按`isinstance(node.value, str) and len(node.value) > 2000`分支；L104抛异常，停止当前正常路径；L105按`type(node.value) is int and abs(node.value) > 10**18`分支。后续分支沿下方源码相同行号继续阅读。 调用`UnsafeRule`、`isinstance`、`type`、`len`、`abs`、`all`、`self._expression`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `Rules.validate`（L145–L150）：接收`entity`、`data`。 控制顺序：L150抛异常，停止当前正常路径。 调用`self._run`、`ValueError`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `Rules._run`（L152–L162）：接收`body`、`env`。 控制顺序：L153遍历`body`；L154按`isinstance(node, ast.If)`分支；L156按`self._run(branch, env)`分支；L158按`isinstance(node, ast.Raise)`分支；L159抛异常，停止当前正常路径；L160按`isinstance(node, ast.Return)`分支。 调用`isinstance`、`self._eval`、`self._run`、`ValueError`。 返回路径：L157的`True`；L161的`True`；L162的`False`。
- `Rules._eval`（L164–L190）：接收`node`、`env`。 控制顺序：L165按`isinstance(node, ast.Constant)`分支；L167按`isinstance(node, ast.Name)`分支；L169按`isinstance(node, (ast.List, ast.Tuple))`分支；L171按`isinstance(node, ast.Subscript)`分支；L173按`isinstance(node, ast.Call)`分支；L176按`isinstance(node, ast.UnaryOp)`分支；L179按`isinstance(node, ast.BoolOp)`分支；L182按`isinstance(node, ast.Compare)`分支。后续分支沿下方源码相同行号继续阅读。 调用`isinstance`、`self._eval`、`len`、`env["data"].get`、`all`、`any`、`zip`、`OPS[type(op)]`、`type`等。 返回路径：L166的`node.value`；L168的`env[node.id]`；L170的`[self._eval(x, env) for x in node.elts]`。

</details>

**创建路径：** `workbench/rules.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L190。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`7812`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/rules.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "8fc135f9689c08bfcfafa8a627b198a09812e29bba78b8f13c4cdda6cfc812ef"} -->
````python
# workbench/rules.py
"""A small Python-shaped rule interpreter. Model-authored files are NEVER imported/exec'ed.

Allowed: validate(entity, data), if, boolean/comparison expressions, data.get,
len, literals and raise ValueError. No imports, assignment, loops or arbitrary calls.
"""

import ast
import operator


class UnsafeRule(ValueError):
    pass


OPS = {
    ast.Eq: operator.eq,
    ast.NotEq: operator.ne,
    ast.Gt: operator.gt,
    ast.GtE: operator.ge,
    ast.Lt: operator.lt,
    ast.LtE: operator.le,
    ast.In: lambda a, b: a in b,
    ast.NotIn: lambda a, b: a not in b,
    ast.Is: operator.is_,
    ast.IsNot: operator.is_not,
}


class Rules:
    def __init__(self, source):
        if len(source) > 30000:
            raise UnsafeRule("规则文件过大")
        tree = ast.parse(source)
        if len(list(ast.walk(tree))) > 400:
            raise UnsafeRule("规则复杂度超限")
        if len(tree.body) != 1 or not isinstance(tree.body[0], ast.FunctionDef):
            raise UnsafeRule("只能定义一个 validate(entity, data) 函数")
        fn = tree.body[0]
        args = fn.args
        if (
            fn.name != "validate"
            or [a.arg for a in args.args] != ["entity", "data"]
            or args.defaults
            or args.kw_defaults
            or args.kwonlyargs
            or args.posonlyargs
            or args.vararg
            or args.kwarg
            or fn.decorator_list
            or fn.returns
            or any(a.annotation for a in args.args)
            or fn.type_params
        ):
            raise UnsafeRule("规则函数签名无效")
        self.body = fn.body
        self._statements(fn.body, 0)

    def _statements(self, body, depth):
        if depth > 20:
            raise UnsafeRule("规则嵌套过深")
        for node in body:
            if isinstance(node, ast.If):
                self._expression(node.test, depth + 1)
                self._statements(node.body, depth + 1)
                self._statements(node.orelse, depth + 1)
            elif isinstance(node, ast.Raise):
                call = node.exc
                if (
                    node.cause
                    or not isinstance(call, ast.Call)
                    or not isinstance(call.func, ast.Name)
                    or call.func.id != "ValueError"
                    or len(call.args) != 1
                    or call.keywords
                    or not isinstance(call.args[0], ast.Constant)
                    or not isinstance(call.args[0].value, str)
                ):
                    raise UnsafeRule("只能抛出 ValueError(固定文本)")
                self._expression(call.args[0], depth + 1)
            elif isinstance(node, ast.Return):
                if node.value and not (
                    isinstance(node.value, ast.Constant) and node.value.value is None
                ):
                    raise UnsafeRule("规则只能返回 None")
            elif isinstance(node, ast.Pass):
                continue
            elif (
                isinstance(node, ast.Expr)
                and isinstance(node.value, ast.Constant)
                and isinstance(node.value.value, str)
            ):
                self._expression(node.value, depth + 1)
            else:
                raise UnsafeRule(f"不支持的规则语句: {type(node).__name__}")

    def _expression(self, node, depth):
        if depth > 25:
            raise UnsafeRule("规则表达式过深")
        children = []
        if isinstance(node, ast.Constant):
            if type(node.value) not in {str, int, bool, type(None)}:
                raise UnsafeRule("不支持的常量")
            if isinstance(node.value, str) and len(node.value) > 2000:
                raise UnsafeRule("规则常量过长")
            if type(node.value) is int and abs(node.value) > 10**18:
                raise UnsafeRule("规则数值过大")
        elif isinstance(node, ast.Name) and node.id in {"entity", "data"}:
            pass
        elif isinstance(node, (ast.List, ast.Tuple)) and len(node.elts) <= 50:
            children = node.elts
        elif isinstance(node, ast.Compare) and all(type(o) in OPS for o in node.ops):
            children = [node.left, *node.comparators]
        elif isinstance(node, ast.BoolOp) and isinstance(node.op, (ast.And, ast.Or)):
            children = node.values
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.Not, ast.USub)):
            children = [node.operand]
        elif (
            isinstance(node, ast.Subscript)
            and isinstance(node.value, ast.Name)
            and node.value.id == "data"
        ):
            if not isinstance(node.slice, ast.Constant) or not isinstance(node.slice.value, str):
                raise UnsafeRule("data 下标必须是固定字段名")
            children = [node.slice]
        elif isinstance(node, ast.Call) and not node.keywords:
            if isinstance(node.func, ast.Name) and node.func.id == "len" and len(node.args) == 1:
                children = node.args
            elif (
                isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "data"
                and node.func.attr == "get"
                and 1 <= len(node.args) <= 2
                and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, str)
            ):
                children = node.args
            else:
                raise UnsafeRule("不允许调用此函数")
        else:
            raise UnsafeRule(f"不支持的规则表达式: {type(node).__name__}")
        for child in children:
            self._expression(child, depth + 1)

    def validate(self, entity, data):
        env = {"entity": entity, "data": data}
        try:
            self._run(self.body, env)
        except (TypeError, KeyError, IndexError, OverflowError) as exc:
            raise ValueError("规则与字段类型不匹配") from exc

    def _run(self, body, env):
        for node in body:
            if isinstance(node, ast.If):
                branch = node.body if self._eval(node.test, env) else node.orelse
                if self._run(branch, env):
                    return True
            elif isinstance(node, ast.Raise):
                raise ValueError(node.exc.args[0].value)
            elif isinstance(node, ast.Return):
                return True
        return False

    def _eval(self, node, env):
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.Name):
            return env[node.id]
        if isinstance(node, (ast.List, ast.Tuple)):
            return [self._eval(x, env) for x in node.elts]
        if isinstance(node, ast.Subscript):
            return env["data"][node.slice.value]
        if isinstance(node, ast.Call):
            args = [self._eval(x, env) for x in node.args]
            return len(args[0]) if isinstance(node.func, ast.Name) else env["data"].get(*args)
        if isinstance(node, ast.UnaryOp):
            value = self._eval(node.operand, env)
            return not value if isinstance(node.op, ast.Not) else -value
        if isinstance(node, ast.BoolOp):
            values = (self._eval(x, env) for x in node.values)
            return all(values) if isinstance(node.op, ast.And) else any(values)
        if isinstance(node, ast.Compare):
            left = self._eval(node.left, env)
            for op, right_node in zip(node.ops, node.comparators, strict=True):
                right = self._eval(right_node, env)
                if not OPS[type(op)](left, right):
                    return False
                left = right
            return True
        raise UnsafeRule("不支持的表达式")
````
