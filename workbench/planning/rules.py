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
