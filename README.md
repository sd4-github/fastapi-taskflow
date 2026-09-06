# TaskFlow API

A **FastAPI** task management REST API built for backend interview preparation (~5 YOE depth). Progresses from basic routing through intermediate ORM patterns to advanced features like JWT auth, WebSockets, Redis caching, and rate limiting.

[GitHub](https://github.com/sd4-github/fastapi-taskflow)

## What It Does

- **Register & login** with email/password (JWT-based auth)
- **CRUD tasks** with ownership enforcement — users only see their own tasks
- **Advanced features**: Redis caching, background tasks, file uploads, WebSockets, rate limiting

## Tech Stack

| Layer | Tech |
|-------|------|
| Framework | [FastAPI](https://fastapi.tiangolo.com/) 0.111 |
| ASGI Server | Uvicorn |
| ORM | SQLAlchemy 2.0 |
| Database | PostgreSQL |
| Auth | JWT (python-jose + bcrypt) |
| Caching | Redis |
| Background Tasks | FastAPI BackgroundTasks + Celery |
| Testing | pytest + httpx |

## Project Structure

```
src/
├── app/
│   ├── api/deps.py          # Dependency injection (auth, DB sessions)
│   ├── core/
│   │   ├── config.py        # pydantic-settings config from env
│   │   ├── database.py      # SQLAlchemy engine + session
│   │   └── security.py      # JWT creation/verification + password hashing
│   ├── models/              # SQLAlchemy ORM models (User, Task)
│   ├── routers/
│   │   ├── basic.py         # Level 1: HTTP methods, path/query params
│   │   ├── auth.py          # Register + login (OAuth2 password flow)
│   │   ├── tasks.py         # Level 2: CRUD with DB, pagination, ownership
│   │   └── advanced.py      # Level 3: Cache, uploads, WebSockets, rate limiting
│   ├── schemas/             # Pydantic request/response models
│   └── services/crud.py     # Business logic layer
└── tests/                   # pytest test suite
```

## Quick Start

```bash
# Prerequisites: PostgreSQL + Redis running locally

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Start the dev server (auto-creates tables)
python run_dev.py
```

API available at [http://127.0.0.1:8000](http://127.0.0.1:8000) | Swagger docs at [/docs](http://127.0.0.1:8000/docs)

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/` | No | Root info |
| `GET` | `/health` | No | Health check |
| `POST` | `/auth/register` | No | Register user |
| `POST` | `/auth/login` | No | Login (returns JWT) |
| `POST` | `/tasks` | Yes | Create task |
| `GET` | `/tasks` | Yes | List tasks (paginated, filterable) |
| `GET` | `/tasks/{id}` | Yes | Get task |
| `PATCH` | `/tasks/{id}` | Yes | Update task |
| `DELETE` | `/tasks/{id}` | Yes | Delete task |
| `GET` | `/advanced/cached-time` | Yes | Redis-cached endpoint |
| `POST` | `/advanced/upload` | Yes | File upload |
| `WS` | `/advanced/ws/echo/{client}` | Yes | WebSocket echo |
| `GET` | `/advanced/rate-limited` | Yes | Rate-limited endpoint |

## Interview Topics Covered

- Python fundamentals, async/await, decorators
- FastAPI dependency injection, Pydantic validation
- SQLAlchemy ORM, relationships, session management
- JWT authentication, password hashing, role-based access
- Redis caching, cache invalidation
- WebSockets, background tasks, file uploads
- Rate limiting, middleware, CORS
- Testing with pytest + TestClient

See [INTERVIEW_TOPICS.md](INTERVIEW_TOPICS.md) for the full topic-to-file mapping.

## More Projects

- [TakkarCV](https://github.com/sd4-github/takkarcv)
- [Keycloak RBAC Django Auth](https://github.com/sd4-github/keycloak-rbac-django-auth)
- [Bulk Contract Processing](https://github.com/sd4-github/bulk-contract-processing)
- [Contract Processing](https://github.com/sd4-github/contract-processing)

## Built With

Made with [OpenCode](https://opencode.ai).
