from __future__ import annotations
from dataclasses import dataclass, asdict

WEEKDAYS_RU = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]


@dataclass(frozen=True)
class Lesson:
    date: str            
    slot: str            #начало пары
    start: str           #фактическое начало (может отличаться от slot)
    end: str             
    subject: str
    kind: str = ""       #тип занятия
    teacher: str = ""
    room: str = ""
    building: str = ""   #корпус
    building_name: str = ""
    online: bool = False
    course_code: str = ""
    note: str = ""
    cancelled: bool = False

    @property
    def key(self) -> str:    #ключик пары, по нему сравниваем версии расписания

        return f"{self.date}|{self.slot}|{self.subject}|{self.kind}"

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "Lesson":
        fields = Lesson.__dataclass_fields__.keys()
        return Lesson(**{k: v for k, v in d.items() if k in fields})
