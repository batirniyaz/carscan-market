import time
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.car import Car
from app.models.exception_nums import Number
from app.crud.cars.call_processes import call_processes
from app.crud.cars.car_processes import process_rounded_time


async def get_cars_by_day(
        db: AsyncSession,
        page: Optional[int] = 1,
        limit: Optional[int] = 10,
        date: str = None,
):
    query_start = time.time()
    try:
        query = select(Car).filter_by(date=date)
        pag_query = query.limit(limit).offset((page - 1) * limit).order_by(Car.time.desc())
        result = await db.execute(query)
        pag_result = await db.execute(pag_query)
        cars = result.scalars().all()
        pag_cars = pag_result.scalars().all()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")

    query_duration = (time.time() - query_start) * 1000

    exception_nums_query = await db.execute(select(Number))
    exception_nums = exception_nums_query.scalars().all()

    # Remove cars with exception numbers
    exception_car_nums = [exception_num.number for exception_num in exception_nums]
    cars = [car for car in cars if car.number not in exception_car_nums]
    pag_cars = [car for car in pag_cars if car.number not in exception_car_nums]

    # Car calculation processing
    calculation_start = time.time()
    (last_attendances,
     last_attendances_count,
     top10response,
     top10response,
     unique_cars) = call_processes(pag_cars, cars)

    rounded_response = process_rounded_time(cars)

    calculation_duration = (time.time() - calculation_start) * 1000

    return {
        "general": last_attendances,
        "general_count": last_attendances_count,
        "top10": top10response,
        "total_cars": len(unique_cars),
        "graphic": rounded_response,
        "timing": {
            "query_duration": query_duration,
            "calculation_duration": calculation_duration
        }
    }


