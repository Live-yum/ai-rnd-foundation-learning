"""Declarative business behavior: no SQL, executable scripts or claimed support flags."""

from datetime import date, datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, JsonValue, model_validator

Name = Annotated[str, Field(pattern=r"^[a-z][a-z0-9_]{0,39}$")]
Action = Literal[
    "create",
    "read",
    "update",
    "archive",
    "assign",
    "transition",
    "add_note",
    "read_history",
    "read_audit",
    "read_metrics",
]
SYSTEM_FIELDS = {
    "id": "text",
    "created_by": "text",
    "created_at": "datetime",
    "updated_at": "datetime",
    "archived_at": "datetime",
}


class BusinessContract(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class BusinessRole(BusinessContract):
    name: Name
    label: str = Field(min_length=1, max_length=100)


class BusinessRegistration(BusinessContract):
    enabled: bool = False
    default_role: Name


class BusinessResource(BusinessContract):
    entity: Name
    assignee_field: Name | None = None
    archive: Literal[True] = True
    notes: bool = True
    audit: Literal[True] = True


class RelationSpec(BusinessContract):
    entity: Name
    field: Name
    target_entity: Name | Literal["$users"]
    on_delete: Literal["restrict"] = "restrict"


class PermissionSpec(BusinessContract):
    role: Name
    entity: Name
    actions: list[Action] = Field(min_length=1, max_length=10)
    scope: Literal["all", "own", "assigned"]


class TransitionSpec(BusinessContract):
    name: Name
    label: str = Field(default="", max_length=100)
    from_states: list[str] = Field(min_length=1, max_length=50)
    to_state: str = Field(min_length=1, max_length=200)
    roles: list[Name] = Field(min_length=1, max_length=20)
    set_timestamp: Name | None = None


class WorkflowSpec(BusinessContract):
    entity: Name
    status_field: Name
    initial: str = Field(min_length=1, max_length=200)
    transitions: list[TransitionSpec] = Field(min_length=1, max_length=50)


class NotificationSpec(BusinessContract):
    entity: Name
    event: Literal["created", "assigned", "transitioned", "note_added", "due"]
    recipient: Literal["creator", "assignee"]
    transition: Name | None = Field(
        default=None,
        description=(
            "For event=transitioned this must name an existing transition in the same entity's "
            "workflow, never null or a wildcard. An all-state-changes requirement needs one "
            "notification per named transition and recipient. Other events require null."
        ),
    )
    due_field: Name | None = Field(
        default=None,
        description="For event=due name an optional date/datetime field on this entity; other events require null.",
    )
    channel: Literal["in_app"] = "in_app"


class MetricPredicate(BusinessContract):
    field: Name
    op: Literal["eq", "ne", "in", "gte", "lte"] = "eq"
    value: JsonValue


class MetricSpec(BusinessContract):
    name: Name
    label: str = Field(min_length=1, max_length=100)
    entity: Name
    kind: Literal["count", "average_duration", "group_count", "time_count"]
    group_by: Name | None = None
    start_field: Name | None = None
    end_field: Name | None = None
    time_field: Name | None = None
    filters: list[MetricPredicate] = Field(default_factory=list, max_length=12)
    unit: Literal["seconds"] = "seconds"
    bucket: Literal["day"] = "day"
    timezone: Literal["UTC"] = "UTC"


class BusinessSpec(BusinessContract):
    """Own means immutable created_by; assigned means resource.assignee_field.

    Permissions are grant-only and one row per role/resource; no implicit grants.
    Every mutation emits server-authored audit/history in its transaction. Archive
    retains references/history. Metrics use the caller's read_metrics row scope;
    average_duration excludes missing endpoints and returns null for zero samples.
    In-app events are deduplicated by source event and recipient; read state is
    private to that recipient. UTC daily buckets and duration seconds are fixed.
    """

    roles: list[BusinessRole] = Field(min_length=1, max_length=20)
    registration: BusinessRegistration
    bootstrap_role: Name
    role_admin_roles: list[Name] = Field(min_length=1, max_length=20)
    resources: list[BusinessResource] = Field(min_length=1, max_length=8)
    relations: list[RelationSpec] = Field(default_factory=list, max_length=64)
    permissions: list[PermissionSpec] = Field(min_length=1, max_length=160)
    workflows: list[WorkflowSpec] = Field(default_factory=list, max_length=8)
    notifications: list[NotificationSpec] = Field(default_factory=list, max_length=64)
    metrics: list[MetricSpec] = Field(default_factory=list, max_length=40)

    @model_validator(mode="after")
    def unique_declarations(self):
        collections = [
            (self.roles, lambda x: x.name),
            (self.resources, lambda x: x.entity),
            (self.relations, lambda x: (x.entity, x.field)),
            (self.permissions, lambda x: (x.role, x.entity)),
            (self.workflows, lambda x: x.entity),
            (self.metrics, lambda x: x.name),
            (
                self.notifications,
                lambda x: (x.entity, x.event, x.recipient, x.transition, x.due_field),
            ),
        ]
        for items, key in collections:
            if len({key(item) for item in items}) != len(items):
                raise ValueError("Duplicate/contradictory business declaration")
        for permission in self.permissions:
            if len(set(permission.actions)) != len(permission.actions):
                raise ValueError("Duplicate permission action")
        return self

    def validate_plan(self, plan):
        entities = {entity.name: entity for entity in plan.entities}
        if set(entities) & {
            "business_audit",
            "business_notes",
            "business_notifications",
            "business_setup",
        }:
            raise ValueError("Entity conflicts with reserved business runtime tables")
        resources = {resource.entity: resource for resource in self.resources}
        roles = {role.name for role in self.roles}
        if self.registration.default_role not in roles or self.bootstrap_role not in roles:
            raise ValueError("Registration/bootstrap role must be declared")
        if (
            len(set(self.role_admin_roles)) != len(self.role_admin_roles)
            or not set(self.role_admin_roles) <= roles
            or self.bootstrap_role not in self.role_admin_roles
        ):
            raise ValueError("Role administrators must be declared and include bootstrap role")
        if self.registration.default_role in self.role_admin_roles:
            raise ValueError("Self-registration cannot grant role administration")
        if set(resources) != set(entities):
            raise ValueError("Every business entity must declare exactly one resource policy")
        if plan.data_scope != "shared":
            raise ValueError("Business roles require shared data with explicit row scopes")
        for entity in entities.values():
            if any(field.name in SYSTEM_FIELDS for field in entity.fields):
                raise ValueError("Business system fields are immutable and cannot be redeclared")

        def field(entity, name):
            if entity not in entities:
                raise ValueError("Unknown business entity: " + entity)
            found = next((item for item in entities[entity].fields if item.name == name), None)
            if found is None:
                raise ValueError("Unknown business field: " + entity + "." + name)
            return found

        def kind(entity, name):
            return SYSTEM_FIELDS[name] if name in SYSTEM_FIELDS else field(entity, name).kind

        def timestamp(entity, name):
            if name is None or kind(entity, name) != "datetime":
                raise ValueError("Business timestamp must name a datetime field")

        relations = {(relation.entity, relation.field): relation for relation in self.relations}
        for relation in self.relations:
            if field(relation.entity, relation.field).kind != "text":
                raise ValueError("Relation keys must use wire-normalized text identifiers")
            if relation.target_entity != "$users" and relation.target_entity not in entities:
                raise ValueError("Unknown relation target")
        for resource in self.resources:
            if resource.assignee_field:
                relation = relations.get((resource.entity, resource.assignee_field))
                if not relation or relation.target_entity != "$users":
                    raise ValueError("Assignee must reference authenticated users")
                if field(resource.entity, resource.assignee_field).required:
                    raise ValueError("Assignee must be nullable until an authorized assignment")
        grants = {}
        for permission in self.permissions:
            if permission.role not in roles or permission.entity not in resources:
                raise ValueError("Unknown permission role/resource")
            resource = resources[permission.entity]
            if (
                permission.scope == "assigned" or "assign" in permission.actions
            ) and not resource.assignee_field:
                raise ValueError("Assigned policy requires an assignee relation")
            if "add_note" in permission.actions and not resource.notes:
                raise ValueError("Notes permission contradicts disabled notes")
            grants[permission.role, permission.entity] = set(permission.actions)
        workflows = {workflow.entity: workflow for workflow in self.workflows}
        for permission in self.permissions:
            if "transition" in permission.actions and permission.entity not in workflows:
                raise ValueError("Transition permission requires a workflow")
        for workflow in self.workflows:
            status = field(workflow.entity, workflow.status_field)
            if (
                status.kind != "enum"
                or not status.required
                or workflow.initial not in status.choices
            ):
                raise ValueError("Workflow requires a required enum status and valid initial value")
            if len({item.name for item in workflow.transitions}) != len(workflow.transitions):
                raise ValueError("Duplicate transition name")
            for transition in workflow.transitions:
                if (
                    len(set(transition.from_states)) != len(transition.from_states)
                    or not set(transition.from_states) <= set(status.choices)
                    or transition.to_state not in status.choices
                ):
                    raise ValueError("Transition references invalid/duplicate states")
                if transition.to_state in transition.from_states:
                    raise ValueError("Transition cannot be a no-op")
                if (
                    len(set(transition.roles)) != len(transition.roles)
                    or not set(transition.roles) <= roles
                ):
                    raise ValueError("Transition references invalid/duplicate roles")
                if any(
                    "transition" not in grants.get((role, workflow.entity), set())
                    for role in transition.roles
                ):
                    raise ValueError("Transition role lacks explicit resource permission")
                if transition.set_timestamp:
                    target = field(workflow.entity, transition.set_timestamp)
                    if target.kind != "datetime" or target.required:
                        raise ValueError("Transition timestamp must be nullable datetime")
        for notification in self.notifications:
            if notification.entity not in resources:
                raise ValueError("Unknown notification entity")
            if notification.event == "note_added" and not resources[notification.entity].notes:
                raise ValueError("Note notification requires enabled notes")
            if (
                notification.recipient == "assignee" or notification.event == "assigned"
            ) and not resources[notification.entity].assignee_field:
                raise ValueError("Assignment notification requires assignee relation")
            if notification.event == "transitioned":
                workflow = workflows.get(notification.entity)
                if not workflow or notification.transition not in {
                    item.name for item in workflow.transitions
                }:
                    raise ValueError("Notification requires a known transition")
            elif notification.transition is not None:
                raise ValueError("Transition selector only applies to transitioned events")
            if notification.event == "due":
                timestamp(notification.entity, notification.due_field)
            elif notification.due_field is not None:
                raise ValueError("Due field only applies to due events")
        for metric in self.metrics:
            if metric.entity not in resources:
                raise ValueError("Unknown metric resource")
            expected = {
                "count": set(),
                "average_duration": {"start_field", "end_field"},
                "group_count": {"group_by"},
                "time_count": {"time_field"},
            }[metric.kind]
            actual = {
                name
                for name in ("group_by", "start_field", "end_field", "time_field")
                if getattr(metric, name) is not None
            }
            if actual != expected:
                raise ValueError("Metric parameters contradict its kind")
            for name in expected - {"group_by"}:
                timestamp(metric.entity, getattr(metric, name))
            if metric.group_by:
                kind(metric.entity, metric.group_by)
            if metric.kind == "average_duration" and metric.start_field == metric.end_field:
                raise ValueError("Duration endpoints must differ")
            for predicate in metric.filters:
                value_kind = kind(metric.entity, predicate.field)
                values = predicate.value if predicate.op == "in" else [predicate.value]
                if not isinstance(values, list) or not values or len(values) > 50:
                    raise ValueError("Metric in requires a bounded nonempty list")
                for value in values:
                    if value is None and predicate.op in {"eq", "ne"}:
                        continue
                    expected_type = {"integer": int, "boolean": bool}.get(value_kind, str)
                    if type(value) is not expected_type:
                        raise ValueError("Metric predicate value type mismatch")
                    if value_kind == "boolean" and predicate.op in {"gte", "lte"}:
                        raise ValueError("Boolean metric predicates cannot be ordered")
                    if (
                        value_kind == "enum"
                        and value not in field(metric.entity, predicate.field).choices
                    ):
                        raise ValueError("Metric predicate references invalid enum value")
                    if value_kind == "date":
                        date.fromisoformat(value)
                    if value_kind == "datetime":
                        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
                        if parsed.tzinfo is None:
                            raise ValueError("Metric datetime must include timezone")
        return self
