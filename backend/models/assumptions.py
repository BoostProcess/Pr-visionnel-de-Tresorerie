"""Modèles d'hypothèses : scénarios, saisonnalité, conversion."""

from sqlalchemy import Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.database import Base


class HypotheseScenario(Base):
    __tablename__ = "hypothese_scenario"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    scenario: Mapped[str] = mapped_column(String(20), nullable=False)
    nom_parametre: Mapped[str] = mapped_column(String(50), nullable=False)
    valeur: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    applique_a: Mapped[str | None] = mapped_column(String(50), nullable=True)

    def __repr__(self):
        return f"<HypotheseScenario {self.scenario}/{self.nom_parametre}: {self.valeur}>"


class Saisonnalite(Base):
    __tablename__ = "saisonnalite"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    numero_mois: Mapped[int] = mapped_column(Integer, nullable=False)
    facteur: Mapped[float] = mapped_column(Numeric(5, 4), nullable=False, default=1.0)
    type_tiers: Mapped[str | None] = mapped_column(String(15), nullable=True)
    code_activite: Mapped[str | None] = mapped_column(String(20), nullable=True)

    def __repr__(self):
        return f"<Saisonnalite mois={self.numero_mois} facteur={self.facteur}>"


class HypotheseConversion(Base):
    __tablename__ = "hypothese_conversion"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type_commande: Mapped[str] = mapped_column(String(15), nullable=False)
    delai_moyen_facturation: Mapped[int] = mapped_column(
        Integer, nullable=False, default=30
    )
    taux_confiance: Mapped[float] = mapped_column(
        Numeric(5, 2), nullable=False, default=90.0
    )
    code_activite: Mapped[str | None] = mapped_column(String(20), nullable=True)

    def __repr__(self):
        return f"<HypotheseConversion {self.type_commande}: {self.delai_moyen_facturation}j/{self.taux_confiance}%>"
