"""Grant admin to a user by email. Usage: .venv/bin/python scripts/make_admin.py <email>"""

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.db.session import SessionLocal
from app.models.user import User


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: make_admin.py <email>")
        return 2
    email = sys.argv[1].lower().strip()
    with SessionLocal() as db:
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            print(f"no user with email {email}")
            return 1
        user.is_admin = True
        db.commit()
        print(f"{user.username} <{user.email}> is now admin")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
