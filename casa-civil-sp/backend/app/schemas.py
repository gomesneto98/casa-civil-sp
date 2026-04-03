from pydantic import BaseModel
from typing import Optional, List


# --- Deputy ---
class AmendmentBase(BaseModel):
    id: int
    year: int
    value: float
    description: Optional[str]
    status: str

    class Config:
        from_attributes = True


class MunicipalitySimple(BaseModel):
    id: int
    name: str
    region: str

    class Config:
        from_attributes = True


class DeputySimple(BaseModel):
    id: int
    name: str
    party: str
    votes_2022: int
    ranking: int
    is_substitute: bool
    mandates: int
    photo_url: Optional[str]

    class Config:
        from_attributes = True


class AmendmentDetail(AmendmentBase):
    deputy: DeputySimple
    municipality: MunicipalitySimple

    class Config:
        from_attributes = True


class DeputyDetail(DeputySimple):
    registration: Optional[int]
    amendments: List[AmendmentBase] = []

    class Config:
        from_attributes = True


# --- Municipality ---
class MayorSimple(BaseModel):
    id: int
    name: str
    party: str
    term_start: int
    term_end: int

    class Config:
        from_attributes = True


class MunicipalityDetail(MunicipalitySimple):
    population: Optional[int]
    lat: Optional[float]
    lng: Optional[float]
    mayor: Optional[MayorSimple]

    class Config:
        from_attributes = True


# --- Secretariat ---
class SecretariatSimple(BaseModel):
    id: int
    name: str
    acronym: str
    emoji: Optional[str]
    secretary_name: Optional[str]
    party: Optional[str]
    executives: Optional[str]

    class Config:
        from_attributes = True


class BudgetItemOut(BaseModel):
    id: int
    year: int
    category: str
    value: float
    description: Optional[str]

    class Config:
        from_attributes = True


class SecretariatDetail(SecretariatSimple):
    budget_items: List[BudgetItemOut] = []

    class Config:
        from_attributes = True


# --- Program ---
class ProgramOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    secretariat_id: Optional[int]
    secretariat: Optional[SecretariatSimple]
    year_start: int
    year_end: Optional[int]
    total_budget: float
    status: str

    class Config:
        from_attributes = True


# --- Programa de Metas ---
class GoalGroupOut(BaseModel):
    id: int
    number: int
    name: str
    pillar: str

    class Config:
        from_attributes = True


class MetaOut(BaseModel):
    id: int
    code: str
    description: str
    goal_group_id: int
    goal_group: GoalGroupOut
    secretariat_id: Optional[int]
    secretariat: Optional[SecretariatSimple]
    priority: str
    status: str
    flag_100_dias: bool
    flag_estadao: bool
    flag_folha: bool
    flag_interior: bool
    flag_capital: bool
    flag_infraestrutura: bool
    planned_value: Optional[float]
    actual_value: Optional[float]
    unit: Optional[str]
    planned_date: Optional[str]
    progress_pct: Optional[float]

    class Config:
        from_attributes = True


class MetasSummary(BaseModel):
    total: int
    by_status: dict
    by_pillar: dict
    by_priority: dict


# --- Dashboard ---
class DashboardSummary(BaseModel):
    total_deputies: int
    total_municipalities: int
    total_secretariats: int
    total_programs: int
    total_amendments_value: float
    total_budget_2025: float
    amendments_by_status: dict
    budget_by_secretariat: List[dict]
    amendments_by_party: List[dict]
