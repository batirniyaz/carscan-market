import time
from datetime import datetime

from fastapi import APIRouter, Depends, Query, UploadFile, File, status, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.base_config import current_active_user
from app.auth.database import get_async_session, User
from app.config import current_tz
from app.crud.car import create_car, get_car, migrate_images_to_s3
from app.crud.cars import get_cars_by_week, get_cars_by_day, get_cars_by_month
from app.schemas.car import CarResponse

router = APIRouter()


@router.post("/", response_model=CarResponse)
async def create_car_endpoint(
        number: str = Query(..., description="The number of the car", alias="car-number", example="95A123BB"),
        date: str = Query(
            ...,
            description="The date of the car",
            alias="car-date",
            example=f"{datetime.now(current_tz).strftime('%Y-%m-%d')}"),
        time: str = Query(
            ...,
            description="The time of the car",
            alias="car-time",
            example=f"{datetime.now(current_tz).strftime('%H:%M:%S')}"),
        db: AsyncSession = Depends(get_async_session),
        image: UploadFile = File(None),
        user: User = Depends(current_active_user)
):
    try:
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

        if not image:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Image is required")

        if len(number) != 8:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Number must be 8 characters and match example")

        if len(date) != 10:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Date must be 10 characters and format YYYY-MM-DD")

        if len(time) != 8:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Time must be 8 characters and format HH:MM:SS")

        return await create_car(db=db, number=number, date=date, time=time, image=image)

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/day")
async def get_cars_endpoint(
        response: Response,
        db: AsyncSession = Depends(get_async_session),
        page: int = Query(1, description="The page number", alias="page"),
        limit: int = Query(10, description="The number of cars per page", alias="limit"),
        day: str = Query(
            datetime.now(current_tz).strftime("%Y-%m-%d"),
            description="The date should be in format DD",
            alias="day",
        ),
        user: User = Depends(current_active_user)
):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    start_time = time.time()

    cars_data = await get_cars_by_day(db=db, page=page, limit=limit, date=day)

    total_duration = (time.time() - start_time) * 1000

    response.headers["Server-Timing"] = (
        f"query_duration;dur={cars_data['timing']['query_duration']:.2f}, "
        f"calculation_duration;dur={cars_data['timing']['calculation_duration']:.2f}, "
        f"total;dur={total_duration:.2f}"
    )

    return cars_data


@router.get("/month")
async def get_cars_by_month_endpoint(
        response: Response,
        db: AsyncSession = Depends(get_async_session),
        page: int = Query(1, description="The page number", alias="page"),
        limit: int = Query(10, description="The number of cars per page", alias="limit"),
        month: str = Query(
            datetime.now(current_tz).strftime("%Y-%m"),
            description="The date should be in format MM",
            alias="month",
        ),
        user: User = Depends(current_active_user)
):
    start_time = time.time()

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    cars_data = await get_cars_by_month(db=db, page=page, limit=limit, date=month)

    total_duration = (time.time() - start_time) * 1000

    response.headers["Server-Timing"] = (
        f"query_duration;dur={cars_data['timing']['query_duration']:.2f}, "
        f"pag_query_duration;dur={cars_data['timing']['pag_query_duration']:.2f}, "
        f"calculation_duration;dur={cars_data['timing']['calculation_duration']:.2f}, "
        f"total;dur={total_duration:.2f}"
    )

    return cars_data


@router.get("/week")
async def get_cars_endpoint(
        response: Response,
        db: AsyncSession = Depends(get_async_session),
        page: int = Query(1, description="The page number", alias="page"),
        limit: int = Query(10, description="The number of cars per page", alias="limit"),
        week: str = Query(
            datetime.now(current_tz).strftime("%Y-%W"),
            description="The date should be in format YYYY-WW",
            alias="week",
        ),
        user: User = Depends(current_active_user)
):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    start_time = time.time()

    cars_data = await get_cars_by_week(db=db, page=page, limit=limit, week=week)

    total_duration = (time.time() - start_time) * 1000

    response.headers["Server-Timing"] = (
        f"query_duration;dur={cars_data['timing']['query_duration']:.2f}, "
        f"calculation_duration;dur={cars_data['timing']['calculation_duration']:.2f}, "
        f"total;dur={total_duration:.2f}"
    )

    return cars_data

@router.get("/migrate")
async def search_cars_endpoint(
        db: AsyncSession = Depends(get_async_session)):
    await migrate_images_to_s3(db, )


@router.get("/{car_number}")
async def get_car_endpoint(
        response: Response,
        car_number: str,
        db: AsyncSession = Depends(get_async_session),
        page: int = Query(1, description="The page number", alias="page"),
        limit: int = Query(10, description="The number of cars per page", alias="limit"),
        date: str = Query(
            ...,
            description="The month or day of the cars",
            alias="date",
            example=f"{datetime.now(current_tz).strftime('%Y-%m')}",
        ),
        user: User = Depends(current_active_user)
):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    if not car_number:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Car number is required")

    if not page and limit:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Page and limit are required")

    start_time = time.time()
    car_data = await get_car(db=db, page=page, limit=limit, car_number=car_number, date=date)
    total_duration = (time.time() - start_time) * 1000

    response.headers["Server-Timing"] = (
        f"total;dur={total_duration:.2f}"
    )

    return car_data


