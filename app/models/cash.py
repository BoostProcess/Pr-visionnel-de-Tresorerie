"""Modèles de trésorerie et lignes de prévisionnel."""

from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.database import Base


class PositionTresorerie(Base):
    __tablename__ = "position_tresorerie"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    solde_banque: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    est_initial: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<PositionTresorerie {self.date}: {self.solde_banque} XPF>"


class LignePrevisionnel(Base):
    __tablename__ = "ligne_previsionnel"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    version_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("version_mensuelle.id"), nullable=True
    )
    scenario: Mapped[str] = mapped_column(String(20), nullable=False)
    mois: Mapped[date] = mapped_column(Date, nullable=False)
    categorie: Mapped[str] = mapped_column(String(30), nullable=False)
    sous_categorie: Mapped[str | None] = mapped_column(String(50), nullable=True)
    source_type: Mapped[str | None] = mapped_column(String(30), nullable=True)
    source_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    nom_tiers: Mapped[str | None] = mapped_column(String(100), nullable=True)
    montant: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    date_echeance: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    version = relationship("VersionMensuelle")

    def __repr__(self):
        return f"<LignePrevisionnel {self.mois} {self.categorie}: {self.montant} XPF>"
