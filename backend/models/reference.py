"""Modèles de référentiel : clients, fournisseurs, conditions de règlement."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.database import Base


class ConditionReglement(Base):
    __tablename__ = "condition_reglement"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    libelle: Mapped[str] = mapped_column(String(100), nullable=False)
    base_jours: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    fin_de_mois: Mapped[bool] = mapped_column(Boolean, default=False)
    jour_du_mois: Mapped[int | None] = mapped_column(Integer, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    clients = relationship("Client", back_populates="condition_reglement")
    fournisseurs = relationship("Fournisseur", back_populates="condition_reglement")

    def __repr__(self):
        return f"<ConditionReglement {self.code}: {self.libelle}>"


class Client(Base):
    __tablename__ = "client"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sage_code: Mapped[str] = mapped_column(String(17), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    condition_reglement_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("condition_reglement.id"), nullable=True
    )
    code_activite: Mapped[str | None] = mapped_column(String(20), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )

    condition_reglement = relationship("ConditionReglement", back_populates="clients")
    factures = relationship("FactureClient", back_populates="client")
    commandes = relationship("CommandeClient", back_populates="client")

    def __repr__(self):
        return f"<Client {self.sage_code}: {self.name}>"


class Fournisseur(Base):
    __tablename__ = "fournisseur"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sage_code: Mapped[str] = mapped_column(String(17), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    condition_reglement_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("condition_reglement.id"), nullable=True
    )
    code_activite: Mapped[str | None] = mapped_column(String(20), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )

    condition_reglement = relationship(
        "ConditionReglement", back_populates="fournisseurs"
    )
    factures = relationship("FactureFournisseur", back_populates="fournisseur")
    commandes = relationship("CommandeFournisseur", back_populates="fournisseur")

    def __repr__(self):
        return f"<Fournisseur {self.sage_code}: {self.name}>"
