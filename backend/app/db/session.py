from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

# Disable psycopg (v3) client-side named prepared statements. When DATABASE_URL
# points at a PgBouncer-style pooler (e.g. Supabase), pooled server sessions are
# reused across processes and the generated `_pgN` prepared-statement names can
# collide, raising "DuplicatePreparedStatement" at startup. Disabling the cache
# sidesteps that while keeping normal query performance.
connect_args = {}
if settings.DATABASE_URL.startswith("postgresql+psycopg://"):
    connect_args = {"prepare_threshold": None}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
