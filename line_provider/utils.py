from datetime import datetime, timezone
from typing import Dict
from fastapi import HTTPException


def is_deadline_valid(deadline: datetime) -> bool:
    """
    Проверяет, что дедлайн для ставки находится в будущем.

    :param deadline: Дата и время дедлайна.
    :return: True, если дедлайн в будущем, иначе False.
    """
    current_time = datetime.now(timezone.utc)
    return deadline > current_time


def get_event_or_404(events: Dict[str, dict], event_id: str) -> dict:
    """
    Проверяет существование события с указанным идентификатором.

    :param events: Словарь всех событий (хранится в памяти).
    :param event_id: Уникальный идентификатор события.
    :return: Событие, если оно найдено.
    :raises HTTPException: Если событие не найдено.
    """
    event = events.get(event_id)
    if not event:
        raise HTTPException(status_code=404, detail=f"Event with ID '{event_id}' not found")
    return event

