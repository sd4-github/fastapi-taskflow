# TaskFlow API — Architecture & Implementation Guide

A **pure-backend** FastAPI demo API built to teach every essential feature from
**basic → intermediate → advanced**, as needed for a 5-YOE backend interview.

> Read top-to-bottom. Each section explains **what**, **why**, and **where** in code.

---

## 1. Project layout (what each folder does)

```
1_fastapi_taskflow/
├── src/app/                  # the actual application (a Python package)
│   ├── main.py               # app entry: routers, middleware, lifespan, handlers
│   ├── api/
│   │   └── deps.py           # FastAPI dependencies (auth + DB injection)
│   ├── core/
│   │   ├── config.py         # typed settings from env / .env (pydantic-settings)
│   │   ├── database.py       # SQLAlchemy engine + session + get_db dependency
│   │   └── security.py       # JWT create/decode + password hashing (bcrypt)
│   ├── models/               # SQLAlchemy ORM models (User, Task)
│   ├── schemas/              # Pydantic schemas (request/response validation)
│   ├── services/crud.py      # business logic / DB access layer (thin routers)
│   ├── routers/
│   │   ├── basic.py          # LEVEL 1  — basics: params, body, in-memory CRUD
│   │   ├── tasks.py          # LEVEL 2-3— DB CRUD + JWT auth + ownership
│   │   ├── auth.py           # LEVEL 3  — register/login, JWT issue
│   │   └── advanced.py       # LEVEL 3  — Redis, background tasks, uploads,
│   │                         #            websockets, rate limiting
│   └── celery_app.py         # durable distributed background tasks (Celery)
├── tests/                    # pytest suite (HTTP-level, isolated test DB)
├── python_scripts/           # Python fundamentals: 01 basics, 02 intermediate, 03 async
├── smoke_test.py             # verifies the advanced features end-to-end
├── run_dev.py                # one-command dev boot
├── .env / .gitignore / requirements.txt / pyproject.toml
└── .venv/                    # isolated virtual environment
```

### Layered architecture (the interview answer)
```
Client (JSON)  ->  Routers (HTTP only)  ->  Services (business logic + DB)
                     ^                        |
                     |                        v
               Dependencies (auth/db)    Models (ORM) -> Postgres
```
- **Routers = thin**: they parse input via Pydantic schemas, call a service, and
  serialize output. No SQL, no business rules inside routers.
- **Services = logic**: where queries and rules live. Testable without HTTP.
- **Dependencies = context**: `get_db`, `get_current_user` inject what endpoints
  need without repeating boilerplate (the Dependency-Injection pattern).

---

## 2. Feature walkthrough (basic → advanced)

### LEVEL 1 — Basics (`routers/basic.py`)
| Feature | Where | What it teaches |
|---|---|---|
| HTTP verbs | `@router.get/post/put/delete` | Maps URL paths to handler functions |
| Path params | `/items/{item_id}` | Dynamic URL segments |
| Query params | `?skip=0&limit=10` | Optional typed URL query, with validation |
| Request body | Pydantic `Item` model | JSON body parsed + validated automatically |
| Validation | `Field(gt=0, min_length=...)` | Input constraints; bad input → HTTP 422 |
| Auto-docs | `/docs`, `/redoc` | Interactive Swagger/OpenAPI generated for free |
| Status codes | `status.HTTP_201_CREATED` | Semantic HTTP responses |

### LEVEL 2 — Intermediate (`routers/tasks.py`, `core/database.py`)
| Feature | Where | What it teaches |
|---|---|---|
| SQLAlchemy ORM | `models/task.py` | Python classes ↔ Postgres tables |
| Sessions | `core/database.py` `get_db` | Request-scoped "unit of work"; `yield` cleanup |
| Pydantic schemas | `schemas/` | Enforce request/response shapes |
| `response_model` | `tasks.py` | Validate + serialize what the API returns |
| Pagination/filter | `TaskService.list` | `offset/limit` + dynamic `WHERE` clauses |
| Row-level ownership | filter by `owner_id` | Users only see/write their own data |

### LEVEL 3 — Advanced
| Feature | Where | What it teaches |
|---|---|---|
| JWT auth | `core/security.py`, `api/deps.py` | Stateless signed tokens; scopes/roles |
| Dependency injection | `api/deps.py` | Compose `get_db` → `get_current_user` |
| Background tasks | `routers/advanced.py` | Fire-and-forget work after the response |
| Redis caching | `routers/advanced.py` | Cache slow responses; invalidation |
| File uploads | `routers/advanced.py` | Multipart `UploadFile`, streaming |
| WebSockets | `routers/advanced.py` | Real-time bidirectional connection |
| Rate limiting | `routers/advanced.py` | Redis counter + TTL → HTTP 429 |
| Middleware | `main.py` | Code running on every request (logging, timing) |
| Global handlers | `main.py` | Central error handling, clean 500s |
| Lifespan | `main.py` | Startup/shutdown hooks (DB init) |
| Celery | `celery_app.py` | Durable, retryable, scalable background queue |

---

## 3. Security model (JWT, the interview favourite)

1. **Register** → store a **bcrypt hash** of the password (`core/security.py`)
   — never plaintext.
2. **Login** → verify, then **sign a JWT** embedding `sub` (user id) + `exp`.
3. **Every protected route** → dependency `get_current_user_required` decodes the
   `Authorization: Bearer <token>`, verifies signature + expiry, loads the user.
4. **Result:** stateless — the server stores no session; any node can verify a
   request. Signature is derived from `SECRET_KEY`, so clients can't forge tokens.

---

## 4. Database & Redis

- **Postgres** `taskflow` DB (SQLAlchemy `postgresql+psycopg2://...`).
- **Redis** via Docker (`redis-interview` container on port 6379) for caching,
  rate limiting, and as the Celery broker.
- Tables are created on startup for dev (`init_db`). In production, use
  **Alembic migrations** (schema versioning).

---

## 5. How to run it

```bash
cd 1_fastapi_taskflow
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python run_dev.py        # or: .venv/bin/uvicorn app.main:app --reload --app-dir src
# docs -> http://127.0.0.1:8000/docs
```

### Run tests
```bash
cd src && ../.venv/bin/python -m pytest -q
```

### Verify advanced features
```bash
.venv/bin/python smoke_test.py     # caching, background, upload, rate-limit
```

---

## 6. Interview Q&A this project prepares you for

- What's the difference between sync and async endpoints in FastAPI?
- How does FastAPI's dependency injection work? Why `yield` for DB sessions?
- Why is JWT "stateless"? What's in a token? How do you revoke one?
- How do you scale reads? (Redis cache) / do background work? (Celery)
- How do you add auth and row-level permission to an API?
- How do you write and isolate tests? (transaction rollback per test)
- Layered/clean architecture vs putting everything in the router — pros/cons.
