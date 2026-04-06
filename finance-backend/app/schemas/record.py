from typing import Optional
from datetime import date
from pydantic import BaseModel, field_validator
from app.models.record import TransactionType


class RecordCreate(BaseModel):
    amount: float
    type: TransactionType
    category: str
    date: date
    notes: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Amount must be greater than zero.")
        return v


class RecordUpdate(BaseModel):
    amount: Optional[float] = None
    type: Optional[TransactionType] = None
    category: Optional[str] = None
    date: Optional[date] = None
    notes: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v <= 0:
            raise ValueError("Amount must be greater than zero.")
        return v


class RecordRead(BaseModel):
    id: int
    amount: float
    type: TransactionType
    category: str
    date: date
    notes: Optional[str]
    owner_id: Optional[int]

    class Config:
        from_attributes = True
