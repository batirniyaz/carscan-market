from datetime import datetime, timedelta

from fastapi import UploadFile, HTTPException
from app.utils.time_utils import round_time_slot
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.utils.file_utils import save_upload_file
from app.config import BASE_URL
from app.models.car import Car


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
    query = select(Car).offset((page - 1) * limit).limit(limit)

    if date:
        try:
            if len(date) == 10:  # yyyy-mm-dd
                query = query.filter_by(date=date)
            elif len(date) == 7:  # yyyy-mm
                query = query.filter(Car.date.startswith(date))
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
                print(f"start_date: {start_date}, end_date: {end_date}")
            else:
                raise ValueError
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid week format")

    result = await db.execute(query)
    cars = result.scalars().all()

    response = []
    unique_cars = set()
    attend_count = {}

    for car in cars:
        if car.number not in attend_count:
            attend_count[car.number] = 1
        else:
            attend_count[car.number] += 1

        if car.number not in unique_cars:
            unique_cars.add(car.number)

        response.append({
            "attend_id": car.id,
            "car_number": car.number,
            "attend_date": car.date,
            "attend_time": car.time,
            "image_url": f"{BASE_URL}{car.image_url}"
        })

    sorted_cars = sorted(cars, key=lambda x: attend_count[x.number], reverse=True)

    top10response = []
    added_cars = set()
    for car in sorted_cars:
        if car.number not in added_cars:
            top10response.append({
                "attend_id": car.id,
                "car_number": car.number,
                "attend_date": car.date,
                "attend_time": car.time,
                "image_url": f"{BASE_URL}{car.image_url}",
                "attend_count": attend_count[car.number]
            })
            added_cars.add(car.number)
            if len(top10response) == 10:
                break

    rounded_response = []

    if date:
        if len(date) == 10:
            time_slots = {}
            for car in cars:
                rounded_time = round_time_slot(datetime.strptime(car.time, "%H:%M:%S"))
                if rounded_time not in time_slots:
                    time_slots[rounded_time] = 1
                else:
                    time_slots[rounded_time] += 1

            rounded_response = [{"time": time, "count": count} for time, count in time_slots.items()]
        elif len(date) == 7:
            day_slots = {}
            for car in cars:
                if car.date not in day_slots:
                    day_slots[car.date] = 1
                else:
                    day_slots[car.date] += 1

            rounded_response = [{"day": day, "count": count} for day, count in day_slots.items()]

    elif week:
        weekday_slots = {}
        for car in cars:
            weekday = datetime.strptime(car.date, "%Y-%m-%d").strftime("%A").lower()
            if weekday not in weekday_slots:
                weekday_slots[weekday] = 1
            else:
                weekday_slots[weekday] += 1

        rounded_response = [{"weekday": weekday, "count": count} for weekday, count in weekday_slots.items()]

    return {
        "general": response,
        "top10": top10response,
        "total_cars": len(unique_cars),
        "graphic": rounded_response
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
