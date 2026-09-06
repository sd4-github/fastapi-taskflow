# TaskFlow — FastAPI: Interview Topics Covered

> Pure-backend FastAPI task manager. **Basic → Intermediate → Advanced**, ~5 YOE depth.
> Each row maps a likely **interview question/topic** to the **file(s)** where it's answered in code.
> Relative links are from the project root `1_fastapi_taskflow/`.

---

## 1. Python fundamentals
| Topic / question | Where covered |
|------------------|---------------|
| Types, collections, f-strings, comprehensions | [python_scripts/01_basics.py](python_scripts/01_basics.py) |
| Functions, `*args/**kwargs`, generators, decorators, typing | [python_scripts/02_intermediate.py](python_scripts/02_intermediate.py) (FastAPI) |
| Async/await, `asyncio`, concurrency vs parallelism | [python_scripts/03_async_advanced.py](python_scripts/03_async_advanced.py) |

## 2. FastAPI framework
| Topic / question | Where covered |
|------------------|---------------|
| App lifecycle / `FastAPI()` wiring | [src/app/main.py](src/app/main.py) |
| Path & query params, request body, models | [src/app/routers/basic.py](src/app/routers/basic.py) |
| Pydantic schemas (validation, nested, `Config`) | [src/app/schemas/](src/app/schemas/) |
| Path/query/body parameter precedence | [src/app/routers/tasks.py](src/app/routers/tasks.py) |
| Dependency injection (`Depends`) | [src/app/api/deps.py](src/app/api/deps.py) |
| Router organization / APIRouter | [src/app/routers/](src/app/routers/) |
| Settings via pydantic-settings / env config | [src/app/core/config.py](src/app/core/config.py) |
| SQLAlchemy async database session | [src/app/core/database.py](src/app/core/database.py) |
| CRUD / service layer | [src/app/services/crud.py](src/app/services/crud.py) |
| Schema migration? (outside scope — see ARCHITECTURE.md) | [ARCHITECTURE.md](ARCHITECTURE.md) |

## 3. Advanced FastAPI topics
| Topic / question | Where covered |
|------------------|---------------|
| Async endpoints & concurrency (`await`, parallel) | [src/app/routers/advanced.py](src/app/routers/advanced.py) |
| Background tasks (`BackgroundTasks`) | [src/app/routers/advanced.py](src/app/routers/advanced.py) |
| File upload (`UploadFile`, streaming) | [src/app/routers/advanced.py](src/app/routers/advanced.py) |
| Redis caching of expensive operation | [src/app/routers/advanced.py](src/app/routers/advanced.py) |
| Rate limiting (custom middleware/dependency) | [src/app/routers/advanced.py](src/app/routers/advanced.py) |
| Celery task queue | [src/app/celery_app.py](src/app/celery_app.py) |

## 4. Auth & security
| Topic / question | Where covered |
|------------------|---------------|
| Password hashing (bcrypt/passlib) | [src/app/core/security.py](src/app/core/security.py) |
| JWT issuance & verification | [src/app/core/security.py](src/app/core/security.py) |
| Login / token endpoints | [src/app/routers/auth.py](src/app/routers/auth.py) |
| Current-user dependency / auth guard | [src/app/api/deps.py](src/app/api/deps.py) |
| Token schemas | [src/app/schemas/token.py](src/app/schemas/token.py) |

## 5. Models & DB
| Topic / question | Where covered |
|------------------|---------------|
| ORM model definitions (User/Task) | [src/app/models/](src/app/models/) |
| Relationships (FK between Task & User) | [src/app/models/task.py](src/app/models/task.py) |

## 6. Testing & docs
| Topic / question | Where covered |
|------------------|---------------|
| TestClient-based API tests | [src/tests/test_api.py](src/tests/test_api.py) |
| Auth + task flow tests | [src/tests/test_auth_tasks.py](src/tests/test_auth_tasks.py) |
| Test fixtures (DB fixtures, client fixture) | [src/tests/conftest.py](src/tests/conftest.py) |
| Full-stack smoke test of every feature | [smoke_test.py](smoke_test.py) |

---

### How to explore
Start with `python_scripts/01_basics.py` → read the app `src/app/main.py` in file order → then per-feature router files. Every file is heavily commented with **why**, not just *what*.
