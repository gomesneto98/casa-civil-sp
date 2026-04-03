from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List

from app.database import get_db
from app.models import Program
from app.schemas import ProgramOut

router = APIRouter(prefix="/api/programs", tags=["programs"])


@router.get("", response_model=List[ProgramOut])
def list_programs(db: Session = Depends(get_db)):
    return (
        db.query(Program)
        .options(joinedload(Program.secretariat))
        .order_by(Program.name)
        .all()
    )


@router.get("/{program_id}", response_model=ProgramOut)
def get_program(program_id: int, db: Session = Depends(get_db)):
    prog = (
        db.query(Program)
        .options(joinedload(Program.secretariat))
        .filter(Program.id == program_id)
        .first()
    )
    if not prog:
        raise HTTPException(status_code=404, detail="Program not found")
    return prog
