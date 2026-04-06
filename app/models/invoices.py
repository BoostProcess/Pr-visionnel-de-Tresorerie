"""Modèles de factures clients, fournisseurs et avoirs."""

from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.database import Base


class FactureClient(Base):
    __tablename__ = "facture_client"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sage_doc_number: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False
    )
    sage_doc_type: Mapped[int] = mapped_column(Integer, nullable=False, default=6)
    client_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("client.id"), nullable=False
    )
    date_facture: Mapped[date] = mapped_column(Date, nullable=False)
    date_echeance: Mapped[date | None] = mapped_column(Date, nullable=True)
    montant_ht: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    montant_ttc: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    montant_tva: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    montant_regle: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    reste_a_regler: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    en_litige: Mapped[bool] = mapped_column(Boolean, default=False)
    note_litige: Mapped[str | None] = mapped_column(Text, nullable=True)
    code_affaire: Mapped[str | None] = mapped_column(String(30), nullable=True)
    statut: Mapped[str] = mapped_column(String(20), nullable=False, default="ouvert")
    lot_import_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("lot_import.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )

    client = relationship("Client", back_populates="factures")
    lot_import = relationship("LotImport")

    def __repr__(self):
        return f"<FactureClient {self.sage_doc_number}: {self.montant_ttc} XPF>"


class FactureFournisseur(Base):
    __tablename__ = "facture_fournisseur"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sage_doc_number: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False
    )
    sage_doc_type: Mapped[int] = mapped_column(Integer, nullable=False, default=6)
    fournisseur_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("fournisseur.id"), nullable=False
    )
    date_facture: Mapped[date] = mapped_column(Date, nullable=False)
    date_echeance: Mapped[date | None] = mapped_column(Date, nullable=True)
    montant_ht: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    montant_ttc: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    montant_tva: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    montant_regle: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    reste_a_regler: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    en_litige: Mapped[bool] = mapped_column(Boolean, default=False)
    note_litige: Mapped[str | None] = mapped_column(Text, nullable=True)
    code_affaire: Mapped[str | None] = mapped_column(String(30), nullable=True)
    statut: Mapped[str] = mapped_column(String(20), nullable=False, default="ouvert")
    lot_import_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("lot_import.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )

    fournisseur = relationship("Fournisseur", back_populates="factures")
    lot_import = relationship("LotImport")

    def __repr__(self):
        return f"<FactureFournisseur {self.sage_doc_number}: {self.montant_ttc} XPF>"


class Avoir(Base):
    __tablename__ = "avoir"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sage_doc_number: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False
    )
    type_tiers: Mapped[str] = mapped_column(String(15), nullable=False)
    tiers_id: Mapped[int] = mapped_column(Integer, nullable=False)
    date_avoir: Mapped[date] = mapped_column(Date, nullable=False)
    montant_ht: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    montant_ttc: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    facture_liee_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    est_impute: Mapped[bool] = mapped_column(Boolean, default=False)
    lot_import_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("lot_import.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    lot_import = relationship("LotImport")

    def __repr__(self):
        return f"<Avoir {self.sage_doc_number}: {self.montant_ttc} XPF>"
