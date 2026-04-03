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
