import unittest
import os
from datetime import date
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session, select

from app.main import app
from app.core.database import get_session
from app.models.user import User, Role
from app.models.record import FinancialRecord, TransactionType

# Setup a test database
TEST_DATABASE_URL = "sqlite:///./test.db"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})

def get_test_session():
    with Session(test_engine) as session:
        yield session

app.dependency_overrides[get_session] = get_test_session

class TestFinanceAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        SQLModel.metadata.create_all(test_engine)
        cls.client = TestClient(app)

    @classmethod
    def tearDownClass(cls):
        SQLModel.metadata.drop_all(test_engine)
        if os.path.exists("./test.db"):
            os.remove("./test.db")

    def setUp(self):
        # Clear tables before each test
        with Session(test_engine) as session:
            session.exec(select(FinancialRecord)).all()
            for r in session.exec(select(FinancialRecord)).all():
                session.delete(r)
            for u in session.exec(select(User)).all():
                session.delete(u)
            session.commit()

        # Create base users for testing
        with Session(test_engine) as session:
            self.admin = User(name="Admin", email="admin@test.com", role=Role.admin)
            self.analyst = User(name="Analyst", email="analyst@test.com", role=Role.analyst)
            self.viewer = User(name="Viewer", email="viewer@test.com", role=Role.viewer)
            session.add(self.admin)
            session.add(self.analyst)
            session.add(self.viewer)
            session.commit()
            session.refresh(self.admin)
            session.refresh(self.analyst)
            session.refresh(self.viewer)

    def test_health_check(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_user_management_rbac(self):
        # Admin can list users
        headers = {"X-User-Id": str(self.admin.id)}
        response = self.client.get("/users/", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 3)

        # Viewer can list users
        headers = {"X-User-Id": str(self.viewer.id)}
        response = self.client.get("/users/", headers=headers)
        self.assertEqual(response.status_code, 200)

        # Admin can create user
        headers = {"X-User-Id": str(self.admin.id)}
        new_user = {"name": "New User", "email": "new@test.com", "role": "viewer"}
        response = self.client.post("/users/", json=new_user, headers=headers)
        self.assertEqual(response.status_code, 201)

        # Viewer cannot create user
        headers = {"X-User-Id": str(self.viewer.id)}
        response = self.client.post("/users/", json=new_user, headers=headers)
        self.assertEqual(response.status_code, 403)

    def test_financial_records_rbac(self):
        # Admin creates a record
        headers = {"X-User-Id": str(self.admin.id)}
        record_data = {
            "amount": 100.5,
            "type": "income",
            "category": "Bonus",
            "date": "2026-04-01",
            "notes": "Testing record creation"
        }
        response = self.client.post("/records/", json=record_data, headers=headers)
        self.assertEqual(response.status_code, 201)
        record_id = response.json()["id"]

        # Analyst cannot create a record
        headers = {"X-User-Id": str(self.analyst.id)}
        response = self.client.post("/records/", json=record_data, headers=headers)
        self.assertEqual(response.status_code, 403)

        # Viewer can see the record
        headers = {"X-User-Id": str(self.viewer.id)}
        response = self.client.get(f"/records/{record_id}", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["category"], "Bonus")

        # Admin can update record
        headers = {"X-User-Id": str(self.admin.id)}
        update_data = {"amount": 200.0}
        response = self.client.patch(f"/records/{record_id}", json=update_data, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["amount"], 200.0)

        # Analyst cannot update record
        response = self.client.patch(f"/records/{record_id}", json=update_data, headers={"X-User-Id": str(self.analyst.id)})
        self.assertEqual(response.status_code, 403)

    def test_analytics_rbac(self):
        # Seed some data for analytics
        with Session(test_engine) as session:
            r1 = FinancialRecord(amount=1000, type=TransactionType.income, category="Salary", date=date(2026, 4, 1), owner_id=self.admin.id)
            r2 = FinancialRecord(amount=300, type=TransactionType.expense, category="Food", date=date(2026, 4, 2), owner_id=self.admin.id)
            session.add(r1)
            session.add(r2)
            session.commit()

        # Analyst can access summary
        headers = {"X-User-Id": str(self.analyst.id)}
        response = self.client.get("/analytics/summary", headers=headers)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total_income"], 1000.0)
        self.assertEqual(data["total_expenses"], 300.0)
        self.assertEqual(data["net_balance"], 700.0)

        # Viewer cannot access summary
        headers = {"X-User-Id": str(self.viewer.id)}
        response = self.client.get("/analytics/summary", headers=headers)
        self.assertEqual(response.status_code, 403)

        # Analyst can access breakdown
        headers = {"X-User-Id": str(self.analyst.id)}
        response = self.client.get("/analytics/by-category", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Food", response.json()["breakdown"])

    def test_invalid_user(self):
        # Non-existent user
        headers = {"X-User-Id": "999"}
        response = self.client.get("/users/", headers=headers)
        self.assertEqual(response.status_code, 401)

    def test_inactive_user(self):
        # Admin deactivates analyst
        headers = {"X-User-Id": str(self.admin.id)}
        self.client.delete(f"/users/{self.analyst.id}", headers=headers)

        # Inactive user cannot access API
        headers = {"X-User-Id": str(self.analyst.id)}
        response = self.client.get("/users/", headers=headers)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["detail"], "User account is inactive.")

if __name__ == "__main__":
    unittest.main()
