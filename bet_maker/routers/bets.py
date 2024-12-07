from typing import List, Dict

import aiohttp
from fastapi import APIRouter, HTTPException
from models import CreateBetRequest, CreateBetResponse, BetStatus, BetHistoryResponse, Bet
from provider.database import database

router = APIRouter()


@router.post("/", response_model=CreateBetResponse, status_code=201, tags=["Bets"])
async def create_bet(bet_request: CreateBetRequest) -> CreateBetResponse:
    """
    Создает новую ставку на событие.

    :param bet_request: Данные для создания ставки, включая идентификатор события и сумму ставки.
    :return: Объект CreateBetResponse с информацией о созданной ставке.
    :raises HTTPException: Если событие не найдено, уже завершено или недоступно.
    """
    line_provider_url = f"http://line-provider:8001/events/{bet_request.event_id}"

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(line_provider_url) as response:
                if response.status == 404:
                    raise HTTPException(status_code=400, detail="Событие не найдено или уже завершено")
                elif response.status != 200:
                    raise HTTPException(status_code=500, detail="Ошибка связи с сервисом line-provider")
                event_data = await response.json()
        except aiohttp.ClientError as e:
            raise HTTPException(status_code=500, detail=f"Ошибка запроса к line-provider: {str(e)}")

    if event_data["state"] != "new":
        raise HTTPException(status_code=400, detail="Событие недействительно для ставки")

    query = """
    INSERT INTO bets (event_id, amount, status)
    VALUES (:event_id, :amount, :status)
    RETURNING bet_id;
    """

    values = {
        "event_id": bet_request.event_id,
        "amount": bet_request.amount,
        "status": BetStatus.PENDING.value
    }

    bet_id = await database.execute(query=query, values=values)
    return CreateBetResponse(
        bet_id=str(bet_id),
        event_id=bet_request.event_id,
        amount=float(bet_request.amount),
        status=BetStatus.PENDING.value
    )


@router.get("/", response_model=List[BetHistoryResponse], tags=["Bets"])
async def get_bets() -> List[BetHistoryResponse]:
    """
    Возвращает историю всех ставок.

    :return: Список объектов BetHistoryResponse, представляющих историю ставок.
    """
    query = "SELECT bet_id, event_id, amount, status FROM bets;"
    rows = await database.fetch_all(query=query)
    return [
        BetHistoryResponse(
            bet_id=str(row["bet_id"]),
            event_id=row["event_id"],
            amount=row["amount"],
            status=BetStatus(row["status"])
        )
        for row in rows
    ]


@router.get("/{bet_id}", response_model=Bet, tags=["Bets"])
async def get_bet(bet_id: int) -> Bet:
    """
    Возвращает информацию о ставке по идентификатору.

    :param bet_id: Уникальный идентификатор ставки.
    :return: Объект Bet с информацией о ставке.
    :raises HTTPException: Если ставка с указанным идентификатором не найдена.
    """
    query = "SELECT bet_id, event_id, amount, status FROM bets WHERE bet_id = :bet_id"
    row = await database.fetch_one(query=query, values={"bet_id": bet_id})

    if not row:
        raise HTTPException(status_code=404, detail="Bet not found")

    return Bet(
        bet_id=str(row["bet_id"]),
        event_id=row["event_id"],
        amount=row["amount"],
        status=row["status"]
    )


@router.post("/update", tags=["Bets"])
async def update_bet_status(event_update: Dict[str, str]) -> Dict[str, str]:
    """
    Обновляет статусы ставок, связанных с завершенным событием.

    :param event_update: Словарь с идентификатором события и новым статусом.
    :return: Словарь с сообщением об успешном обновлении статусов.
    :raises HTTPException: Если новый статус недействителен или обновление не удалось.
    """
    event_id = event_update["event_id"]
    new_status = event_update["status"]

    if new_status == "finished_win":
        bet_status = BetStatus.WON.value
    elif new_status == "finished_lose":
        bet_status = BetStatus.LOST.value
    else:
        raise HTTPException(status_code=400, detail="Invalid event status")

    query = """
    UPDATE bets
    SET status = :status
    WHERE event_id = :event_id AND status = 'pending';
    """

    await database.execute(query=query, values={"status": str(bet_status), "event_id": event_id})

    return {"message": f"Bets for event '{event_id}' updated to {bet_status}"}

