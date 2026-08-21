import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy import text

from app.db.base import Base
from app.db.session import SessionLocal, engine


def main():
    import app.models

    Base.metadata.create_all(bind=engine)
    with engine.begin() as conn:
        conn.execute(
            text("ALTER TABLE submissions ADD COLUMN IF NOT EXISTS ai_review JSONB")
        )
        conn.execute(
            text("ALTER TABLE submissions ADD COLUMN IF NOT EXISTS judge_summary JSONB")
        )
    with SessionLocal() as db:
        rows = db.execute(
            text("SELECT tablename FROM pg_tables WHERE schemaname='public'")
        ).fetchall()
    print("tables:", sorted(row[0] for row in rows))


if __name__ == "__main__":
    main()
