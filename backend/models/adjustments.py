"""Modèle d'ajustements manuels."""

from datetime import date, datetime

from sqlalchemy import Date, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.database import Base


class AjustementManuel(Base):
    __tablename__ = "ajustement_manuel"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    mois: Mapped[date] = mapped_column(Date, nullable=False)
    direction: Mapped[str] = mapped_column(String(20), nullable=False)
    libelle: Mapped[str] = mapped_column(String(200), nullable=False)
    montant: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    categorie: Mapped[str] = mapped_column(String(50), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    cree_par: Mapped[str | None] = mapped_column(String(50), nullable=True)
    cree_le: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<AjustementManuel {self.mois} {self.direction}: {self.montant} XPF>"
