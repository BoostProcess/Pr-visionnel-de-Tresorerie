"""Modèles de journal d'import."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.database import Base


class LotImport(Base):
    __tablename__ = "lot_import"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nom_fichier: Mapped[str] = mapped_column(String(255), nullable=False)
    type_fichier: Mapped[str] = mapped_column(String(30), nullable=False)
    nb_lignes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    nb_importees: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    nb_doublons: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    nb_erreurs: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    date_import: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    statut: Mapped[str] = mapped_column(String(20), nullable=False, default="en_cours")

    erreurs = relationship("ErreurImport", back_populates="lot_import")

    def __repr__(self):
        return f"<LotImport {self.nom_fichier}: {self.statut}>"


class ErreurImport(Base):
    __tablename__ = "erreur_import"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    lot_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("lot_import.id"), nullable=False
    )
    numero_ligne: Mapped[int] = mapped_column(Integer, nullable=False)
    nom_champ: Mapped[str | None] = mapped_column(String(50), nullable=True)
    type_erreur: Mapped[str] = mapped_column(String(30), nullable=False)
    valeur_brute: Mapped[str | None] = mapped_column(String(500), nullable=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)

    lot_import = relationship("LotImport", back_populates="erreurs")

    def __repr__(self):
        return f"<ErreurImport ligne {self.numero_ligne}: {self.type_erreur}>"
