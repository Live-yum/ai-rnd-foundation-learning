"""Explicit deterministic model response for native integration acceptance, never live mode."""

from workbench.native_coding import NativeEdits, region


class NativeCodingFixture:
    def __init__(self, fail_first=True):
        self.calls = []
        self.fail_first = fail_first

    def complete(self, run_id, key, instruction, payload, schema):
        if schema is not NativeEdits:
            raise AssertionError(schema)
        self.calls.append(key)
        failed = self.fail_first and len(self.calls) == 1
        rows = []
        for name, data in payload["registered_files"].items():
            source = data["source"]
            prefix, expression, suffix = region(source)
            if failed:
                result = "True" if name.endswith(".py") else "true"
            elif name.endswith(".py"):
                result = 'data.get("quantity") is None or data["quantity"] >= 0'
            elif name.endswith(".java"):
                result = "quantity == null || quantity >= 0"
            else:
                result = "data.quantity == null || Number(data.quantity) >= 0"
            position = source.index("# RND_RULE_BEGIN") if name.endswith(".py") else source.index("// RND_RULE_BEGIN")
            before = source[source.rfind("\n", 0, position) + 1:]
            after = before.replace(expression, result, 1)
            rows.append({"path": name, "before_sha256": data["sha256"],
                         "blocks": f"{name}\n<<<<<<< SEARCH\n{before.rstrip()}\n=======\n{after.rstrip()}\n>>>>>>> REPLACE\n"})
        return schema(files=rows, explanation="Explicit local test fixture: nonnegative quantity")
