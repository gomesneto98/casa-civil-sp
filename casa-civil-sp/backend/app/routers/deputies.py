from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import Optional, List

from app.database import get_db
from app.models import Deputy, Amendment, Municipality
from app.schemas import DeputySimple, DeputyDetail, MunicipalitySimple

router = APIRouter(prefix="/api/deputies", tags=["deputies"])


@router.get("", response_model=List[DeputySimple])
def list_deputies(
    party: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("name"),
    db: Session = Depends(get_db),
):
    q = db.query(Deputy)
    if party:
        q = q.filter(Deputy.party == party)
    if search:
        q = q.filter(Deputy.name.ilike(f"%{search}%"))

    sort_map = {
        "name": Deputy.name,
        "votes": Deputy.votes_2022.desc(),
        "party": Deputy.party,
        "mandates": Deputy.mandates.desc(),
    }
    order = sort_map.get(sort_by, Deputy.name)
    if sort_by in ("votes", "mandates"):
        q = q.order_by(order)
    else:
        q = q.order_by(order)

    return q.all()


@router.get("/{deputy_id}", response_model=DeputyDetail)
def get_deputy(deputy_id: int, db: Session = Depends(get_db)):
    dep = (
        db.query(Deputy)
        .options(joinedload(Deputy.amendments))
        .filter(Deputy.id == deputy_id)
        .first()
    )
    if not dep:
        raise HTTPException(status_code=404, detail="Deputy not found")
    return dep


@router.get("/{deputy_id}/municipalities", response_model=List[MunicipalitySimple])
def get_deputy_municipalities(deputy_id: int, db: Session = Depends(get_db)):
    dep = db.query(Deputy).filter(Deputy.id == deputy_id).first()
    if not dep:
        raise HTTPException(status_code=404, detail="Deputy not found")

    mun_ids = (
        db.query(Amendment.municipality_id)
        .filter(Amendment.deputy_id == deputy_id)
        .distinct()
        .all()
    )
    ids = [r[0] for r in mun_ids]
    municipalities = db.query(Municipality).filter(Municipality.id.in_(ids)).all()
    return municipalities
