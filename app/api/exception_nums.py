from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.database import get_async_session, User
from app.crud.exception_nums import create_exception_num, get_exception_nums, delete_exception_num
from app.schemas.exception_nums import NumbersResponse
from app.auth.base_config import current_active_user

router = APIRouter()


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
async def get_exception_nums_endpoint(
        db: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_active_user)
):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    return await get_exception_nums(db)


@router.delete("/{car_number}")
async def delete_exception_num_endpoint(
        car_number: str,
        db: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_active_user)
):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    return await delete_exception_num(db, car_number)
