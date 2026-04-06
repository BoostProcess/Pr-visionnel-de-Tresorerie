"""Détection d'anomalies non-bloquantes lors de l'import."""

from datetime import date, timedelta


class AnomalyDetector:
    """Détecte des anomalies dans les données importées.

    Les anomalies sont des alertes (non-bloquantes) qui sont loggées
    mais n'empêchent pas l'import.
    """

    def detect(self, row: dict, file_type: str) -> list[str]:
        """Retourne la liste des anomalies détectées."""
        anomalies = []

        if file_type in ("factures_clients", "factures_fournisseurs"):
            anomalies.extend(self._check_invoice_anomalies(row))
        elif file_type in ("commandes_clients", "commandes_fournisseurs"):
            anomalies.extend(self._check_order_anomalies(row))

        return anomalies

    def _check_invoice_anomalies(self, row: dict) -> list[str]:
        anomalies = []
        today = date.today()

        date_facture = row.get("date_facture")
        date_echeance = row.get("date_echeance")
        montant_ht = row.get("montant_ht", 0)
        montant_ttc = row.get("montant_ttc", 0)
        montant_regle = row.get("montant_regle", 0)

        # Facture dans le futur
        if isinstance(date_facture, date) and date_facture > today:
            anomalies.append(f"Date de facture dans le futur : {date_facture}")

        # Échéance antérieure à la date de facture
        if (
            isinstance(date_facture, date)
            and isinstance(date_echeance, date)
            and date_echeance < date_facture
        ):
            anomalies.append(
                f"Date d'échéance ({date_echeance}) antérieure à la date de facture ({date_facture})"
            )

        # Montant HT négatif sur une facture (pas un avoir)
        if isinstance(montant_ht, int) and montant_ht < 0:
            anomalies.append(f"Montant HT négatif : {montant_ht}")

        # Montant réglé supérieur au TTC (trop-perçu)
        if (
            isinstance(montant_regle, int)
            and isinstance(montant_ttc, int)
            and montant_regle > montant_ttc > 0
        ):
            anomalies.append(
                f"Montant réglé ({montant_regle}) supérieur au TTC ({montant_ttc})"
            )

        # Facture très ancienne encore ouverte (> 365 jours)
        if isinstance(date_facture, date) and (today - date_facture).days > 365:
            reste = montant_ttc - montant_regle if isinstance(montant_regle, int) else montant_ttc
            if reste > 0:
                anomalies.append(
                    f"Facture de plus d'un an encore ouverte ({(today - date_facture).days} jours)"
                )

        return anomalies

    def _check_order_anomalies(self, row: dict) -> list[str]:
        anomalies = []
        today = date.today()

        date_commande = row.get("date_commande")

        # Commande très ancienne (> 180 jours)
        if isinstance(date_commande, date) and (today - date_commande).days > 180:
            anomalies.append(
                f"Commande de plus de 6 mois ({(today - date_commande).days} jours)"
            )

        return anomalies
