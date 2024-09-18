import time

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from sqlalchemy.future import select
from typing import Optional

from app.models.car import Car
from app.models.exception_nums import Number
from app.crud.cars.call_processes import call_processes
from app.crud.cars.car_processes import process_rounded_month


async def get_cars_by_month(
        db: AsyncSession,
        page: Optional[int] = 1,
        limit: Optional[int] = 10,
        date: str = None,
):
    try:
        query_start = time.time()
        query = select(Car).filter(Car.date.startswith(date))
        result = await db.execute(query)
        cars = result.scalars().all()
        query_duration = (time.time() - query_start) * 1000
        pag_query_start = time.time()
        pag_query = query.limit(limit).offset((page - 1) * limit).order_by(Car.date.desc(), Car.time.desc())
        pag_result = await db.execute(pag_query)
        pag_cars = pag_result.scalars().all()
        pag_query_duration = (time.time() - pag_query_start) * 1000
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")

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
     unique_cars) = call_processes(pag_cars, cars)

    rounded_response = process_rounded_month(cars)

    calculation_duration = (time.time() - calculation_start) * 1000

    query_test_start = time.time()
    result = await db.execute(select(Car).filter(Car.date.startswith(date)))
    cars = result.scalars().all()
    query_test_duration = (time.time() - query_start) * 1000

    return {
        "general": last_attendances,
        "general_count": last_attendances_count,
        "top10": top10response,
        "total_cars": len(unique_cars),
        "graphic": rounded_response,
        "timing": {
            "query_duration": query_duration,
            "pag_query_duration": pag_query_duration,
            "calculation_duration": calculation_duration,
            "query_test_duration": query_test_duration
        }
    }

