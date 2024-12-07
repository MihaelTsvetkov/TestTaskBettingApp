from pydantic import PostgresDsn, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Настройки приложения, включая параметры подключения к базе данных
    и конфигурацию хоста приложения.
    """

    POSTGRES_USER: str = Field(..., env="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field(..., env="POSTGRES_PASSWORD")
    POSTGRES_HOST: str = Field(..., env="POSTGRES_HOST")
    POSTGRES_PORT: int = Field(..., env="POSTGRES_PORT")
    POSTGRES_DB: str = Field(..., env="POSTGRES_DB")

    @property
    def DATABASE_URL(self) -> str:
        """
        Возвращает строку подключения к PostgreSQL.
        """
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    APP_HOST: str = Field(default="0.0.0.0", env="APP_HOST")
    APP_PORT: int = Field(default=8000, env="APP_PORT")

    class Config:
        """
        Конфигурация для загрузки переменных окружения из файла.
        """
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

