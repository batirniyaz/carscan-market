from datetime import datetime, timedelta

from fastapi import UploadFile, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from concurrent.futures import ThreadPoolExecutor

from app.config import BASE_URL, START_TIME, END_TIME

from app.models.car import Car
from app.models.exception_nums import Number

from app.utils.file_utils import save_upload_file

from app.crud.car_processes import (
    process_last_attendances,
    process_attend_count,
    process_top10_response,
    process_rounded_time,
    process_rounded_month,
    process_rounded_weekday
)


async def create_car(db: AsyncSession, number: str, date: str, time: str, image: UploadFile):
    try:
        main_image_url = f"/storage/"
        file_path = save_upload_file(image)
        image_url = f"{main_image_url}{file_path}"

        db_car = Car(number=number, date=date, time=time, image_url=image_url)
        db.add(db_car)
        await db.commit()
        await db.refresh(db_car)

        db_car.image_url = f"{BASE_URL}{image_url}"

        return db_car
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


async def get_cars(
        db: AsyncSession,
        page: int = 1,
        limit: int = 10,
        date: str = None,
        week: str = None
):
    query = select(Car)
    with_pagination_query = query.offset((page - 1) * limit).limit(limit).order_by(Car.time.desc())

    external_res = await db.execute(select(Number))
    external_cars = external_res.scalars().all()

    if date:
        try:
            if len(date) == 10:  # yyyy-mm-dd
                query = query.filter_by(date=date)
                with_pagination_query = with_pagination_query.filter_by(date=date)
            elif len(date) == 7:  # yyyy-mm
                query = query.filter(Car.date.startswith(date))
                with_pagination_query = with_pagination_query.filter(Car.date.startswith(date))
            else:
                raise ValueError
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format")

    if week:
        try:
            if len(week) == 7:
                year, week_num = week.split('-')
                start_date = datetime.strptime(f'{year}-W{week_num}-1', "%Y-W%W-%w").date()
                end_date = start_date + timedelta(days=6)
                query = query.filter(Car.date.between(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")))
                with_pagination_query = with_pagination_query.filter(Car.date.between(start_date.strftime("%Y-%m-%d"),
                                                                                      end_date.strftime("%Y-%m-%d")))
            else:
                raise ValueError
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid week format")

    result = await db.execute(query)
    cars = result.scalars().all()

    with_pagination_result = await db.execute(with_pagination_query)
    cars_with_pagination = with_pagination_result.scalars().all()

    external_car_numbers = [external.number for external in external_cars]
    cars_with_pagination = [car for car in cars_with_pagination if car.number not in external_car_numbers]
    cars = [car for car in cars if car.number not in external_car_numbers]

    with ThreadPoolExecutor() as executor:
        # Submit tasks
        last_attendances_future = executor.submit(process_last_attendances, cars_with_pagination)
        attend_count_future = executor.submit(process_attend_count, cars)

        last_attendances = last_attendances_future.result()
        attend_count, unique_cars, sorted_cars = attend_count_future.result()

        top10response_future = executor.submit(process_top10_response, sorted_cars, attend_count)

        # Handle date-based processing
        rounded_response_future = None
        if date:
            if len(date) == 10:
                rounded_response_future = executor.submit(process_rounded_time, cars)
            elif len(date) == 7:
                rounded_response_future = executor.submit(process_rounded_month, cars)
        elif week:
            rounded_response_future = executor.submit(process_rounded_weekday, cars)

        top10response, all_car_response = top10response_future.result()
        rounded_response = rounded_response_future.result() if rounded_response_future else []

    return {
        "general": last_attendances,
        "top10": top10response,
        "total_cars": len(unique_cars),
        "graphic": rounded_response if rounded_response else [],
        "all_cars": all_car_response
    }


async def get_car(
        db: AsyncSession,
        car_number: str,
        date: str,
        page: int = 1,
        limit: int = 10
):
    query = select(Car).filter_by(number=car_number).offset((page - 1) * limit).limit(limit)
    stmt = query.filter(Car.date.startswith(date))
    result = await db.execute(stmt)
    cars_attendances = result.scalars().all()

    response = []
    first_attendances = {}
    last_attendances = {}

    for car in cars_attendances:
        if car.date not in first_attendances:
            first_attendances[car.date] = car
        elif car.time < first_attendances[car.date].time:
            first_attendances[car.date] = car

        if car.date not in last_attendances:
            last_attendances[car.date] = car
        elif car.time > last_attendances[car.date].time:
            last_attendances[car.date] = car

    for date in first_attendances:
        response.append(
            {
                "date": date,
                "car_number": first_attendances[date].number,
                "first_time": first_attendances[date].time,
                "first_image": f"{BASE_URL}{first_attendances[date].image_url}",
                "last_time": last_attendances[date].time,
                "last_image": f"{BASE_URL}{last_attendances[date].image_url}"
            }
        )

    return response

