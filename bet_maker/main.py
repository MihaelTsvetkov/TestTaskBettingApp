from fastapi import FastAPI
from routers.bets import router as bets_router
from routers.events import router as events_router
from provider.database import database
from config import settings

app = FastAPI(
    title="Bet Maker Service",
    description="Сервис для работы с ставками",
    version="1.0.0"
)

app.include_router(bets_router, prefix="/bets", tags=["Bets"])
app.include_router(events_router, prefix="/get_events", tags=["Events"])


@app.on_event("startup")
async def startup() -> None:
    """
    Подключение к базе данных при запуске приложения.
    """
    await database.connect()


@app.on_event("shutdown")
async def shutdown() -> None:
    """
    Отключение от базы данных при остановке приложения.
    """
    await database.disconnect()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.APP_HOST, port=settings.APP_PORT)

