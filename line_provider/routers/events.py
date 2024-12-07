from datetime import datetime, timedelta, timezone
from typing import List

from aiohttp import ClientSession
from fastapi import APIRouter, HTTPException, Path

from models import Event, EventState
from utils import is_deadline_valid, get_event_or_404

router = APIRouter()

BET_MAKER_URL = "http://bet-maker:8000"

events = {
    '1': Event(event_id='1',
               coefficient=1.2,
               deadline=datetime.now(timezone.utc) + timedelta(minutes=10),
               state=EventState.NEW),

    '2': Event(event_id='2',
               coefficient=1.15,
               deadline=datetime.now(timezone.utc) + timedelta(minutes=5),
               state=EventState.NEW),

    '3': Event(event_id='3',
               coefficient=1.67,
               deadline=datetime.now(timezone.utc) + timedelta(minutes=15),
               state=EventState.NEW),
}


@router.get("/", response_model=List[Event])
async def get_events() -> List[Event]:
    """
    Возвращает список всех активных событий.

    Событие считается активным, если его дедлайн не истёк.

    :return: Список активных событий.
    """
    current_time = datetime.now(timezone.utc)
    return [event for event in events.values() if event.deadline > current_time]


@router.post("/", response_model=Event, status_code=201)
async def create_event(event: Event) -> Event:
    """
    Создает новое событие.

    Проверяет, что дедлайн находится в будущем, и генерирует уникальный идентификатор события.

    :param event: Данные события, включая идентификатор, коэффициент, дедлайн и статус.
    :return: Созданное событие.
    """
    if event.event_id in events:
        raise HTTPException(status_code=400, detail="Event with this id already exists")
    if not is_deadline_valid(event.deadline):
        raise HTTPException(status_code=400, detail="Deadline must be in the future")

    events[event.event_id] = event
    return event


@router.get("/{event_id}", response_model=Event)
async def get_event(event_id: str = Path(..., description="Event ID")) -> Event:
    """
    Возвращает информацию о событии по его ID.

    :param event_id: Уникальный идентификатор события.
    :return: Событие с указанным ID.
    """
    event = get_event_or_404(events, event_id)
    return event


@router.patch("/{event_id}/status", response_model=Event)
async def update_event_status(event_id: str, state: EventState) -> Event:
    """
    Обновляет статус события.

    Проверяет существование события, обновляет его статус и отправляет запрос
    на обновление статусов связанных ставок.

    :param event_id: Уникальный идентификатор события.
    :param state: Новый статус события.
    :return: Обновлённое событие.
    """
    event = get_event_or_404(events, event_id)
    event.state = state
    events[event_id] = event

    if state in {EventState.FINISHED_WIN, EventState.FINISHED_LOSE}:
        async with ClientSession() as session:
            update_payload = {
                "event_id": event_id,
                "status": state.value
            }
            async with session.post(f"{BET_MAKER_URL}/bets/update", json=update_payload) as response:
                if response.status != 200:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Failed to update bets for event '{event_id}': {await response.text()}"
                    )

    return event
