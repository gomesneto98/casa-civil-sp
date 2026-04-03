from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List

from app.database import get_db
from app.models import Municipality, Amendment, Mayor
from app.schemas import (
    MunicipalityDetail, AmendmentDetail,
    MunicipalityCreate, MunicipalityUpdate,
    MayorCreate, MayorUpdate, MayorSimple,
)

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


# ── Municipality CRUD ──────────────────────────────────────────────────────────

@router.post("", response_model=MunicipalityDetail, status_code=201)
def create_municipality(data: MunicipalityCreate, db: Session = Depends(get_db)):
    mun = Municipality(**data.model_dump())
    db.add(mun)
    db.commit()
    db.refresh(mun)
    return mun


@router.put("/{municipality_id}", response_model=MunicipalityDetail)
def update_municipality(municipality_id: int, data: MunicipalityUpdate, db: Session = Depends(get_db)):
    mun = db.query(Municipality).filter(Municipality.id == municipality_id).first()
    if not mun:
        raise HTTPException(status_code=404, detail="Municipality not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(mun, k, v)
    db.commit()
    db.refresh(mun)
    return mun


@router.delete("/{municipality_id}", status_code=204)
def delete_municipality(municipality_id: int, db: Session = Depends(get_db)):
    mun = db.query(Municipality).filter(Municipality.id == municipality_id).first()
    if not mun:
        raise HTTPException(status_code=404, detail="Municipality not found")
    db.delete(mun)
    db.commit()


# ── Mayor CRUD ────────────────────────────────────────────────────────────────

@router.post("/{municipality_id}/mayor", response_model=MayorSimple, status_code=201)
def create_mayor(municipality_id: int, data: MayorCreate, db: Session = Depends(get_db)):
    mun = db.query(Municipality).filter(Municipality.id == municipality_id).first()
    if not mun:
        raise HTTPException(status_code=404, detail="Municipality not found")
    mayor = Mayor(**data.model_dump())
    db.add(mayor)
    db.flush()
    mun.mayor_id = mayor.id
    db.commit()
    db.refresh(mayor)
    return mayor


@router.put("/{municipality_id}/mayor", response_model=MayorSimple)
def update_mayor(municipality_id: int, data: MayorUpdate, db: Session = Depends(get_db)):
    mun = (
        db.query(Municipality)
        .options(joinedload(Municipality.mayor))
        .filter(Municipality.id == municipality_id)
        .first()
    )
    if not mun or not mun.mayor:
        raise HTTPException(status_code=404, detail="Mayor not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(mun.mayor, k, v)
    db.commit()
    db.refresh(mun.mayor)
    return mun.mayor


@router.delete("/{municipality_id}/mayor", status_code=204)
def delete_mayor(municipality_id: int, db: Session = Depends(get_db)):
    mun = (
        db.query(Municipality)
        .options(joinedload(Municipality.mayor))
        .filter(Municipality.id == municipality_id)
        .first()
    )
    if not mun or not mun.mayor:
        raise HTTPException(status_code=404, detail="Mayor not found")
    mayor = mun.mayor
    mun.mayor_id = None
    db.delete(mayor)
    db.commit()
