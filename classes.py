from dataclasses import dataclass
from aiogram.fsm.state import State, StatesGroup

@dataclass(frozen=True)
class DbConfig:
    admin: str
    password: str
    host: str
    port: int
    db_name: str


@dataclass(frozen=True)
class User:
    id: int
    name: str


class RollCallStates(StatesGroup):
    waiting_subject = State()


@dataclass
class RollCall:
    roll_id: str
    subject: str
    users: dict[int, str]
    present: set[int]
    absent: set[int]
    report_sent: bool
    admin_message_id: int | None