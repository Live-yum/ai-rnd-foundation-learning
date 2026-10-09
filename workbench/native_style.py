"""Keep generated pages inside the selected native frontend and its unchanged UI shell."""

from pathlib import Path

from workbench.domain import digest
from workbench.filesystem import manifest, write_json
from workbench.native_recovery import NativeIntegrityError
from workbench.symbols import parse_file
from workbench.template_adapters import get_adapter, template_ids

# Compatibility view; selection, planning and verification share one adapter.
PROFILES = {
    template: {
        "protected": list(get_adapter(template).ui.protected),
        "family": get_adapter(template).ui.family,
    }
    for template in template_ids()
    if get_adapter(template).ui.protected
}


def native_page_contracts(template, entities, business=False):
    adapter = get_adapter(template)
    if not adapter.ui.protected:
        raise ValueError("Native UI verification requires a registered native template")
    return adapter.ui.page_contracts(entities, business)


def verify_native_style(template, source_frontend, generated_frontend, plan, reports):
    """Source identity plus parsed component contracts, followed by browser UI checks.

    Source roots are the original pinned frontend and its generated copy, not
    project metadata labels. New entity pages may be added; shell/theme changes
    or substitution with a generic CRUD frontend are rejected.
    """
    if template not in PROFILES:
        raise ValueError("Native UI verification requires a registered native template")
    source_frontend, generated_frontend = Path(source_frontend), Path(generated_frontend)
    profile = PROFILES[template]
    before, after = manifest(source_frontend), manifest(generated_frontend)
    protected = {}
    for prefix in profile["protected"]:
        selected = {
            name: value
            for name, value in before.items()
            if name == prefix or (prefix.endswith("/") and name.startswith(prefix))
        }
        actual = {
            name: value
            for name, value in after.items()
            if name == prefix or (prefix.endswith("/") and name.startswith(prefix))
        }
        if not selected or selected != actual:
            raise NativeIntegrityError("Selected native UI shell/theme changed: " + prefix)
        protected.update(selected)
    pages = []
    required = native_page_contracts(
        template, [entity.name for entity in plan.entities], bool(getattr(plan, "business", None))
    )
    for relative, (components, imports) in required.items():
        path = generated_frontend / relative
        if not path.is_file():
            raise NativeIntegrityError("Native-generated UI page missing: " + relative)
        parsed = parse_file(path)
        actual = {
            row["name"] for row in parsed.get("symbols", []) if row["kind"] == "vue_component_usage"
        }
        import_text = "\n".join(parsed.get("imports", []))
        if not components <= actual or any(name not in import_text for name in imports):
            raise NativeIntegrityError("Generated page replaced native UI components: " + relative)
        pages.append(
            {
                "path": relative,
                "sha256": after[relative],
                "native_components": sorted(components),
                "native_imports": imports,
            }
        )
    evidence = {
        "passed": True,
        "template": template,
        "ui_family": profile["family"],
        "shell_and_theme_unchanged": True,
        "protected_files": protected,
        "protected_source_digest": digest(protected),
        "generated_pages": pages,
        "generic_frontend_substitution": False,
        "evidence_scope": "native source identity and parsed Vue components; browser evidence separate",
    }
    write_json(Path(reports) / "native-style.json", evidence)
    return evidence
