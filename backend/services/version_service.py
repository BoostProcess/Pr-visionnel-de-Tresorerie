"""Service de gestion des versions mensuelles."""

from datetime import date, datetime

from sqlalchemy.orm import Session

from app.models.versions import VersionMensuelle


class VersionService:
    """Gère le verrouillage/déverrouillage des mois."""

    def __init__(self, session: Session):
        self.session = session

    def lock_month(self, mois: date, locked_by: str = "utilisateur"):
        """Verrouille un mois."""
        version = self._get_or_create(mois)
        version.est_verrouille = True
        version.verrouille_le = datetime.now()
        version.verrouille_par = locked_by
        self.session.flush()

    def unlock_month(self, mois: date):
        """Déverrouille un mois."""
        version = self._get_or_create(mois)
        version.est_verrouille = False
        version.verrouille_le = None
        version.verrouille_par = None
        self.session.flush()

    def is_locked(self, mois: date) -> bool:
        """Vérifie si un mois est verrouillé."""
        version = self.session.query(VersionMensuelle).filter(
            VersionMensuelle.mois == mois
        ).first()
        return version.est_verrouille if version else False

    def list_versions(self) -> list[VersionMensuelle]:
        """Liste toutes les versions."""
        return (
            self.session.query(VersionMensuelle)
            .order_by(VersionMensuelle.mois)
            .all()
        )

    def _get_or_create(self, mois: date) -> VersionMensuelle:
        version = self.session.query(VersionMensuelle).filter(
            VersionMensuelle.mois == mois
        ).first()
        if not version:
            version = VersionMensuelle(mois=mois)
            self.session.add(version)
            self.session.flush()
        return version
