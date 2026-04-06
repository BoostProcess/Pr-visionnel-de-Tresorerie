"""Modèles de charges fixes, emprunts et charges fiscales."""

from datetime import date

from sqlalchemy import Boolean, Date, Numeric, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.database import Base


class ChargeFix(Base):
    __tablename__ = "charge_fixe"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    libelle: Mapped[str] = mapped_column(String(100), nullable=False)
    categorie: Mapped[str] = mapped_column(String(50), nullable=False)
    montant_ttc: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    taux_tva: Mapped[float] = mapped_column(Numeric(5, 4), nullable=False, default=0.16)
    frequence: Mapped[str] = mapped_column(String(20), nullable=False, default="mensuel")
    jour_paiement: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    date_debut: Mapped[date] = mapped_column(Date, nullable=False)
    date_fin: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    def __repr__(self):
        return f"<ChargeFix {self.libelle}: {self.montant_ttc} XPF/{self.frequence}>"


class Emprunt(Base):
    __tablename__ = "emprunt"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    libelle: Mapped[str] = mapped_column(String(100), nullable=False)
    preteur: Mapped[str] = mapped_column(String(100), nullable=False)
    montant_initial: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    capital_restant: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    mensualite: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    part_interet: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    part_capital: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    jour_paiement: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    date_debut: Mapped[date] = mapped_column(Date, nullable=False)
    date_fin: Mapped[date] = mapped_column(Date, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    def __repr__(self):
        return f"<Emprunt {self.libelle}: {self.mensualite} XPF/mois>"


class ChargeFiscale(Base):
    __tablename__ = "charge_fiscale"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type_taxe: Mapped[str] = mapped_column(String(30), nullable=False)
    libelle: Mapped[str] = mapped_column(String(100), nullable=False)
    frequence: Mapped[str] = mapped_column(String(20), nullable=False, default="mensuel")
    mois_decalage: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    montant_estime: Mapped[int | None] = mapped_column(Integer, nullable=True)
    methode_calcul: Mapped[str] = mapped_column(
        String(20), nullable=False, default="fixe"
    )
    taux: Mapped[float | None] = mapped_column(Numeric(8, 6), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    def __repr__(self):
        return f"<ChargeFiscale {self.type_taxe}: {self.libelle}>"
