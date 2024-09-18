import time

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from sqlalchemy.future import select
from typing import Optional

from app.models.car import Car
from app.models.exception_nums import Number
from app.crud.cars.call_processes import call_processes
from app.crud.cars.car_processes import process_last_attendances


async def get_cars_by_month_pag(
        db: AsyncSession,
        page: Optional[int] = 1,
        limit: Optional[int] = 10,
        date: str = None,
):
    total_func_start = time.time()
    try:
        pag_query_start = time.time()
        pag_query = (select(Car)
                     .filter(Car.date.startswith(date))
                     .limit(limit)
                     .offset((page - 1) * limit)
                     .order_by(Car.date.desc(), Car.time.desc()))
        pag_result = await db.execute(pag_query)
        pag_cars = pag_result.scalars().all()
        pag_query_duration = (time.time() - pag_query_start) * 1000
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")

    exception_nums_query = await db.execute(select(Number))
    exception_nums = exception_nums_query.scalars().all()

    # Remove cars with exception numbers
    exception_car_nums = [exception_num.number for exception_num in exception_nums]
    pag_cars = [car for car in pag_cars if car.number not in exception_car_nums]

    # Car calculation processing
    calculation_start = time.time()

    last_attendances = process_last_attendances(pag_cars)
    last_attendances_count = len(last_attendances)
    top10response = []
    unique_cars = set()
    rounded_response = []

    calculation_duration = (time.time() - calculation_start) * 1000

    time.sleep(.500)

    total_func_duration = (time.time() - total_func_start) * 1000

    return {
        "general": last_attendances,
        "general_count": last_attendances_count,
        "top10": top10response,
        "total_cars": len(unique_cars),
        "graphic": rounded_response,
        "timing": {
            "pag_query_duration": pag_query_duration,
            "calculation_duration": calculation_duration,
            "total_func_duration": total_func_duration
        }
    }


async def get_cars_by_month(
        db: AsyncSession,
        date: str,
):
    try:
        query_start = time.time()
        query = select(Car).filter(Car.date.startswith(date))
        result = await db.execute(query)
        cars = result.scalars().all()
        query_duration = (time.time() - query_start) * 1000
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")

    return ...



