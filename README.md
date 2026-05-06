# FastAPI Auth Service

A containerized REST API with JWT authentication, Role-Based Access Control (RBAC), MySQL database, Alembic migrations, and microservice communication, all orchestrated with Docker Compose.

---

## Tech Stack

| Technology | Purpose |
|---|---|
| FastAPI | Web framework |
| SQLAlchemy | ORM (database interface) |
| Alembic | Database migrations |
| MySQL 8.0 | Database (runs in Docker) |
| JWT (python-jose) | Authentication tokens |
| bcrypt (passlib) | Password hashing |
| Docker + Docker Compose | Containerization |
| httpx | Inter-service HTTP communication |

---

## Services

| Service | Port | Description |
|---|---|---|
| `api` | 8000 | Main FastAPI app (auth + protected routes) |
| `service2` | 8001 | Second microservice (communicates with api) |
| `mysql` | 3306 | MySQL database (internal only, not exposed) |

---

## Project Structure

```
task2/
├── app/                        # Main API service
│   ├── api/
│   │   ├── auth.py             # POST /auth/signup, POST /auth/login
│   │   └── routes.py           # Protected endpoints
│   ├── core/
│   │   ├── config.py           # App settings and env vars
│   │   ├── security.py         # JWT creation, password hashing
│   │   └── dependencies.py     # Auth guards (get_current_user, require_role)
│   ├── db/
│   │   └── database.py         # Database connection setup
│   ├── models/
│   │   └── user.py             # SQLAlchemy User model
│   ├── schemas/
│   │   └── user.py             # Pydantic request/response schemas
│   └── main.py                 # App entry point
├── service2/                   # Second microservice
│   ├── app/
│   │   └── main.py             # Service2 endpoints
│   ├── Dockerfile
│   └── requirements.txt
├── alembic/                    # Database migrations
│   ├── versions/               # Migration files
│   └── env.py                  # Alembic configuration
├── alembic.ini                 # Alembic settings
├── docker-compose.yml          # All services, networks, volumes
├── Dockerfile                  # Main API container
└── requirements.txt            # Python dependencies
```

---

## Docker Networks

| Network | Type | Used By |
|---|---|---|
| `frontend` | bridge | api, service2 (exposed to outside) |
| `backend` | bridge | api, mysql (internal only) |

MySQL is only on the backend network, it cannot be reached directly from outside Docker. Only the `api` container can talk to it.

---

## Prerequisites

- Docker Desktop installed and running
- Git installed
- No need to install Python or MySQL locally, Docker handles everything

---

## Deployment Steps

### 1. Clone the repository
```bash
git clone https://github.com/FurqanRaufHere/wanclouds-project.git
cd wanclouds-project
```

### 2. Start all services
```bash
docker-compose up --build
```

This will:
- Build the `api` and `service2` containers
- Pull the `mysql:8.0` image
- Create `frontend` and `backend` Docker networks
- Start all 3 containers

### 3. Run database migrations
Open a new terminal and run:
```bash
docker exec -it fastapi_app alembic upgrade head
```

This creates the `users` table in MySQL.

### 4. Verify everything is running
```bash
docker ps
```

You should see 3 containers running:
- `fastapi_app` on port 8000
- `fastapi_service2` on port 8001
- `mysql_db` on port 3306

### 5. Access the API
- Swagger UI (Service 1): `http://localhost:8000/docs`
- Swagger UI (Service 2): `http://localhost:8001/docs`

---

## API Endpoints

### Auth (Public — no token needed)

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/signup` | Create a new user account |
| POST | `/auth/login` | Login and receive JWT token |

**Signup request body:**
```json
{
  "username": "ali",
  "email": "ali@example.com",
  "password": "secret123"
}
```

**Login request body:**
```json
{
  "email": "ali@example.com",
  "password": "secret123"
}
```

**Login response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

### Protected (Requires Bearer Token)

Add this header to all protected requests:
```
Authorization: Bearer <your_access_token>
```

| Method | Endpoint | Role Required | Description |
|---|---|---|---|
| GET | `/hello` | any user | Personalized hello message |
| GET | `/status` | any user | Service status |
| POST | `/predict` | any user | Mock prediction |
| GET | `/admin` | admin only | Admin panel |

### Service 2

| Method | Endpoint | Description |
|---|---|---|
| GET | `/ping` | Service2 health check |
| GET | `/fetch-status` | Calls Service1 /status internally |
| GET | `/fetch-hello` | Calls Service1 /hello internally |

---

## Database Access (CLI)

Connect to MySQL directly:
```bash
docker exec -it mysql_db mysql -u appuser -papppassword appdb
```

Useful SQL commands:
```sql
SHOW TABLES;
DESCRIBE users;
SELECT id, username, email, role FROM users;
```

---

## Stopping the Services

```bash
docker-compose down
```