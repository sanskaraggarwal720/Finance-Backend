from enum import Enum
from typing import Optional, TYPE_CHECKING
from datetime import date
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.user import User


class TransactionType(str, Enum):
    income = "income"
    expense = "expense"


class FinancialRecord(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    amount: float = Field(gt=0, description="Must be a positive value.")
    type: TransactionType
    category: str
    date: date
    notes: Optional[str] = Field(default=None)

    owner_id: Optional[int] = Field(default=None, foreign_key="user.id")
    owner: Optional["User"] = Relationship(back_populates="records")
