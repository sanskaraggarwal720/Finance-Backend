from enum import Enum
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.record import FinancialRecord


class Role(str, Enum):
    viewer = "viewer"    # Can only view dashboard data
    analyst = "analyst"  # Can view records and access insights
    admin = "admin"      # Can create, update, and manage records and users


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    email: str = Field(unique=True, index=True)
    role: Role = Field(default=Role.viewer)
    is_active: bool = Field(default=True)

    records: List["FinancialRecord"] = Relationship(back_populates="owner")
