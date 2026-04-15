"""Modèle de versionnement mensuel."""

from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.database import Base


class VersionMensuelle(Base):
    __tablename__ = "version_mensuelle"
    __table_args__ = (UniqueConstraint("mois", name="uq_version_mois"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    mois: Mapped[date] = mapped_column(Date, nullable=False)
    est_verrouille: Mapped[bool] = mapped_column(Boolean, default=False)
    verrouille_le: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    verrouille_par: Mapped[str | None] = mapped_column(String(50), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<VersionMensuelle {self.mois}: {'verrouillé' if self.est_verrouille else 'ouvert'}>"
