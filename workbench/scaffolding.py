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
                "    @model_validator(mode=\"after\")\n"
                "    def rnd_business_check(self):\n"
                "        if not rnd_business_valid(self.model_dump()):\n"
                "            raise ValueError(\"RND_BUSINESS_RULE\")\n"
                "        return self\n\n\n"
            )
            modify(schema, "class " + name + "UpdateSchema", check + "class " + name + "UpdateSchema")
            modify(schema, "class " + name + "OutSchema", check + "class " + name + "OutSchema")
            front = "frontend/web/src/views/module_rnd/" + entity.name
            form = front + "/index.vue"
            anchor = "async function handleSubmit() {"
            modify(form, anchor, anchor + '\n  if (!rndBusinessValid(formData.value as unknown as Record<string, unknown>)) { ElMessage.error("RND_BUSINESS_RULE"); return; }')
        elif template == "yudao-vben":
            slug, name = "wb" + entity.name.replace("_", ""), "Wb" + name
            package = "cn.iocoder.yudao.module.infra.controller.admin." + slug + ".vo"
            module = "backend/yudao-module-infra/yudao-module-infra-server/src/main/java/" + package.replace(".", "/")
            helper = module + "/" + name + "BusinessRules.java"
            parameters = ", ".join({"text": "String", "integer": "Integer", "boolean": "Boolean"}[f.kind] + " " + wire_name(template, f.name) for f in entity.fields)
            add(helper, "rule.java.hbs", {"package": package, "className": name, "parameters": parameters})
            schema = module + "/" + name + "SaveReqVO.java"
            body = inside(product, schema).read_text(encoding="utf-8")
            if not body.rstrip().endswith("}"):
                raise ValueError("Native VO shape changed")
            arguments = ", ".join("get" + wire_name(template, f.name)[:1].upper() + wire_name(template, f.name)[1:] + "()" for f in entity.fields)
            method = ('\n    @jakarta.validation.constraints.AssertTrue(message = "RND_BUSINESS_RULE")\n'
                      '    @com.fasterxml.jackson.annotation.JsonIgnore\n'
                      '    public boolean isRndBusinessValid() {\n'
                      f'        return {name}BusinessRules.valid({arguments});\n    }}\n}}\n')
            modify(schema, body, body.rstrip()[:-1] + method)
            front = "frontend-product/apps/web-antd/src/views/infra/" + slug + "/modules"
            form = front + "/form.vue"
            anchor = "    try {\n      await (formData.value?.id ?"
            modify(form, anchor, '    try {\n      if (!rndBusinessValid(data as unknown as Record<string, unknown>)) { message.error("RND_BUSINESS_RULE"); return; }\n      await (formData.value?.id ?')
        else:
            raise ValueError("No native Plop template")
        component = front + "/business-rules.vue"
        encoded = json.dumps(rule.description, ensure_ascii=True).replace("<", "\\u003c").replace(">", "\\u003e")
        add(component, "rule.vue.hbs", {"descriptionJson": encoded})
        mount = "        <FaForm" if template == "fastapiadmin" else '  <Modal :title="getTitle">'
        replacement = "        <RndBusinessRule />\n        <FaForm" if template == "fastapiadmin" else mount + "\n    <RndBusinessRule />"
        modify(form, mount, replacement)
        body = inside(product, form).read_text(encoding="utf-8")
        marker = next((line for line in body.splitlines() if line.startswith("<script") and "setup" in line), "")
        if not marker:
            raise ValueError("Native Vue setup script not found")
        modify(form, marker, marker + '\nimport RndBusinessRule, { rndBusinessValid } from "./business-rules.vue";')
    return {"template": template, "spec_digest": digest(plan.model_dump()), "actions": actions, "editable": editable}


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
        result = run_command([
            "node", "--require", str(ROOT / "tools/node/no-network.cjs"),
            str(ROOT / "tools/node/plop-runner.mjs"), str(request), str(work),
        ], ROOT, 60)
        if manifest(product) != before:
            raise ValueError("Product changed during Plop generation")
        paths = sorted({item["path"] for item in spec["actions"]})
        generated = {name: inside(work, name).read_text(encoding="utf-8") for name in paths}
        if set(manifest(work)) != set(paths):
            raise ValueError("Plop emitted an unexpected file")
        originals = {name: inside(product, name).read_bytes() if inside(product, name).is_file() else None for name in paths}
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
        "engine": "node-plop", "version": "0.32.3", "network": "disabled",
        "spec_digest": spec["spec_digest"], "editable": spec["editable"],
        "files": {name: sha(inside(product, name)) for name in paths}, "actions": len(spec["actions"]),
        "log": result["log"][-2000:],
    }
    write_json(receipt_path, receipt)
    return receipt
