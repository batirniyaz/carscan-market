from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.database import get_async_session
from app.crud.exception_nums import create_exception_num, get_exception_nums, delete_exception_num
from app.schemas.exception_nums import NumbersResponse

router = APIRouter()


@router.post("/", response_model=NumbersResponse)
async def create_exception_num_endpoint(
        number: str,
        db: AsyncSession = Depends(get_async_session),
):
    return await create_exception_num(db, number)


@router.get("/", response_model=[])
async def get_exception_nums_endpoint(
        db: AsyncSession = Depends(get_async_session),
):
    return await get_exception_nums(db)


@router.delete("/{car_number")
async def delete_exception_num_endpoint(
        car_number: str,
        db: AsyncSession = Depends(get_async_session),
):
    return await delete_exception_num(db, car_number)
