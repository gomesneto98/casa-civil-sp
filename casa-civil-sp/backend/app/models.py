from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Deputy(Base):
    __tablename__ = "deputies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    party = Column(String, nullable=False)
    votes_2022 = Column(Integer, default=0)
    registration = Column(Integer, nullable=True)
    ranking = Column(Integer, default=0)
    is_substitute = Column(Boolean, default=False)
    mandates = Column(Integer, default=1)
    photo_url = Column(String, nullable=True)

    amendments = relationship("Amendment", back_populates="deputy")


class Municipality(Base):
    __tablename__ = "municipalities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    region = Column(String, nullable=False)
    population = Column(Integer, nullable=True)
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)
    mayor_id = Column(Integer, ForeignKey("mayors.id"), nullable=True)

    mayor = relationship("Mayor", back_populates="municipality")
    amendments = relationship("Amendment", back_populates="municipality")


class Mayor(Base):
    __tablename__ = "mayors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    party = Column(String, nullable=False)
    term_start = Column(Integer, nullable=False)
    term_end = Column(Integer, nullable=False)

    municipality = relationship("Municipality", back_populates="mayor")
    budget_items = relationship("BudgetItem", back_populates="mayor")


class Amendment(Base):
    __tablename__ = "amendments"

    id = Column(Integer, primary_key=True, index=True)
    deputy_id = Column(Integer, ForeignKey("deputies.id"), nullable=False)
    municipality_id = Column(Integer, ForeignKey("municipalities.id"), nullable=False)
    year = Column(Integer, nullable=False)
    value = Column(Float, nullable=False)
    description = Column(String, nullable=True)
    status = Column(String, nullable=False, default="pendente")

    deputy = relationship("Deputy", back_populates="amendments")
    municipality = relationship("Municipality", back_populates="amendments")


class Secretariat(Base):
    __tablename__ = "secretariats"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    acronym = Column(String, nullable=False)
    emoji = Column(String, nullable=True)
    secretary_name = Column(String, nullable=True)
    party = Column(String, nullable=True)
    executives = Column(String, nullable=True)  # semicolon-separated "Nome|Partido"

    budget_items = relationship("BudgetItem", back_populates="secretariat")
    metas = relationship("Meta", back_populates="secretariat")


class BudgetItem(Base):
    __tablename__ = "budget_items"

    id = Column(Integer, primary_key=True, index=True)
    secretariat_id = Column(Integer, ForeignKey("secretariats.id"), nullable=True)
    mayor_id = Column(Integer, ForeignKey("mayors.id"), nullable=True)
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=True)
    year = Column(Integer, nullable=False)
    category = Column(String, nullable=False)  # dotacao, empenhado, liquidado, pago
    value = Column(Float, nullable=False)
    description = Column(String, nullable=True)

    secretariat = relationship("Secretariat", back_populates="budget_items")
    mayor = relationship("Mayor", back_populates="budget_items")
    program = relationship("Program", back_populates="budget_items")


class Program(Base):
    __tablename__ = "programs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    secretariat_id = Column(Integer, ForeignKey("secretariats.id"), nullable=True)
    year_start = Column(Integer, nullable=False)
    year_end = Column(Integer, nullable=True)
    total_budget = Column(Float, nullable=False)
    status = Column(String, nullable=False, default="ativo")

    budget_items = relationship("BudgetItem", back_populates="program")


# ── Programa de Metas (Governo Tarcísio 2023-2026) ─────────────────────────

class GoalGroup(Base):
    """Dimensão: 12 Objetivos do Programa de Metas, agrupados por um dos 3 Eixos."""
    __tablename__ = "goal_groups"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(Integer, nullable=False)           # 1-12
    name = Column(String, nullable=False)              # nome do objetivo
    pillar = Column(String, nullable=False)            # Dignidade / Desenvolvimento / Diálogo

    metas = relationship("Meta", back_populates="goal_group")


class Meta(Base):
    """Fato+Dimensão: cada uma das 260 Metas com dados de execução (planejado x realizado)."""
    __tablename__ = "metas"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, nullable=False)              # ex: "1.1", "3.4"
    description = Column(String, nullable=False)       # texto da meta
    goal_group_id = Column(Integer, ForeignKey("goal_groups.id"), nullable=False)
    secretariat_id = Column(Integer, ForeignKey("secretariats.id"), nullable=True)

    # Dimensão Programa de Metas
    priority = Column(String, nullable=False, default="B")  # A, B ou C
    status = Column(String, nullable=False)                 # Em andamento, Em alerta, Atrasado, Alcançado, Evento a confirmar

    # Flags / visões especiais
    flag_100_dias = Column(Boolean, default=False)
    flag_estadao = Column(Boolean, default=False)
    flag_folha = Column(Boolean, default=False)
    flag_interior = Column(Boolean, default=False)
    flag_capital = Column(Boolean, default=False)
    flag_infraestrutura = Column(Boolean, default=False)

    # Execução (planejado x realizado)
    planned_value = Column(Float, nullable=True)        # valor planejado
    actual_value = Column(Float, nullable=True)         # valor realizado
    unit = Column(String, nullable=True)                # ex: "unidades", "km", "%", "R$ bi"
    planned_date = Column(String, nullable=True)        # data prevista de conclusão (ex: "2026-12")
    progress_pct = Column(Float, nullable=True)         # % de conclusão

    goal_group = relationship("GoalGroup", back_populates="metas")
    secretariat = relationship("Secretariat", back_populates="metas")
