from pydantic import BaseModel
from typing import Optional

class DisruptionInput(BaseModel):
    flight_number: str
    airline: Optional[str] = ""
    origin: str
    destination: str
    scheduled_departure: Optional[str] = ""
    delay_minutes: Optional[int] = 0
    disruption_type: Optional[str] = ""
    severity: Optional[int] = 5
    notes: Optional[str] = ""