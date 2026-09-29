import pytest

from app.db.session import SessionLocal
from app.models.user import User


@pytest.fixture(autouse=True)
def purge_test_users():
    """Drop accounts created by the suite so runs do not accumulate in the
    real database. Related rows (submissions, test sessions, badges, events)
    go with them via ON DELETE CASCADE."""
    yield
    with SessionLocal() as db:
        db.query(User).filter(User.email.like("%@test.com")).delete(
            synchronize_session=False
        )
        db.commit()
