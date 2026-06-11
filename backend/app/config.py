from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración de la aplicación leída desde variables de entorno."""

    # 🎯 ALERTA CLAVE: Agregamos case_sensitive=False para que a Pydantic no le importe
    # si desde Terraform le mandás en mayúsculas o minúsculas.
    model_config = SettingsConfigDict(
        env_file=".env", 
        extra="ignore",
        case_sensitive=False  # <--- AGREGÁ ESTO
    )

    # Conexión directa por URL
    DATABASE_URL: str | None = None

    # Componentes individuales
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_NAME: str = "postgres"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432

    # Pasamos esta también a mayúsculas para mantener el estándar limpio
    CLOUD_SQL_CONNECTION_NAME: str | None = None

    def build_database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL

        if self.CLOUD_SQL_CONNECTION_NAME:
            # Cloud Run monta el socket de Cloud SQL en /cloudsql/<conn-name>.
            socket_path = f"/cloudsql/{self.CLOUD_SQL_CONNECTION_NAME}"
            return (
                f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASSWORD}"
                f"@/{self.DB_NAME}?host={socket_path}"
            )

        return (
            f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()