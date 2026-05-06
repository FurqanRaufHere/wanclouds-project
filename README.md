# FastAPI Auth Service

A containerized REST API with JWT authentication, RBAC, and microservice communication.

## Stack
- FastAPI, SQLAlchemy, Alembic
- MySQL (Docker)
- JWT + bcrypt
- Docker Compose

## Services
| Service | Port | Description |
|---|---|---|
| api | 8000 | Main auth API |
| service2 | 8001 | Secondary microservice |
| mysql | 3306 | Database (internal only) |

## Setup

```bash
docker-compose up --build
```

Run migrations:
```bash
docker exec -it fastapi_app alembic upgrade head
```

## API Endpoints

**Auth (public)**
- `POST /auth/signup` — create account
- `POST /auth/login` — get JWT token

**Protected (requires Bearer token)**
- `GET /hello` — personalized hello
- `GET /status` — service status
- `POST /predict` — mock prediction
- `GET /admin` — admin only

**Service 2**
- `GET /ping` — health check
- `GET /fetch-status` — calls service 1 internally

## Database Access
```bash
docker exec -it mysql_db mysql -u appuser -papppassword appdb
```
```sql
SELECT * FROM users;
```

## Project Structure
```
├── app/              # Main API service
│   ├── api/          # Routes and auth endpoints
│   ├── core/         # JWT, security, config
│   ├── db/           # Database connection
│   ├── models/       # SQLAlchemy models
│   └── schemas/      # Pydantic schemas
├── service2/         # Second microservice
├── alembic/          # Database migrations
└── docker-compose.yml
```