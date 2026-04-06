"""Modèle d'historique de facturation."""

from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.database import Base


class HistoriqueFacturation(Base):
    __tablename__ = "historique_facturation"
    __table_args__ = (
        UniqueConstraint("type_tiers", "tiers_id", "mois", name="uq_historique_tiers_mois"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type_tiers: Mapped[str] = mapped_column(String(15), nullable=False)
    tiers_id: Mapped[int] = mapped_column(Integer, nullable=False)
    mois: Mapped[date] = mapped_column(Date, nullable=False)
    montant_ht: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    montant_ttc: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    nombre_factures: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    delai_paiement_moyen_jours: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )
    lot_import_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("lot_import.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    lot_import = relationship("LotImport")

    def __repr__(self):
        return f"<HistoriqueFacturation {self.type_tiers} {self.tiers_id} {self.mois}>"
