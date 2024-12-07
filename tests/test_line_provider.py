from datetime import datetime, timezone, timedelta
import pytest
from aiohttp import ClientSession


async def create_event(session: ClientSession, event_id: str, coefficient: float, deadline: str, state: str) -> dict:
    """
    Создает событие через API и возвращает данные созданного события.

    :param session: Экземпляр ClientSession для выполнения запросов.
    :param event_id: Уникальный идентификатор события.
    :param coefficient: Коэффициент ставки.
    :param deadline: Дедлайн события в формате ISO8601.
    :param state: Статус события.
    :return: Словарь с данными созданного события.
    """
    test_event = {
        "event_id": event_id,
        "coefficient": coefficient,
        "deadline": deadline,
        "state": state
    }
    async with session.post("/events", json=test_event) as response:
        response_text = await response.text()
        assert response.status == 201, f"Failed to create event: {response_text}"
        return await response.json()


async def get_event(session: ClientSession, event_id: str) -> dict:
    """
    Получает данные события через API.

    :param session: Экземпляр ClientSession для выполнения запросов.
    :param event_id: Уникальный идентификатор события.
    :return: Словарь с данными события.
    """
    async with session.get(f"/events/{event_id}") as response:
        response_text = await response.text()
        assert response.status == 200, f"Failed to retrieve event: {response_text}"
        return await response.json()


async def update_event_status(session: ClientSession, event_id: str, state: str) -> dict:
    """
    Обновляет статус события через API.

    :param session: Экземпляр ClientSession для выполнения запросов.
    :param event_id: Уникальный идентификатор события.
    :param state: Новый статус события.
    :return: Словарь с обновленными данными события.
    """
    async with session.patch(f"/events/{event_id}/status?state={state}") as response:
        response_text = await response.text()
        assert response.status == 200, f"Failed to update event status: {response_text}"
        return await response.json()


@pytest.mark.parametrize('anyio_backend', ['asyncio'])
async def test_line_provider_workflow(anyio_backend: str) -> None:
    """
    Тестирует рабочий процесс провайдера линий.

    :param anyio_backend: Бэкенд для асинхронного тестирования (например, asyncio).
    """
    test_event_id = "test_event_1"
    test_deadline = (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat()
    test_coefficient = 1.5
    test_state = "new"

    async with ClientSession(base_url="http://line-provider:8001") as session:

        created_event = await create_event(session, test_event_id, test_coefficient, test_deadline, test_state)
        assert created_event["event_id"] == test_event_id
        assert created_event["coefficient"] == test_coefficient
        assert created_event["state"] == test_state

        created_deadline = int(datetime.fromisoformat(created_event["deadline"].replace("Z", "")).timestamp())
        expected_deadline = int(datetime.fromisoformat(test_deadline.replace("Z", "")).timestamp())
        assert abs(created_deadline - expected_deadline) <= 5, "Mismatch in deadline"

        event = await get_event(session, test_event_id)
        assert event["event_id"] == test_event_id
        assert event["coefficient"] == test_coefficient
        assert event["state"] == test_state

        retrieved_deadline = int(datetime.fromisoformat(event["deadline"].replace("Z", "")).timestamp())
        assert abs(retrieved_deadline - expected_deadline) <= 5, "Mismatch in deadline"

        new_status = "finished_win"
        updated_event = await update_event_status(session, test_event_id, new_status)
        assert updated_event["state"] == new_status

        updated_event = await get_event(session, test_event_id)
        assert updated_event["state"] == new_status
