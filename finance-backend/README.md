# Finance Dashboard Backend

A FastAPI-based backend for a finance dashboard system featuring role-based access control (RBAC), financial record management, and analytics.

## Features

- **User Management**: Create, update, and manage users with specific roles.
- **Financial Records**: Track income and expenses with categories and notes.
- **Role-Based Access Control (RBAC)**:
  - `admin`: Full access (User management, create/update/delete records).
  - `analyst`: Access to view records and analytics summaries.
  - `viewer`: Read-only access to users and financial records.
- **Analytics**: Get high-level summaries, category breakdowns, and monthly trends.
- **SQLite Database**: Uses SQLModel (SQLAlchemy + Pydantic) for data persistence.

## Project Structure

```text
├── app/
│   ├── core/          # Database config and dependencies (auth/RBAC)
│   ├── models/        # SQLModel database models
│   ├── routers/       # API endpoints (users, records, analytics)
│   ├── schemas/       # Pydantic models for validation
│   ├── main.py        # FastAPI app entry point
│   └── seed.py        # Database seeding script
├── finance.db         # SQLite database file
├── integrationTest.py # Comprehensive integration tests
└── requirements.txt   # Project dependencies
```

## Setup and Installation

1. **Create Virtual Environment** (if not already created):
   ```powershell
   python -m venv .venv
   ```

2. **Activate Virtual Environment**:
   ```powershell
   .venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

4. **Seed the Database**:
   Populate the database with initial admin user and sample data.
   ```powershell
   python -m app.seed
   ```

## Running the Application

Start the FastAPI server:
```powershell
uvicorn app.main:app --reload
```
The API will be available at `http://127.0.0.1:8000`.
You can access the interactive documentation at `http://127.0.0.1:8000/docs`.

## Running Tests

Run the integration tests to verify API functionality and RBAC:
```powershell
python integrationTest.py
```

## API Usage and Authentication

The API uses a mock authentication header `X-User-Id` to identify the acting user. Pass the ID of an existing user in the header for all requests.

### Example: Get Analytics Summary (Analyst/Admin only)
```powershell
Invoke-RestMethod -Headers @{"X-User-Id"="1"} -Uri http://127.0.0.1:8000/analytics/summary
```
