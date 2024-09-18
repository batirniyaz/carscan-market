import time
from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.car import Car
from app.models.exception_nums import Number
from app.crud.cars.call_processes import call_processes
from app.crud.cars.car_processes import process_rounded_weekday


async def get_cars_by_week(
        db: AsyncSession,
        page: Optional[int] = 1,
        limit: Optional[int] = 10,
        week: str = None,
):
    query_start = time.time()
    try:
        year, week_num = week.split('-')
        start_date = datetime.strptime(f'{year}-W{week_num}-1', "%Y-W%W-%w").date()
        end_date = start_date + timedelta(days=6)
        query = select(Car).filter(Car.date.between(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")))
        pag_query = (select(Car)
                     .offset((page - 1) * limit)
                     .limit(limit)
                     .filter(Car.date
                             .between(start_date
                                      .strftime("%Y-%m-%d"),end_date
                                      .strftime("%Y-%m-%d")))
                     .order_by(Car.date.desc(), Car.time.desc()))
        res = await db.execute(query)
        pag_res = await db.execute(pag_query)
        cars = res.scalars().all()
        pag_cars = pag_res.scalars().all()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid week format")

    query_duration = (time.time() - query_start) * 1000

    exception_cars_query = await db.execute(select(Number))
    exception_cars = exception_cars_query.scalars().all()

    exception_nums = [exception_num.number for exception_num in exception_cars]
    cars = [car for car in cars if car.number not in exception_nums]
    pag_cars = [car for car in pag_cars if car.number not in exception_nums]

    calculation_start = time.time()

    (last_attendances,
     last_attendances_count,
     top10response,
     top10response,
     unique_cars) = call_processes(pag_cars, cars)

    rounded_response = process_rounded_weekday(cars)

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




