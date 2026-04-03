from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List

from app.database import get_db
from app.models import Secretariat, BudgetItem, Program
from app.schemas import SecretariatSimple, SecretariatDetail, ProgramOut

router = APIRouter(prefix="/api/secretariats", tags=["secretariats"])


@router.get("", response_model=List[dict])
def list_secretariats(db: Session = Depends(get_db)):
    secretariats = db.query(Secretariat).order_by(Secretariat.name).all()
    result = []
    for sec in secretariats:
        total = (
            db.query(func.sum(BudgetItem.value))
            .filter(BudgetItem.secretariat_id == sec.id, BudgetItem.category == "dotacao")
            .scalar()
            or 0
        )
        result.append(
            {
                "id": sec.id,
                "name": sec.name,
                "acronym": sec.acronym,
                "secretary_name": sec.secretary_name,
                "total_budget": total,
            }
        )
    return result


@router.get("/{secretariat_id}", response_model=SecretariatDetail)
def get_secretariat(secretariat_id: int, db: Session = Depends(get_db)):
    sec = (
        db.query(Secretariat)
        .options(joinedload(Secretariat.budget_items))
        .filter(Secretariat.id == secretariat_id)
        .first()
    )
    if not sec:
        raise HTTPException(status_code=404, detail="Secretariat not found")
    return sec


@router.get("/{secretariat_id}/programs", response_model=List[ProgramOut])
def get_secretariat_programs(secretariat_id: int, db: Session = Depends(get_db)):
    sec = db.query(Secretariat).filter(Secretariat.id == secretariat_id).first()
    if not sec:
        raise HTTPException(status_code=404, detail="Secretariat not found")

    programs = (
        db.query(Program)
        .options(joinedload(Program.secretariat))
        .filter(Program.secretariat_id == secretariat_id)
        .all()
    )
    return programs
