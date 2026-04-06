from datetime import date
from sqlmodel import Session, select

from app.core.database import engine, init_db
from app.models.user import Role, User
from app.models.record import FinancialRecord, TransactionType

def seed_data():
    init_db()
    with Session(engine) as s:
        # Check if admin already exists
        existing_admin = s.exec(select(User).where(User.email == "alice@example.com")).first()
        if existing_admin:
            print("Database already seeded.")
            return

        admin = User(name="Alice", email="alice@example.com", role=Role.admin)
        s.add(admin)
        s.commit()
        s.refresh(admin)

        r1 = FinancialRecord(
            amount=5000.0,
            type=TransactionType.income,
            category="Salary",
            date=date(2026, 4, 1),
            owner_id=admin.id
        )
        r2 = FinancialRecord(
            amount=1200.0,
            type=TransactionType.expense,
            category="Rent",
            date=date(2026, 4, 2),
            owner_id=admin.id
        )
        s.add(r1)
        s.add(r2)
        s.commit()

        print("Admin ID:", admin.id)
        print("Seeded records for Alice.")


if __name__ == "__main__":
    seed_data()
