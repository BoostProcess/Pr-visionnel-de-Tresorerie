"""Modèle pour stocker les écritures FEC brutes en base."""

from datetime import date, datetime

from sqlalchemy import Date, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.database import Base


class EcritureFEC(Base):
    """Écriture comptable issue d'un fichier FEC."""
    __tablename__ = "ecriture_fec"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    journal_code: Mapped[str] = mapped_column(String(10), nullable=False)
    journal_lib: Mapped[str] = mapped_column(String(100), nullable=False)
    ecriture_num: Mapped[str] = mapped_column(String(20), nullable=False)
    ecriture_date: Mapped[date] = mapped_column(Date, nullable=False)
    compte_num: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    compte_lib: Mapped[str] = mapped_column(String(200), nullable=False)
    comp_aux_num: Mapped[str | None] = mapped_column(String(20), nullable=True)
    comp_aux_lib: Mapped[str | None] = mapped_column(String(200), nullable=True)
    piece_ref: Mapped[str] = mapped_column(String(50), nullable=False)
    piece_date: Mapped[date] = mapped_column(Date, nullable=False)
    ecriture_lib: Mapped[str] = mapped_column(String(200), nullable=False)
    debit: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    credit: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    ecriture_let: Mapped[str | None] = mapped_column(String(20), nullable=True)
    date_let: Mapped[date | None] = mapped_column(Date, nullable=True)
    valid_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    lot_import_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
