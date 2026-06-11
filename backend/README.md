# Stock API

API básica de stock con **FastAPI** + **PostgreSQL**, lista para desplegar en **Cloud Run**.

## Estructura

```
backend/
  app/
    config.py     # Configuración por variables de entorno
    database.py   # Engine y sesión de SQLAlchemy
    models.py     # Tabla `stock` (descripcion, cantidad, precio)
    schemas.py    # Modelos Pydantic (validación)
    crud.py       # Operaciones de base de datos
    main.py       # App FastAPI y endpoints
  Dockerfile
  requirements.txt
```

## Tabla `stock`

| Columna     | Tipo          | Notas              |
|-------------|---------------|--------------------|
| id          | serial        | PK autoincremental |
| descripcion | varchar(255)  | requerido          |
| cantidad    | integer       | >= 0               |
| precio      | numeric(12,2) | >= 0               |

La tabla se crea automáticamente al iniciar la app.

## Endpoints

| Método | Ruta               | Descripción              |
|--------|--------------------|--------------------------|
| GET    | `/`                | Estado del servicio      |
| GET    | `/health`          | Healthcheck + chequeo DB |
| GET    | `/stock`           | Lista (paginada)         |
| GET    | `/stock/{id}`      | Obtiene uno              |
| POST   | `/stock`           | Crea                     |
| PUT    | `/stock/{id}`      | Actualiza (parcial)      |
| DELETE | `/stock/{id}`      | Elimina                  |

Docs interactivas en `/docs`.

## Desarrollo local

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # ajustá las credenciales

# Postgres rápido con Docker:
docker run --name stock-pg -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres:16

uvicorn app.main:app --reload --port 8080
```

## Despliegue en Cloud Run

Requisitos: una instancia de **Cloud SQL (PostgreSQL)** y `gcloud` configurado.

```bash
PROJECT_ID=mi-proyecto
REGION=us-central1
INSTANCE=mi-proyecto:us-central1:mi-instancia

# 1. Build & push de la imagen (Artifact Registry)
gcloud builds submit --tag $REGION-docker.pkg.dev/$PROJECT_ID/apps/stock-api ./backend

# 2. Deploy a Cloud Run con conexión a Cloud SQL
gcloud run deploy stock-api \
  --image $REGION-docker.pkg.dev/$PROJECT_ID/apps/stock-api \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --add-cloudsql-instances $INSTANCE \
  --set-env-vars CLOUD_SQL_CONNECTION_NAME=$INSTANCE,DB_USER=postgres,DB_NAME=postgres \
  --set-secrets DB_PASSWORD=stock-db-password:latest
```

Notas:
- Cloud Run inyecta `PORT` (8080); el contenedor ya lo respeta.
- Con `--add-cloudsql-instances` se monta el socket en `/cloudsql/<conn>`, y `config.py` arma la URL de conexión vía ese socket.
- Guardá `DB_PASSWORD` en **Secret Manager** en vez de pasarla en texto plano.

