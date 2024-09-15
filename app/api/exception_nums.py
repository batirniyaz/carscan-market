from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.database import get_async_session, User
from app.crud.exception_nums import (
    create_exception_num,
    get_exception_nums,
    search,
    delete_exception_num,
    create_start_end_time,
    update_start_end_time,
    get_start_end_time
)
from app.schemas.exception_nums import NumbersResponse
from app.auth.base_config import current_active_user
from aiocache import cached

router = APIRouter()
router_start = APIRouter()


@router.post("/", response_model=NumbersResponse)
async def create_exception_num_endpoint(
        number: str,
        db: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_active_user)
):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    return await create_exception_num(db, number)


@router.get("/", response_model=[])
@cached(ttl=60)
async def get_exception_nums_endpoint(
        db: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_active_user)
):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    return await get_exception_nums(db)


@router.get("/search")
@cached(ttl=60)
async def search_endpoint(
        db: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_active_user)
):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    return await search(db)


@router.delete("/{car_number}")
async def delete_exception_num_endpoint(
        car_number: str,
        db: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_active_user)
):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    return await delete_exception_num(db, car_number)


@router_start.post("/")
async def create_start_end_time_endpoint(
        start_time: str,
        end_time: str,
        db: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_active_user),
):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    if len(start_time) != 5 and len(end_time) != 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Time must be 5 characters and format HH:MM")

    return await create_start_end_time(db, start_time, end_time)


@router_start.get("/")
async def get_start_end_time_endpoint(
        db: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_active_user),
):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    return await get_start_end_time(db)


@router_start.put("/")
async def update_start_end_time_endpoint(
        start_time: str = Query(..., description="The start time", alias="start_time", example="07:00"),
        end_time: str = Query(..., description="The end time", alias="end_time", example="19:00"),
        db: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_active_user),
):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    if len(start_time) != 5 and len(end_time) != 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Time must be 5 characters and format HH:MM")

    return await update_start_end_time(db, start_time, end_time)
