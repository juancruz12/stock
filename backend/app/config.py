from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración de la aplicación leída desde variables de entorno."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Conexión directa por URL (tiene prioridad si está definida).
    # Ej: postgresql+psycopg://user:pass@host:5432/dbname
    database_url: str | None = None

    # Componentes individuales (usados si no hay database_url).
    db_user: str = "postgres"
    db_password: str = "postgres"
    db_name: str = "postgres"
    db_host: str = "localhost"
    db_port: int = 5432

    # Nombre de conexión de la instancia de Cloud SQL.
    # Ej: project:region:instance
    # Si está definido, se conecta vía socket Unix en /cloudsql.
    cloud_sql_connection_name: str | None = None

    def build_database_url(self) -> str:
        if self.database_url:
            return self.database_url

        if self.cloud_sql_connection_name:
            # Cloud Run monta el socket de Cloud SQL en /cloudsql/<conn-name>.
            socket_path = f"/cloudsql/{self.cloud_sql_connection_name}"
            return (
                f"postgresql+psycopg://{self.db_user}:{self.db_password}"
                f"@/{self.db_name}?host={socket_path}"
            )

        return (
            f"postgresql+psycopg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
