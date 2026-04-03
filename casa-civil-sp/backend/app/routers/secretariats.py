from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List

from app.database import get_db
from app.models import Secretariat, BudgetItem, Program, Meta
from app.schemas import (
    SecretariatSimple, SecretariatDetail, ProgramOut,
    SecretariatCreate, SecretariatUpdate,
)

router = APIRouter(prefix="/api/secretariats", tags=["secretariats"])


@router.get("", response_model=List[dict])
def list_secretariats(db: Session = Depends(get_db)):
    secretariats = db.query(Secretariat).order_by(Secretariat.name).all()

    # Batch-query meta counts (avoid N+1)
    meta_counts = dict(
        db.query(Meta.secretariat_id, func.count(Meta.id))
        .group_by(Meta.secretariat_id)
        .all()
    )
    meta_status_raw = (
        db.query(Meta.secretariat_id, Meta.status, func.count(Meta.id))
        .group_by(Meta.secretariat_id, Meta.status)
        .all()
    )
    meta_by_status: dict = {}
    for sec_id, status, count in meta_status_raw:
        meta_by_status.setdefault(sec_id, {})[status] = count

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
                "emoji": sec.emoji,
                "secretary_name": sec.secretary_name,
                "party": sec.party,
                "executives": sec.executives,
                "total_budget": total,
                "meta_count": meta_counts.get(sec.id, 0),
                "meta_by_status": meta_by_status.get(sec.id, {}),
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


@router.post("", response_model=SecretariatSimple, status_code=201)
def create_secretariat(data: SecretariatCreate, db: Session = Depends(get_db)):
    sec = Secretariat(**data.model_dump())
    db.add(sec)
    db.commit()
    db.refresh(sec)
    return sec


@router.put("/{secretariat_id}", response_model=SecretariatSimple)
def update_secretariat(secretariat_id: int, data: SecretariatUpdate, db: Session = Depends(get_db)):
    sec = db.query(Secretariat).filter(Secretariat.id == secretariat_id).first()
    if not sec:
        raise HTTPException(status_code=404, detail="Secretariat not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(sec, k, v)
    db.commit()
    db.refresh(sec)
    return sec


@router.delete("/{secretariat_id}", status_code=204)
def delete_secretariat(secretariat_id: int, db: Session = Depends(get_db)):
    sec = db.query(Secretariat).filter(Secretariat.id == secretariat_id).first()
    if not sec:
        raise HTTPException(status_code=404, detail="Secretariat not found")
    db.delete(sec)
    db.commit()
