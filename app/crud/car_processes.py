from datetime import datetime

from app.config import BASE_URL
from app.utils.time_utils import round_time_slot


def process_last_attendances(cars_with_pagination, date):
    last_attendances = []

    for car in cars_with_pagination:
        last_attendances.append({
            "attend_id": car.id,
            "car_number": car.number,
            "attend_date": car.date,
            "attend_time": car.time,
            "image_url": f"{BASE_URL}{car.image_url}"
        })

    if len(date) == 10:
        last_attendances_sorted = sorted(last_attendances, key=lambda x: x["attend_time"], reverse=True)
    else:
        last_attendances_sorted = sorted(last_attendances, key=lambda x: (x["attend_date"], x["attend_time"]), reverse=True)

    return last_attendances_sorted


def process_last_attendances_without_pagination(cars):
    last_attendances_count = 0

    for _ in cars:
        last_attendances_count += 1
    return last_attendances_count


def process_attend_count(cars):
    unique_cars = set()
    attend_count = {}
    attend_count_cars = {}

    for car in cars:

        if car.number not in attend_count:
            attend_count[car.number] = 1
        else:
            attend_count[car.number] += 1

        if car.date not in attend_count_cars:
            attend_count_cars[car.date] = 1
        else:
            attend_count_cars[car.date] += 1

        if car.number not in unique_cars:
            unique_cars.add(car.number)

    sorted_cars = sorted(cars, key=lambda x: attend_count[x.number], reverse=True)

    return attend_count, unique_cars, sorted_cars, attend_count_cars


def process_top10_response(sorted_cars, attend_count):
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

    return top10response, all_car_response


def process_rounded_time(cars):
    time_slots = {}
    for car in cars:
        rounded_time = round_time_slot(datetime.strptime(car.time, "%H:%M:%S"))
        if rounded_time not in time_slots:
            time_slots[rounded_time] = 1
        else:
            time_slots[rounded_time] += 1

    return [{"time": time, "count": count} for time, count in time_slots.items()]


def process_rounded_month(cars):
    day_slots = {}
    for car in cars:
        if car.date not in day_slots:
            day_slots[car.date] = 1
        else:
            day_slots[car.date] += 1

    return [{"day": day, "count": count} for day, count in day_slots.items()]


def process_rounded_weekday(cars):
    weekday_slots = {}
    for car in cars:
        weekday = datetime.strptime(car.date, "%Y-%m-%d").strftime("%A").lower()
        if weekday not in weekday_slots:
            weekday_slots[weekday] = 1
        else:
            weekday_slots[weekday] += 1

    return [{"weekday": weekday, "count": count} for weekday, count in weekday_slots.items()]
