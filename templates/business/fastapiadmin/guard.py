from fastapi import HTTPException


async def block_generated_crud():
    """All methods, including import/export/batch, must use audited policy endpoints."""
    raise HTTPException(403, "Use the business workflow API")
