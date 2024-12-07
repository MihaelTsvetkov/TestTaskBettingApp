import pytest
from aiohttp import ClientSession
from datetime import datetime, timedelta, timezone


async def create_event_if_not_exists(event_id: str, base_url: str, test_event_data: dict = None) -> None:
    """
    Создает событие, если его нет.

    :param event_id: Уникальный идентификатор события.
    :param base_url: Базовый URL для API.
    :param test_event_data: Пользовательские данные для создания события.
    """
    async with ClientSession(base_url=base_url) as session:
        async with session.get(f"/events/{event_id}") as get_event_response:
            if get_event_response.status == 404:
                test_event = test_event_data or {
                    "event_id": event_id,
                    "coefficient": 1.5,
                    "deadline": (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat(),
                    "state": "new"
                }
                async with session.post("/events", json=test_event) as create_event_response:
                    assert create_event_response.status == 201, "Failed to create event"
            else:
                event_data = await get_event_response.json()
                deadline = datetime.fromisoformat(event_data["deadline"])
                assert deadline > datetime.now(timezone.utc), "Event deadline is in the past"


async def make_request(session: ClientSession,
                       method: str,
                       url: str,
                       expected_status: int = 200,
                       return_json=True,
                       **kwargs) -> dict | str:
    """
    Выполняет HTTP-запрос и возвращает ответ.

    :param session: Экземпляр ClientSession для выполнения запросов.
    :param method: HTTP-метод (GET, POST и т.д.).
    :param url: URL для выполнения запроса.
    :param expected_status: Ожидаемый HTTP-статус ответа.
    :param return_json: Флаг, указывающий, нужно ли возвращать JSON-ответ.
    :param kwargs: Дополнительные параметры запроса.
    :return: Ответ в формате JSON (или текст, если return_json=False).
    """
    async with session.request(method, url, **kwargs) as response:
        response_text = await response.text()
        assert response.status == expected_status, f"Request failed: {response_text}"
        return await response.json() if return_json else response_text


def validate_bet(bet: dict, expected_bet: dict) -> None:
    """
    Проверяет соответствие ставки ожидаемым данным.

    :param bet: Словарь с данными ставки.
    :param expected_bet: Ожидаемые данные ставки.
    """
    assert float(bet["amount"]) == float(expected_bet["amount"]), "Mismatch in bet amount"
    assert bet["event_id"] == expected_bet["event_id"], "Mismatch in event ID"


@pytest.mark.parametrize('anyio_backend', ['asyncio'])
async def test_bet_maker_workflow(anyio_backend: str) -> None:
    """
    Тестирует рабочий процесс для сервиса ставок.

    :param anyio_backend: Бэкенд для асинхронного тестирования (например, asyncio).
    """
    test_event_id = "3"

    await create_event_if_not_exists(test_event_id, base_url="http://line-provider:8001")

    test_bet = {"event_id": test_event_id, "amount": 100.50}
    async with ClientSession(base_url="http://bet-maker:8000") as session:

        created_bet = await make_request(session, "POST", "/bets", json=test_bet, expected_status=201)
        validate_bet(created_bet, test_bet)

        bet_id = created_bet["bet_id"]
        bet = await make_request(session, "GET", f"/bets/{bet_id}")
        validate_bet(bet, created_bet)

        update_data = {"event_id": test_event_id, "status": "finished_win"}
        update_response = await make_request(session, "POST", "/bets/update", json=update_data)
        assert "updated" in update_response["message"]

        bets = await make_request(session, "GET", "/bets")
        assert any(bet["status"] == "won" for bet in bets if bet["bet_id"] == bet_id)
