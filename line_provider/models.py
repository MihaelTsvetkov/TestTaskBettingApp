from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field


class EventState(Enum):
    """
    Enum, представляющий возможные статусы события.
    """
    NEW = "new"
    FINISHED_WIN = "finished_win"
    FINISHED_LOSE = "finished_lose"


class Event(BaseModel):
    """
    Модель, представляющая событие для ставок.
    """
    event_id: str = Field(..., description="The unique identifier of the event")
    coefficient: float = Field(
        ...,
        gt=0,
        description=(
            "The coefficient of betting on the event (positive number with a two-digit fractional part)"
        )
    )
    deadline: datetime = Field(..., description="The deadline for accepting bets on the event")
    state: EventState = Field(EventState.NEW, description="The current status of the event")

