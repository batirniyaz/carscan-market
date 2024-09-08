def round_time_slot(time):
    if time.minute >= 30:
        rounded_hour = (time.hour + 1) % 24
    else:
        rounded_hour = time.hour

    return f"{rounded_hour:02}:00"
