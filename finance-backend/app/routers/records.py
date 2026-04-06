from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from app.core.database import get_session
from app.core.deps import require_admin, require_viewer_or_above, require_analyst_or_above
from app.models.record import FinancialRecord, TransactionType
from app.models.user import User
from app.schemas.record import RecordCreate, RecordRead, RecordUpdate

router = APIRouter()


@router.post("/", response_model=RecordRead, status_code=201)
def create_record(
    payload: RecordCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin),
):
    """Admin only: create a financial record."""
    record = FinancialRecord(**payload.model_dump(), owner_id=current_user.id)
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


@router.get("/", response_model=List[RecordRead])
def list_records(
    type: Optional[TransactionType] = Query(default=None),
    category: Optional[str] = Query(default=None),
    date_from: Optional[date] = Query(default=None),
    date_to: Optional[date] = Query(default=None),
    session: Session = Depends(get_session),
    _: User = Depends(require_viewer_or_above),
):
    """All authenticated users can view records with optional filters."""
    query = select(FinancialRecord)
    if type:
        query = query.where(FinancialRecord.type == type)
    if category:
        query = query.where(FinancialRecord.category == category)
    if date_from:
        query = query.where(FinancialRecord.date >= date_from)
    if date_to:
        query = query.where(FinancialRecord.date <= date_to)
    return session.exec(query).all()


@router.get("/{record_id}", response_model=RecordRead)
def get_record(
    record_id: int,
    session: Session = Depends(get_session),
    _: User = Depends(require_viewer_or_above),
):
    record = session.get(FinancialRecord, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found.")
    return record


@router.patch("/{record_id}", response_model=RecordRead)
def update_record(
    record_id: int,
    payload: RecordUpdate,
    session: Session = Depends(get_session),
    _: User = Depends(require_admin),
):
    """Admin only: update a financial record."""
    record = session.get(FinancialRecord, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found.")
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(record, key, value)
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


@router.delete("/{record_id}", status_code=204)
def delete_record(
    record_id: int,
    session: Session = Depends(get_session),
    _: User = Depends(require_admin),
):
    """Admin only: delete a financial record."""
    record = session.get(FinancialRecord, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found.")
    session.delete(record)
    session.commit()
