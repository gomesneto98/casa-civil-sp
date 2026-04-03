from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from app.database import get_db
from app.models import Deputy, Municipality, Secretariat, Program, Amendment, BudgetItem
from app.schemas import DashboardSummary

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(db: Session = Depends(get_db)):
    total_deputies = db.query(func.count(Deputy.id)).scalar()
    total_municipalities = db.query(func.count(Municipality.id)).scalar()
    total_secretariats = db.query(func.count(Secretariat.id)).scalar()
    total_programs = db.query(func.count(Program.id)).scalar()

    total_amendments_value = db.query(func.sum(Amendment.value)).scalar() or 0

    total_budget_2025 = (
        db.query(func.sum(BudgetItem.value))
        .filter(BudgetItem.year == 2025, BudgetItem.category == "dotacao", BudgetItem.secretariat_id.isnot(None))
        .scalar()
        or 0
    )

    # Amendments by status
    status_rows = (
        db.query(Amendment.status, func.count(Amendment.id))
        .group_by(Amendment.status)
        .all()
    )
    amendments_by_status = {row[0]: row[1] for row in status_rows}

    # Budget by secretariat (top 5 by dotacao sum)
    budget_rows = (
        db.query(
            Secretariat.name,
            Secretariat.acronym,
            func.sum(BudgetItem.value).label("total"),
        )
        .join(BudgetItem, BudgetItem.secretariat_id == Secretariat.id)
        .filter(BudgetItem.category == "dotacao")
        .group_by(Secretariat.id, Secretariat.name, Secretariat.acronym)
        .order_by(func.sum(BudgetItem.value).desc())
        .limit(5)
        .all()
    )
    budget_by_secretariat = [
        {"name": r[0], "acronym": r[1], "total": r[2]} for r in budget_rows
    ]

    # Amendments by party
    party_rows = (
        db.query(
            Deputy.party,
            func.sum(Amendment.value).label("total"),
        )
        .join(Amendment, Amendment.deputy_id == Deputy.id)
        .group_by(Deputy.party)
        .order_by(func.sum(Amendment.value).desc())
        .limit(10)
        .all()
    )
    amendments_by_party = [{"party": r[0], "total": r[1]} for r in party_rows]

    return DashboardSummary(
        total_deputies=total_deputies,
        total_municipalities=total_municipalities,
        total_secretariats=total_secretariats,
        total_programs=total_programs,
        total_amendments_value=total_amendments_value,
        total_budget_2025=total_budget_2025,
        amendments_by_status=amendments_by_status,
        budget_by_secretariat=budget_by_secretariat,
        amendments_by_party=amendments_by_party,
    )
