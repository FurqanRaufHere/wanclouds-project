# Vehicle Discovery Service

A containerized REST API that ingests car data from Back4App on a schedule and
exposes it behind JWT authentication. FastAPI + MySQL + Celery, orchestrated
with Docker Compose.

---

## Tech Stack

| Technology | Purpose |
|---|---|
| FastAPI | Web framework |
| SQLAlchemy | ORM |
| Alembic | Database migrations |
| MySQL 8.0 | Database |
| Celery | Background task queue |
| Celery Beat | Task scheduler |
| Redis | Celery broker and result backend |
| JWT (python-jose) | Authentication tokens |
| bcrypt (passlib) | Password hashing |
| Docker Compose | Orchestration |

---

## Services

| Container | Port | Description |
|---|---|---|
| `web` | 8000 | FastAPI app — auth and cars endpoints |
| `vehicle_discovery_worker` | — | Celery worker, executes the fetch task |
| `vehicle_discovery_beat` | — | Celery beat, triggers the task every 24h |
| `redis` | — | Celery broker/backend |
| `mysql_db` | — | MySQL 8.0 |

All five share a single `app_network` bridge network. Only `web` publishes a
port; MySQL and Redis are reachable only from inside the network.

---

## How the data gets in

`vehicle_discovery_beat` fires the `fetch_cars` task every 24 hours. The worker
pages through Back4App's `Car_Model_List` class 100 records at a time and
writes new cars into MySQL, skipping any `objectId` already stored.

Make, model, and year are **normalized** rather than stored as strings on each
car — they live in `car_makes`, `car_models`, and `car_years`, and `cars` holds
foreign keys. The three form a hierarchy: a model belongs to a make, a year
belongs to a model.

```
car_makes ──< car_models ──< car_years
     ▲             ▲             ▲
     └─────────── cars ──────────┘
              (make_id, model_id, year_id)
```

To run the fetch immediately instead of waiting for the schedule:

```bash
docker exec -it vehicle_discovery_worker python -c \
  "from app.tasks.fetch_cars import fetch_cars_task; print(fetch_cars_task.delay())"
```

---

## Project Structure

```
task2/
├── app/
│   ├── api/
│   │   ├── auth/               # POST /auth/signup, POST /auth/login
│   │   └── cars/               # GET /cars/, GET|PUT|DELETE /cars/{id}
│   ├── common/
│   │   └── schemas.py          # Page-based pagination query + response envelope
│   ├── core/
│   │   ├── config.py           # Env vars and connection strings
│   │   ├── dependencies.py     # get_current_user, @authenticate
│   │   └── security.py         # JWT creation/decoding, password hashing
│   ├── db/
│   │   ├── base.py             # SQLAlchemy declarative Base
│   │   └── database.py         # Engine and session factory
│   ├── models/                 # User, Car, CarMake, CarModel, CarYear
│   ├── tasks/
│   │   └── fetch_cars.py       # Celery task pulling from Back4App
│   ├── celery_app.py           # Celery config and beat schedule
│   └── main.py                 # App entry point
├── alembic/versions/           # Migrations
├── scripts/                    # Container entrypoints (web, worker, beat)
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

---

## Setup

### 1. Clone

```bash
git clone https://github.com/FurqanRaufHere/wanclouds-project.git
cd wanclouds-project
```

### 2. Configure environment

```bash
cp .env.example .env
```

Then edit `.env` and fill in the blanks:

| Variable | Notes |
|---|---|
| `SECRET_KEY` | Generate: `python -c "import secrets; print(secrets.token_urlsafe(32))"` |
| `BACK4APP_APP_ID` | Back4App dashboard → App Settings → Security & Keys |
| `BACK4APP_MASTER_KEY` | Same page |

The MySQL and Redis values in `.env.example` already match `docker-compose.yml`
and work as-is.

### 3. Start

```bash
docker-compose up --build
```

`web` waits for MySQL to accept connections, runs `alembic upgrade head`, then
starts uvicorn. No manual migration step needed.

### 4. Verify

```bash
docker ps
```

Five containers should be running. Then open <http://localhost:8000/docs>.

---

## API

### Auth — public

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/auth/signup` | Create an account |
| `POST` | `/auth/login` | Exchange credentials for a JWT |

```bash
curl -X POST localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"ali","email":"ali@example.com","password":"secret123"}'

curl -X POST localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"ali@example.com","password":"secret123"}'
```

Login returns:

```json
{ "access_token": "eyJhbGciOiJIUzI1NiJ9...", "token_type": "bearer" }
```

### Cars — requires `Authorization: Bearer <token>`

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/cars/` | List cars, paginated |
| `GET` | `/cars/{car_id}` | Fetch a single car |
| `PUT` | `/cars/{car_id}` | Update a car |
| `DELETE` | `/cars/{car_id}` | Delete a car |

**Pagination** — `page` (1-based, default 1) and `limit` (default 20, max 100):

```bash
curl "localhost:8000/cars/?page=1&limit=20" \
  -H "Authorization: Bearer $TOKEN"
```

```json
{
  "total": 4821,
  "page": 1,
  "pages": 242,
  "limit": 20,
  "items": [
    { "id": "a3f...", "make": "Toyota", "model": "Corolla", "category": "Sedan", "year": 2020 }
  ]
}
```

Results are ordered by `id` so a row never lands on two pages. Each page is a
single query — make, model, and year are joined in, not lazy-loaded per row.

**Fetch one** — same shape as a single `items` entry, `404` if the id is unknown:

```bash
curl localhost:8000/cars/a3f... -H "Authorization: Bearer $TOKEN"
```

**Update** — all fields optional; only what you send is changed. Passing a new
`make`/`model`/`year` creates the lookup rows if they don't exist yet.

```bash
curl -X PUT localhost:8000/cars/a3f... \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"category":"Hatchback"}'
```

Returns `404` if the id is unknown. `DELETE` returns `204` with no body.

---

## Database Access

```bash
docker exec -it mysql_db mysql -u appuser -papppassword appdb
```

```sql
SHOW TABLES;
SELECT COUNT(*) FROM cars;

SELECT c.id, mk.name AS make, md.name AS model, y.year, c.category
FROM cars c
JOIN car_makes  mk ON mk.id = c.make_id
JOIN car_models md ON md.id = c.model_id
LEFT JOIN car_years y ON y.id = c.year_id
LIMIT 10;
```

---

## Common Tasks

```bash
# Follow logs for one service
docker-compose logs -f web
docker-compose logs -f vehicle_discovery_worker

# Create a migration after changing a model
docker exec -it web alembic revision --autogenerate -m "describe the change"
docker exec -it web alembic upgrade head

# Stop everything (add -v to also drop the MySQL volume)
docker-compose down
```
