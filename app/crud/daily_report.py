
import schedule
import asyncio

from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.config import current_tz, BASE_URL
from app.auth.database import get_async_session
from app.models.daily_report import DailyReport
from app.crud.car import get_car
from app.utils.excel_file_utils import create_excel_file

from app.models.exception_nums import StartEndTime
from app.models.car import Car
from app.crud.cars import get_cars_by_day


async def define_date_type(db: AsyncSession, date: str):
    query = select(DailyReport)

    if len(date) == 10:
        result = await db.execute(query.filter_by(date=date))
        daily_report = result.scalars().first()
    else:
        result = await db.execute(query.filter(DailyReport.date.startswith(date)).order_by(DailyReport.date.desc()))
        daily_report = result.scalars().all()

    return daily_report if daily_report else []


async def get_daily_report(db: AsyncSession, date: str):
    daily_report = await define_date_type(db, date)

    return daily_report


async def store_daily_report():
    current_date = datetime.now(current_tz).strftime("%Y-%m-%d")
    date = "2024-09-16"

    async for session in get_async_session():
        async with session.begin():
            response = await get_cars_by_day(db=session, page=1, limit=10, date=date)
            result = await session.execute(select(Car).filter_by(date=date))
            cars_attendances = result.scalars().all()

            start_and_end_res = await session.execute(select(StartEndTime).limit(1))
            start_and_end = start_and_end_res.scalars().first()

            START_TIME = start_and_end.start_time
            END_TIME = start_and_end.end_time

            attend_count = {}
            unique_cars = set()
            for car in cars_attendances:
                if car.number not in attend_count:
                    attend_count[car.number] = 1
                else:
                    attend_count[car.number] += 1

                if car.number not in unique_cars:
                    unique_cars.add(car.number)

            sorted_cars = sorted(cars_attendances, key=lambda x: attend_count[x.number], reverse=True)

            all_car_response = []
            all_cars = set()
            for car in sorted_cars:
                if car.number not in all_cars:
                    all_car_response.append({
                        "attend_id": car.id,
                        "car_number": car.number,
                        "attend_date": car.date,
                        "attend_time": car.time,
                        "image_url": f"{BASE_URL}{car.image_url}",
                        "attend_count": attend_count[car.number]
                    })
                    all_cars.add(car.number)

            top10 = response["top10"]
            total_cars = response["total_cars"]

            top10_cars = []
            for car in top10:
                if car["attend_count"] > 2:
                    if START_TIME <= car["attend_time"] <= END_TIME:
                        top10_cars.append(car)

            cars_attendances_count = 0
            general_cars = []
            for car in all_car_response:
                if car["attend_count"] > 2:
                    if START_TIME <= car["attend_time"] <= END_TIME:
                        general_cars.append(car)
                        cars_attendances_count += car["attend_count"]

            daily_report = DailyReport(
                date=date,
                top10=top10_cars,
                general=general_cars,
                general_attendances_count=cars_attendances_count,
                general_count=len(general_cars),
                overall_count=total_cars
            )

            session.add(daily_report)


def schedule_daily_report():
    schedule_time = datetime.now(current_tz).replace(hour=00, minute=23, second=0, microsecond=0)
    schedule.every().day.at(schedule_time.strftime("%H:%M")).do(lambda: asyncio.create_task(store_daily_report()))


async def run_scheduler():
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)

schedule_daily_report()
asyncio.create_task(run_scheduler())


async def create_excel_report(db: AsyncSession, date: str):
    daily_report = await define_date_type(db, date)

    if len(date) == 10:
        daily_report_car_numbers = [car["car_number"] for car in daily_report.general]
        data = await get_car(db=db, date=date, page=None, limit=None, car_number=None)
        formated_data = [car if car["car_number"] in daily_report_car_numbers else None for car in data]
        formated_response = []

        total_cars = 0
        total_attendance = 0

        for car in formated_data:
            if car is not None:
                for attend in daily_report.general:
                    if attend["car_number"] == car["car_number"]:
                        formated_response.append(
                            {
                                "car_number": car["car_number"],
                                "attend_count": attend["attend_count"],
                                "first_time": car["first_time"],
                                "last_time": car["last_time"],
                            }
                        )
                        total_cars += 1
                        total_attendance += attend["attend_count"]

        formated_response.append({"car_number": "", "attend_count": "", "first_time": "", "last_time": ""})

        formated_response.append(
            {
                "car_number": f"{total_cars} cars",
                "attend_count": f"total {total_attendance}",
                "first_time": "",
                "last_time": "",
            }
        )

        excel_report = await create_excel_file(formated_response, file_name=f"daily_report_{date}")

        return excel_report
    else:
        formated_general_data = []

        total_daily_count = 0
        total_paid_car = 0
        total_non_paid_car = 0
        total_general_count = 0

        for report in daily_report:
            daily_count = 0
            non_paid_count = report.overall_count - report.general_count
            for car in report.general:
                daily_count += car["attend_count"]
            formated_general_data.append(
                {
                    "date": report.date,
                    "daily_count": daily_count,
                    "average_come": daily_count / report.general_count if report.general_count != 0 else 0,
                    "paid_car": report.general_count,
                    "non_paid_car": non_paid_count,
                    "general_count": report.general_attendances_count,
                }
            )
            total_daily_count += daily_count
            total_paid_car += report.general_count
            total_non_paid_car += non_paid_count
            total_general_count += report.general_attendances_count or 0

        formated_general_data.append({"date": "", "daily_count": "", "average_come": "", "paid_car": "", "non_paid_car": "", "general_count": ""})

        formated_general_data.append(
            {
                "date": "Total",
                "daily_count": total_daily_count,
                "average_come": total_daily_count / total_paid_car if total_paid_car != 0 else 0,
                "paid_car": total_paid_car,
                "non_paid_car": total_non_paid_car,
                "general_count": total_general_count,
            }
        )

        excel_report = await create_excel_file(formated_general_data, file_name=f"monthly_report_{date}")

        return excel_report
