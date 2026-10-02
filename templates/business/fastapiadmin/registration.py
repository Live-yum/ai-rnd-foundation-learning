"""Native registration extension: same session, native password/account validation."""

from sqlalchemy import select

from . import runtime as rt
from .model import BusinessEvent


async def before_registration(db):
    if not rt.SPEC["registration"]["enabled"]:
        rt.fail(403, "Business self-registration is disabled")
    marker = await db.scalar(
        select(BusinessEvent).where(BusinessEvent.source_key == "bootstrap").with_for_update()
    )
    if marker is None:
        rt.fail(409, "A native administrator must initialize this project first")


async def registration_completed(db, user_id):
    role = rt.SPEC["registration"]["default_role"]
    await rt.set_role(db, user_id, role)
    db.add(
        BusinessEvent(
            entity="roles",
            record_id=user_id,
            actor=user_id,
            event="joined",
            payload={"role": role},
        )
    )
    # Native user creation and restricted role membership are one atomic transaction.
    await db.commit()
