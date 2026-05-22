# generators/anomaly_generator.py

import random
from datetime import datetime, timedelta
from .alarm_schema import AlarmEvent


ERROR_CODES = ["E01", "E02", "E12", "E99"]


def generate_anomaly_event(start_time: datetime) -> AlarmEvent:
    """Genererar ett ovanligt eller farligt/anomal larm-event."""

    # Orimliga eller misstänkta värden
    anomaly_type = random.choice([
        "no_response",
        "long_response",
        "early_door_open",
        "double_alarm",
        "sensor_spike",
        "hardware_error",
    ])

    # Defaultvärden
    response_time = random.uniform(10, 120)
    door_open_time = random.uniform(1, 10)
    reset_time = random.uniform(30, 180)
    staff_present = True
    double_alarm = False
    error_code = None

    # Modifiera utifrån anomalityp
    if anomaly_type == "no_response":
        response_time = 9999
        staff_present = False

    elif anomaly_type == "long_response":
        response_time = random.uniform(300, 2000)  # svar dröjer extremt

    elif anomaly_type == "early_door_open":
        response_time = random.uniform(30, 300)
        door_open_time = 0.1                       # dörr öppnas FÖRE kvittering

    elif anomaly_type == "double_alarm":
        double_alarm = True

    elif anomaly_type == "sensor_spike":
        response_time = random.uniform(0, 3)       # supersnabb (o-logisk)
        reset_time = random.uniform(0, 5)
        door_open_time = random.uniform(0, 2)

    elif anomaly_type == "hardware_error":
        error_code = random.choice(ERROR_CODES)
        staff_present = False

    return AlarmEvent(
        timestamp=start_time,
        alarm_type="anomaly",
        response_time=response_time,
        reset_time=reset_time,
        door_open_time=door_open_time,
        staff_present=staff_present,
        double_alarm=double_alarm,
        error_code=error_code,
        anomaly=True
    )


def generate_anomaly_dataset(n: int, start_time: datetime):
    """Skapar en lista med n anomalier."""
    events = []
    current_time = start_time

    for _ in range(n):
        event = generate_anomaly_event(current_time)
        events.append(event)

        # Anomalier kan komma tätare
        current_time += timedelta(minutes=random.uniform(0.5, 10))

    return events
