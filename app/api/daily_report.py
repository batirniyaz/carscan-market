from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.database import get_async_session, User
from datetime import datetime
from app.config import current_tz
from app.crud.daily_report import get_daily_report
from app.auth.base_config import current_active_user

router = APIRouter()


@router.get("/")
async def get_daily_report_endpoint(
        db: AsyncSession = Depends(get_async_session),
        date: str = Query(
            ...,
            alias="date",
            description="YYYY-MM-DD format",
            example=datetime.now(current_tz).strftime("%Y-%m")),
        user: User = Depends(current_active_user)
):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    return await get_daily_report(db, date)
