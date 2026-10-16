"""Persisted graph state. Legacy fields retain their names and meaning."""

from typing import TypedDict


class State(TypedDict, total=False):
    run_id: str
    template: str
    round: int
    requirement: dict
    requirement_source_count: int
    requirement_ledger: list[dict]
    requirement_analysis_diagnostics: list[dict]
    requirement_analysis_baseline: dict
    requirement_capability_conflicts: list[dict]
    requirement_intent_version: int
    resolution_feedback: dict
    plan: dict
    decision: str
    last_job_id: str
    attempt: int
    verification: dict
    delivery: dict
    status: str
    model_review: dict
    code_context: dict
    sandbox: dict
    native_generation: dict
    native_normalization: dict
    extension_requested_mode: bool
    extension_design: dict
    extension_scope: dict
    extension_errors: list[str]
    extension_completed: list[dict]
    extension_drafted: list[str]
    extension_attempt: int
    extension_candidate: str
    extension_product: str
    extension_baseline: dict
    extension_error: str
    extension_edit_receipt: dict
    extension_candidate_passed: bool
    extension_proof: dict
    extension_integration_attempt: int
    extension_policy: dict
    extension_aggregate_passed: bool
    extension_coverage: dict
    feature_requested_mode: bool
    feature_design: dict
