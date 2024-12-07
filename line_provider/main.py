from fastapi import FastAPI
from routers.events import router

app = FastAPI(
    title="Line Provider Service",
    description="Сервис для работы с линиями событий",
    version="1.0.0"
)

app.include_router(router, prefix="/events", tags=["events"])


@app.get("/", tags=["Root"])
async def read_root() -> dict:
    """
    Возвращает приветственное сообщение.
    """
    return {"message": "Welcome to the Line Provider Service!"}

