from enum import Enum
from decimal import Decimal
from pydantic import BaseModel, Field


class BetStatus(str, Enum):
    """
    Enum, представляющий возможные статусы ставки.
    """
    PENDING = "pending"
    WON = "won"
    LOST = "lost"


class Bet(BaseModel):
    """
    Модель, представляющая информацию о ставке.
    """
    bet_id: str = Field(..., description="The unique identifier of the bet")
    event_id: str = Field(..., description="The unique identifier of the event")
    amount: Decimal = Field(..., gt=0, description="The amount of the bet")
    status: BetStatus = Field(BetStatus.PENDING, description="The status of the bet")


class CreateBetRequest(BaseModel):
    """
    Модель запроса для создания новой ставки.
    """
    event_id: str = Field(..., description="The unique identifier of the event")
    amount: Decimal = Field(..., gt=0, description="The amount of the bet")


class CreateBetResponse(BaseModel):
    """
    Модель ответа после успешного создания ставки.
    """
    bet_id: str = Field(..., description="The unique identifier of the bet")
    event_id: str = Field(..., description="The identifier of the related event")
    amount: float = Field(..., description="The amount of the bet")
    status: str = Field(..., description="The current status of the bet")


class BetHistoryResponse(BaseModel):
    """
    Модель ответа, представляющая историю ставок.
    """
    bet_id: str = Field(..., description="The unique identifier of the bet")
    event_id: str = Field(..., description="The unique identifier of the event")
    amount: Decimal = Field(..., gt=0, description="The amount of the bet")
    status: BetStatus = Field(BetStatus.PENDING, description="The status of the bet")
