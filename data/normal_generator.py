# generators/normal_generator.py

import random
from datetime import datetime, timedelta
from .alarm_schema import AlarmEvent


ALARM_TYPES = ["toalarm", "nödlarm", "överfallslarm", "assistans"]


def generate_normal_event(start_time: datetime) -> AlarmEvent:
    """Genererar ett normalt, realistiskt larm-event."""

    alarm_type = random.choice(ALARM_TYPES)

    # Normala tidsintervall
    response_time = random.uniform(10, 120)         # kvittering inom 10-120 sek
    door_open_time = random.uniform(1, 10)          # dörr öppnas snabbt
    reset_time = random.uniform(30, 180)            # återställning inom 0.5–3 min

    staff_present = True                            # personal hanterar larm korrekt
    double_alarm = random.random() < 0.05           # 5% chans, mycket ovanligt
    error_code = None                               # inga fel i normalt läge

    return AlarmEvent(
        timestamp=start_time,
        alarm_type=alarm_type,
        response_time=response_time,
        reset_time=reset_time,
        door_open_time=door_open_time,
        staff_present=staff_present,
        double_alarm=double_alarm,
        error_code=error_code,
        anomaly=False
    )


def generate_normal_dataset(n: int, start_time: datetime):
    """Skapar en lista med n normala event."""
    events = []
    current_time = start_time

    for _ in range(n):
        event = generate_normal_event(current_time)
        events.append(event)

        # Hoppa fram i tiden (larm inträffar då och då)
        current_time += timedelta(minutes=random.uniform(1, 20))

    return events
