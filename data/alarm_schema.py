# generators/alarm_schema.py

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class AlarmEvent:
    timestamp: datetime
    alarm_type: str                 # ex: "toalarm", "nödlarm", "överfallslarm"
    response_time: float            # sekunder tills kvittering
    reset_time: float               # sekunder tills systemet återställs
    door_open_time: float           # sekunder tills dörr öppnas
    staff_present: bool             # personal närvarande
    double_alarm: bool              # om två larm kommer nära varandra
    error_code: Optional[str]       # felkod eller None
    anomaly: bool                   # markerar om eventet är anomal eller ej

    def to_dict(self):
        """Konverterar eventet till en flat dict som kan sparas som CSV."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "alarm_type": self.alarm_type,
            "response_time": self.response_time,
            "reset_time": self.reset_time,
            "door_open_time": self.door_open_time,
            "staff_present": int(self.staff_present),
            "double_alarm": int(self.double_alarm),
            "error_code": self.error_code if self.error_code else "",
            "anomaly": int(self.anomaly),
        }
