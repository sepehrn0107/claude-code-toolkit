# Python + FastAPI Standards

Standards for projects using Python with FastAPI.

## Forbidden Calls

### `datetime.utcnow()` — deprecated, never use

```python
# ❌ wrong — deprecated in Python 3.12, removes timezone info
from datetime import datetime
datetime.utcnow()

# ✅ correct
from datetime import datetime, timezone
datetime.now(timezone.utc)
```

Always import `timezone` from `datetime` and use `datetime.now(timezone.utc)` for all timestamp columns, Celery payloads, and audit fields.

### `torch.load()` without `weights_only=True` — security risk

```python
# ❌ wrong — arbitrary code execution via pickle
torch.load(path)
torch.load(path, map_location="cpu")

# ✅ correct
torch.load(path, map_location="cpu", weights_only=True)
```

---

## SQLite with FastAPI/SQLAlchemy — always add `check_same_thread: False`

SQLite objects cannot be shared across threads by default. FastAPI's threaded worker model will raise `sqlite3.ProgrammingError` without this flag.

```python
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
```

Apply this pattern everywhere a SQLAlchemy engine is created from an env-var URL.

---

## Test Isolation with SQLite + StaticPool

For API tests that use SQLAlchemy, use an in-memory SQLite engine with `StaticPool` to keep all connections on the same in-memory DB:

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

Use a **function-scoped** fixture that truncates all tables between tests (not just rolls back — `ROLLBACK` doesn't reset autoincrement in SQLite):

```python
@pytest.fixture
def db():
    session = TestingSessionLocal()
    yield session
    session.rollback()
    for table in reversed(Base.metadata.sorted_tables):
        session.execute(table.delete())
    session.commit()
    session.close()
```

Override `get_db` in the FastAPI test client:

```python
app.dependency_overrides[get_db] = lambda: db_fixture
```

---

## Alembic — always verify migration content

Never commit a migration where `upgrade()` contains only `pass`. After `alembic revision --autogenerate`, verify the generated file contains `op.create_table` or `op.add_column` calls before committing.

```bash
# Verify migration is non-empty
grep -q "op\." migrations/versions/*.py || echo "WARNING: migration may be empty"
```

If `--autogenerate` produces an empty migration, check that `target_metadata = Base.metadata` is set in `alembic/env.py` and that all models are imported before `Base.metadata` is read.

---

## Dependency Injection

- Use `Depends()` for all cross-cutting concerns: auth, DB session, tenant validation
- Never instantiate `SessionLocal()` inside route handlers — always use `Depends(get_db)`
- Auth middleware: always call `algorithms=[JWT_ALG]` explicitly in `jwt.decode()` to prevent algorithm-confusion attacks

---

## Project Structure

```
api/
  main.py        — FastAPI app factory, router registration
  db.py          — engine, SessionLocal, Base
  models.py      — SQLAlchemy ORM models
  deps.py        — shared Depends() factories (get_db, get_current_principal)
  security.py    — JWT encode/decode, password hashing
  routes/        — one file per resource (jobs.py, auth.py, blob.py)
worker/
  celery_app.py  — Celery app factory
  tasks.py       — @app.task definitions
tests/
  api/
    conftest.py  — in-memory engine, seeded fixtures
  worker/
    ...
```
