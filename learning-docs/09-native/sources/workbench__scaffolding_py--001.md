# workbench/scaffolding.py · 1/1

[阶段导读](../README.md) · [本阶段文件顺序](../files.md) · [全部文件索引](../../source-index.md)



**作用：用真实Plop接入受限业务规则。** 从批准Plan和已生成原生模块计算白名单路径、精确锚点及模板参数；先在临时目录调用node-plop，再核对实际新增和修改文件，最后写回。失败恢复已有文件，模型不能提供自己的生成脚本。

**对应关系：** native_coding → scaffolding → tools/node/plop-runner.mjs → 真实原生Python/Java/Vue规则入口；test_native_tools。

**如何编写：** 按页码把同名文件各段依次拼接。只去掉每个代码块第一行的路径注释；不要复制围栏。L行号指最终源文件，不含新增的路径注释。

**先有这些模块：** `workbench.domain`、`workbench.filesystem`、`workbench.native_acceptance`、`workbench.settings`、`workbench.tools`。导入名称对应同名目录/文件；仅定义函数的模块通常在调用时才执行其业务。

<details>
<summary>可选：本段符号与行号索引（用于定位，不必逐项阅读）</summary>

- `class_name`（L15–L16）：接收`entity`。 调用`"".join`、`part.title`、`entity.name.split`。 返回路径：L16的`"".join(part.title() for part in entity.name.split("_"))`。
- `specification`（L19–L139）：接收`template`、`plan`、`product`。 控制顺序：L30遍历`plan.custom_rules`；L33按`template == "fastapiadmin"`分支；L61按`template == "yudao-vben"`分支；L82按`not body.rstrip().endswith("}")`分支；L83抛异常，停止当前正常路径；L107抛异常，停止当前正常路径；L127按`not marker`分支；L128抛异常，停止当前正常路径。 调用`Path`、`next`、`class_name`、`add`、`inside(product, schema).read_text`、`inside`、`modify`、`entity.name.replace`、`package.replace`等。 返回路径：L134的`{ "template": template, "spec_digest": digest(plan.model_dump()), "actions": actions, "edi…`。
- `specification.add`（L23–L25）：接收`path`、`template_file`、`data`。 调用`actions.append`、`editable.append`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `specification.modify`（L27–L28）：接收`path`、`before`、`after`。 调用`actions.append`。没有显式返回业务值；主要效果是上面的校验、写入、调用或异常。
- `scaffold_native_rules`（L142–L212）：接收`template`、`plan`、`product`、`reports`。 控制顺序：L145按`receipt_path.is_file()`分支；L147按`receipt["spec_digest"] != digest(plan.model_dump())`分支；L148抛异常，停止当前正常路径；L149遍历`receipt["editable"]`；L158遍历`spec["actions"]`；L159按`action["type"] == "modify"`分支；L163按`inside(product, action["path"]).exists()`分支；L164抛异常，停止当前正常路径。后续分支沿下方源码相同行号继续阅读。 调用`Path`、`receipt_path.is_file`、`json.loads`、`receipt_path.read_text`、`digest`、`plan.model_dump`、`ValueError`、`inside(product, name).read_text`、`inside`等。 返回路径：L151的`receipt`；L212的`receipt`。

</details>

**创建路径：** `workbench/scaffolding.py`；**本文件共有 1 段**。本段覆盖源文件 L1–L212。第一行路径注释仅供教材定位，保存时删这一行；下方原有注释、shebang和空行全部保留。

本段原始字节数：`9025`。本段原文以LF换行结束。

<!-- learning-source: {"path": "workbench/scaffolding.py", "part": 1, "parts": 1, "encoding": "utf-8", "sha256": "a9c5ed3bf20a780936461d150216c0c5344fcbf81cc14aafacb54bb708982668"} -->
````python
# workbench/scaffolding.py
"""Actual local Plop, before bounded native editing; never executes a model plopfile."""

import json
import shutil
import tempfile
from pathlib import Path

from workbench.domain import digest
from workbench.filesystem import atomic_text, inside, manifest, sha, write_json
from workbench.native_acceptance import wire_name
from workbench.settings import ROOT
from workbench.tools import run_command


def class_name(entity):
    return "".join(part.title() for part in entity.name.split("_"))


def specification(template, plan, product):
    actions, editable = [], []
    product = Path(product)

    def add(path, template_file, data=None):
        actions.append({"type": "add", "path": path, "template": template_file, "data": data or {}})
        editable.append(path)

    def modify(path, before, after):
        actions.append({"type": "modify", "path": path, "before": before, "after": after})

    for rule in plan.custom_rules:
        entity = next(e for e in plan.entities if e.name == rule.entity)
        name = class_name(entity)
        if template == "fastapiadmin":
            module = "backend/app/plugin/module_rnd/" + entity.name
            helper = module + "/business_rules.py"
            add(helper, "rule.py.hbs")
            schema = module + "/schema.py"
            body = inside(product, schema).read_text(encoding="utf-8")
            prefix = "from pydantic import model_validator\nfrom .business_rules import valid as rnd_business_valid\n"
            modify(schema, body, prefix + body)
            check = (
                '    @model_validator(mode="after")\n'
                "    def rnd_business_check(self):\n"
                "        if not rnd_business_valid(self.model_dump()):\n"
                '            raise ValueError("RND_BUSINESS_RULE")\n'
                "        return self\n\n\n"
            )
            modify(
                schema, "class " + name + "UpdateSchema", check + "class " + name + "UpdateSchema"
            )
            modify(schema, "class " + name + "OutSchema", check + "class " + name + "OutSchema")
            front = "frontend/web/src/views/module_rnd/" + entity.name
            form = front + "/index.vue"
            anchor = "async function handleSubmit() {"
            modify(
                form,
                anchor,
                anchor
                + '\n  if (!rndBusinessValid(formData.value as unknown as Record<string, unknown>)) { ElMessage.error("RND_BUSINESS_RULE"); return; }',
            )
        elif template == "yudao-vben":
            slug, name = "wb" + entity.name.replace("_", ""), "Wb" + name
            package = "cn.iocoder.yudao.module.infra.controller.admin." + slug + ".vo"
            module = (
                "backend/yudao-module-infra/yudao-module-infra-server/src/main/java/"
                + package.replace(".", "/")
            )
            helper = module + "/" + name + "BusinessRules.java"
            parameters = ", ".join(
                {"text": "String", "integer": "Integer", "boolean": "Boolean"}[f.kind]
                + " "
                + wire_name(template, f.name)
                for f in entity.fields
            )
            add(
                helper,
                "rule.java.hbs",
                {"package": package, "className": name, "parameters": parameters},
            )
            schema = module + "/" + name + "SaveReqVO.java"
            body = inside(product, schema).read_text(encoding="utf-8")
            if not body.rstrip().endswith("}"):
                raise ValueError("Native VO shape changed")
            arguments = ", ".join(
                "get"
                + wire_name(template, f.name)[:1].upper()
                + wire_name(template, f.name)[1:]
                + "()"
                for f in entity.fields
            )
            method = (
                '\n    @jakarta.validation.constraints.AssertTrue(message = "RND_BUSINESS_RULE")\n'
                "    @com.fasterxml.jackson.annotation.JsonIgnore\n"
                "    public boolean isRndBusinessValid() {\n"
                f"        return {name}BusinessRules.valid({arguments});\n    }}\n}}\n"
            )
            modify(schema, body, body.rstrip()[:-1] + method)
            front = "frontend-product/apps/web-antd/src/views/infra/" + slug + "/modules"
            form = front + "/form.vue"
            anchor = "    try {\n      await (formData.value?.id ?"
            modify(
                form,
                anchor,
                '    try {\n      if (!rndBusinessValid(data as unknown as Record<string, unknown>)) { message.error("RND_BUSINESS_RULE"); return; }\n      await (formData.value?.id ?',
            )
        else:
            raise ValueError("No native Plop template")
        component = front + "/business-rules.vue"
        encoded = (
            json.dumps(rule.description, ensure_ascii=True)
            .replace("<", "\\u003c")
            .replace(">", "\\u003e")
        )
        add(component, "rule.vue.hbs", {"descriptionJson": encoded})
        mount = "        <FaForm" if template == "fastapiadmin" else '  <Modal :title="getTitle">'
        replacement = (
            "        <RndBusinessRule />\n        <FaForm"
            if template == "fastapiadmin"
            else mount + "\n    <RndBusinessRule />"
        )
        modify(form, mount, replacement)
        body = inside(product, form).read_text(encoding="utf-8")
        marker = next(
            (line for line in body.splitlines() if line.startswith("<script") and "setup" in line),
            "",
        )
        if not marker:
            raise ValueError("Native Vue setup script not found")
        modify(
            form,
            marker,
            marker + '\nimport RndBusinessRule, { rndBusinessValid } from "./business-rules.vue";',
        )
    return {
        "template": template,
        "spec_digest": digest(plan.model_dump()),
        "actions": actions,
        "editable": editable,
    }


def scaffold_native_rules(template, plan, product, reports):
    product, reports = Path(product), Path(reports)
    receipt_path = reports / "plop.json"
    if receipt_path.is_file():
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        if receipt["spec_digest"] != digest(plan.model_dump()):
            raise ValueError("Plop receipt belongs to another approved plan")
        for name in receipt["editable"]:
            inside(product, name).read_text(encoding="utf-8")
        return receipt
    spec = specification(template, plan, product)
    before = manifest(product)
    with tempfile.TemporaryDirectory(prefix="rnd-plop-") as directory:
        root = Path(directory)
        work = root / "work"
        work.mkdir()
        for action in spec["actions"]:
            if action["type"] == "modify":
                target = inside(work, action["path"])
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(inside(product, action["path"]), target)
            elif inside(product, action["path"]).exists():
                raise FileExistsError("Plop refuses to overwrite an existing business file")
        request = root / "request.json"
        write_json(request, spec)
        result = run_command(
            [
                "node",
                "--require",
                str(ROOT / "tools/node/no-network.cjs"),
                str(ROOT / "tools/node/plop-runner.mjs"),
                str(request),
                str(work),
            ],
            ROOT,
            60,
        )
        if manifest(product) != before:
            raise ValueError("Product changed during Plop generation")
        paths = sorted({item["path"] for item in spec["actions"]})
        generated = {name: inside(work, name).read_text(encoding="utf-8") for name in paths}
        if set(manifest(work)) != set(paths):
            raise ValueError("Plop emitted an unexpected file")
        originals = {
            name: inside(product, name).read_bytes() if inside(product, name).is_file() else None
            for name in paths
        }
        written = []
        try:
            for name, body in generated.items():
                atomic_text(inside(product, name), body)
                written.append(name)
        except BaseException:
            for name in reversed(written):
                if originals[name] is None:
                    inside(product, name).unlink()
                else:
                    atomic_text(inside(product, name), originals[name].decode("utf-8"))
            raise
    receipt = {
        "engine": "node-plop",
        "version": "0.32.3",
        "network": "disabled",
        "spec_digest": spec["spec_digest"],
        "editable": spec["editable"],
        "files": {name: sha(inside(product, name)) for name in paths},
        "actions": len(spec["actions"]),
        "log": result["log"][-2000:],
    }
    write_json(receipt_path, receipt)
    return receipt
````
