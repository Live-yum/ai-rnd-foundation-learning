from workbench.domain import Entity
from workbench.native_acceptance import invalid_record


def test_optional_only_entity_uses_type_constraint_without_inventing_required_field():
    entity = Entity(
        name="review",
        description="评审",
        fields=[{"name": "score", "kind": "integer", "required": False}],
    )
    value, kind = invalid_record(entity, {"score": 7}, "fastapiadmin")
    assert value == {"score": {"invalid_scalar": True}}
    assert kind == "type"
    assert entity.fields[0].required is False


def test_boolean_only_entity_is_supported_by_acceptance_sampler():
    entity = Entity(
        name="review", description="评审", fields=[{"name": "approved", "kind": "boolean"}]
    )
    value, kind = invalid_record(entity, {"approved": True}, "fastapiadmin")
    assert kind == "type" and value["approved"] == {"invalid_scalar": True}
