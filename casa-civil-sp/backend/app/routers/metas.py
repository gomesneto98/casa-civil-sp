from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List, Optional
from app.database import get_db
from app.models import Meta, GoalGroup
from app.schemas import (
    MetaOut, MetasSummary, GoalGroupOut,
    MetaCreate, MetaUpdate, GoalGroupUpdate,
)

router = APIRouter(prefix="/api/metas", tags=["metas"])


@router.get("/summary", response_model=MetasSummary)
def get_metas_summary(db: Session = Depends(get_db)):
    total = db.query(Meta).count()

    by_status_rows = db.query(Meta.status, func.count(Meta.id)).group_by(Meta.status).all()
    by_status = {r[0]: r[1] for r in by_status_rows}

    by_pillar_rows = (
        db.query(GoalGroup.pillar, func.count(Meta.id))
        .join(Meta, Meta.goal_group_id == GoalGroup.id)
        .group_by(GoalGroup.pillar)
        .all()
    )
    by_pillar = {r[0]: r[1] for r in by_pillar_rows}

    by_priority_rows = db.query(Meta.priority, func.count(Meta.id)).group_by(Meta.priority).all()
    by_priority = {r[0]: r[1] for r in by_priority_rows}

    return MetasSummary(
        total=total,
        by_status=by_status,
        by_pillar=by_pillar,
        by_priority=by_priority,
    )


@router.get("/groups", response_model=List[GoalGroupOut])
def get_goal_groups(db: Session = Depends(get_db)):
    return db.query(GoalGroup).order_by(GoalGroup.number).all()


@router.get("/groups/{group_id}", response_model=GoalGroupOut)
def get_goal_group(group_id: int, db: Session = Depends(get_db)):
    g = db.query(GoalGroup).filter(GoalGroup.id == group_id).first()
    if not g:
        raise HTTPException(status_code=404, detail="Grupo não encontrado")
    return g


@router.put("/groups/{group_id}", response_model=GoalGroupOut)
def update_goal_group(group_id: int, data: GoalGroupUpdate, db: Session = Depends(get_db)):
    g = db.query(GoalGroup).filter(GoalGroup.id == group_id).first()
    if not g:
        raise HTTPException(status_code=404, detail="Grupo não encontrado")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(g, k, v)
    db.commit()
    db.refresh(g)
    return g


@router.get("", response_model=List[MetaOut])
def get_metas(
    pillar: Optional[str] = Query(None),
    group_id: Optional[int] = Query(None),
    priority: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    secretariat_id: Optional[int] = Query(None),
    flag_100_dias: Optional[bool] = Query(None),
    flag_estadao: Optional[bool] = Query(None),
    flag_folha: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
):
    q = (
        db.query(Meta)
        .options(joinedload(Meta.goal_group), joinedload(Meta.secretariat))
        .join(GoalGroup, Meta.goal_group_id == GoalGroup.id)
    )

    if pillar:
        q = q.filter(GoalGroup.pillar == pillar)
    if group_id:
        q = q.filter(Meta.goal_group_id == group_id)
    if priority:
        q = q.filter(Meta.priority == priority)
    if status:
        q = q.filter(Meta.status == status)
    if secretariat_id:
        q = q.filter(Meta.secretariat_id == secretariat_id)
    if flag_100_dias is not None:
        q = q.filter(Meta.flag_100_dias == flag_100_dias)
    if flag_estadao is not None:
        q = q.filter(Meta.flag_estadao == flag_estadao)
    if flag_folha is not None:
        q = q.filter(Meta.flag_folha == flag_folha)

    return q.order_by(Meta.code).all()


def _load_meta(meta_id: int, db: Session) -> Meta:
    m = (
        db.query(Meta)
        .options(joinedload(Meta.goal_group), joinedload(Meta.secretariat))
        .filter(Meta.id == meta_id)
        .first()
    )
    if not m:
        raise HTTPException(status_code=404, detail="Meta não encontrada")
    return m


@router.post("", response_model=MetaOut, status_code=201)
def create_meta(data: MetaCreate, db: Session = Depends(get_db)):
    m = Meta(**data.model_dump())
    db.add(m)
    db.commit()
    db.refresh(m)
    return _load_meta(m.id, db)


@router.get("/{meta_id}", response_model=MetaOut)
def get_meta(meta_id: int, db: Session = Depends(get_db)):
    return _load_meta(meta_id, db)


@router.put("/{meta_id}", response_model=MetaOut)
def update_meta(meta_id: int, data: MetaUpdate, db: Session = Depends(get_db)):
    m = db.query(Meta).filter(Meta.id == meta_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Meta não encontrada")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(m, k, v)
    db.commit()
    db.refresh(m)
    return _load_meta(m.id, db)


@router.delete("/{meta_id}", status_code=204)
def delete_meta(meta_id: int, db: Session = Depends(get_db)):
    m = db.query(Meta).filter(Meta.id == meta_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Meta não encontrada")
    db.delete(m)
    db.commit()
