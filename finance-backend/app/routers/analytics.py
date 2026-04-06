from typing import Optional, Dict, Any
from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select, func, col
from app.core.database import get_session
from app.core.deps import require_analyst_or_above
from app.models.record import FinancialRecord, TransactionType
from app.models.user import User

router = APIRouter()


@router.get("/summary")
def get_summary(
    date_from: Optional[date] = Query(default=None),
    date_to: Optional[date] = Query(default=None),
    session: Session = Depends(get_session),
    _: User = Depends(require_analyst_or_above),
) -> Dict[str, Any]:
    """
    Analyst/Admin: high-level financial summary.
    Returns total income, total expenses, net balance, and record count.
    """
    query = select(FinancialRecord)
    if date_from:
        query = query.where(FinancialRecord.date >= date_from)
    if date_to:
        query = query.where(FinancialRecord.date <= date_to)

    records = session.exec(query).all()

    total_income = sum(r.amount for r in records if r.type == TransactionType.income)
    total_expenses = sum(r.amount for r in records if r.type == TransactionType.expense)

    return {
        "total_income": round(total_income, 2),
        "total_expenses": round(total_expenses, 2),
        "net_balance": round(total_income - total_expenses, 2),
        "record_count": len(records),
        "filters": {
            "date_from": str(date_from) if date_from else None,
            "date_to": str(date_to) if date_to else None,
        },
    }


@router.get("/by-category")
def get_by_category(
    type: Optional[TransactionType] = Query(default=None),
    session: Session = Depends(get_session),
    _: User = Depends(require_analyst_or_above),
) -> Dict[str, Any]:
    """
    Analyst/Admin: totals grouped by category.
    Optionally filter by transaction type (income or expense).
    """
    query = select(FinancialRecord)
    if type:
        query = query.where(FinancialRecord.type == type)
    records = session.exec(query).all()

    breakdown: Dict[str, float] = {}
    for r in records:
        breakdown[r.category] = round(breakdown.get(r.category, 0.0) + r.amount, 2)

    return {
        "filter_type": type.value if type else "all",
        "breakdown": breakdown,
    }


@router.get("/by-month")
def get_by_month(
    session: Session = Depends(get_session),
    _: User = Depends(require_analyst_or_above),
) -> Dict[str, Any]:
    """
    Analyst/Admin: monthly income vs expense totals across all records.
    """
    records = session.exec(select(FinancialRecord)).all()

    monthly: Dict[str, Dict[str, float]] = {}
    for r in records:
        key = r.date.strftime("%Y-%m")
        if key not in monthly:
            monthly[key] = {"income": 0.0, "expense": 0.0}
        monthly[key][r.type.value] = round(monthly[key][r.type.value] + r.amount, 2)

    # Sort chronologically
    sorted_monthly = dict(sorted(monthly.items()))
    return {"monthly_breakdown": sorted_monthly}
