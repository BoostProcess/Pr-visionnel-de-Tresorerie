"""Modèles de commandes clients et fournisseurs."""

from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.database import Base


class CommandeClient(Base):
    __tablename__ = "commande_client"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sage_doc_number: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False
    )
    client_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("client.id"), nullable=False
    )
    date_commande: Mapped[date] = mapped_column(Date, nullable=False)
    date_facturation_prevue: Mapped[date | None] = mapped_column(Date, nullable=True)
    montant_ht: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    montant_ttc: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    montant_facture: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    reste_a_facturer: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    code_affaire: Mapped[str | None] = mapped_column(String(30), nullable=True)
    statut: Mapped[str] = mapped_column(String(20), nullable=False, default="ouverte")
    lot_import_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("lot_import.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )

    client = relationship("Client", back_populates="commandes")
    lot_import = relationship("LotImport")

    def __repr__(self):
        return f"<CommandeClient {self.sage_doc_number}: {self.montant_ttc} XPF>"


class CommandeFournisseur(Base):
    __tablename__ = "commande_fournisseur"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sage_doc_number: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False
    )
    fournisseur_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("fournisseur.id"), nullable=False
    )
    date_commande: Mapped[date] = mapped_column(Date, nullable=False)
    date_facturation_prevue: Mapped[date | None] = mapped_column(Date, nullable=True)
    montant_ht: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    montant_ttc: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    montant_facture: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    reste_a_facturer: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    code_affaire: Mapped[str | None] = mapped_column(String(30), nullable=True)
    statut: Mapped[str] = mapped_column(String(20), nullable=False, default="ouverte")
    lot_import_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("lot_import.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )

    fournisseur = relationship("Fournisseur", back_populates="commandes")
    lot_import = relationship("LotImport")

    def __repr__(self):
        return f"<CommandeFournisseur {self.sage_doc_number}: {self.montant_ttc} XPF>"
