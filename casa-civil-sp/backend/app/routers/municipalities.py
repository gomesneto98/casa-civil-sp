from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List

from app.database import get_db
from app.models import Municipality, Amendment
from app.schemas import MunicipalityDetail, AmendmentDetail

router = APIRouter(prefix="/api/municipalities", tags=["municipalities"])


@router.get("", response_model=List[MunicipalityDetail])
def list_municipalities(db: Session = Depends(get_db)):
    return (
        db.query(Municipality)
        .options(joinedload(Municipality.mayor))
        .order_by(Municipality.name)
        .all()
    )


@router.get("/{municipality_id}", response_model=MunicipalityDetail)
def get_municipality(municipality_id: int, db: Session = Depends(get_db)):
    mun = (
        db.query(Municipality)
        .options(joinedload(Municipality.mayor))
        .filter(Municipality.id == municipality_id)
        .first()
    )
    if not mun:
        raise HTTPException(status_code=404, detail="Municipality not found")
    return mun


@router.get("/{municipality_id}/amendments", response_model=List[AmendmentDetail])
def get_municipality_amendments(municipality_id: int, db: Session = Depends(get_db)):
    mun = db.query(Municipality).filter(Municipality.id == municipality_id).first()
    if not mun:
        raise HTTPException(status_code=404, detail="Municipality not found")

    amendments = (
        db.query(Amendment)
        .options(
            joinedload(Amendment.deputy),
            joinedload(Amendment.municipality),
        )
        .filter(Amendment.municipality_id == municipality_id)
        .all()
    )
    return amendments
