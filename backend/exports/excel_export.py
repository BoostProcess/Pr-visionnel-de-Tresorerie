"""Export du prévisionnel au format Excel."""

import io
from datetime import date

import xlsxwriter

from app.calculations.monthly_aggregator import MonthSummary
from app.models.cash import LignePrevisionnel
from app.ui.components.filters import MOIS_FR, format_month_fr


class ExcelExporter:
    """Génère un classeur Excel du prévisionnel."""

    def export(
        self,
        forecast_data: dict[str, list[MonthSummary]],
        encaissements: list[LignePrevisionnel] | None = None,
        decaissements: list[LignePrevisionnel] | None = None,
    ) -> io.BytesIO:
        """Génère le fichier Excel en mémoire.

        Returns:
            Buffer contenant le fichier .xlsx
        """
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {"in_memory": True})

        # Formats
        formats = self._create_formats(workbook)

        # Onglet 1 : Synthèse (scénario central)
        central = forecast_data.get("central", [])
        if central:
            self._write_summary_sheet(workbook, "Synthèse", central, formats)

        # Onglet 2 : Comparaison 3 scénarios
        self._write_comparison_sheet(workbook, forecast_data, formats)

        # Onglet 3 : Encaissements détaillés
        if encaissements:
            self._write_detail_sheet(workbook, "Encaissements", encaissements, formats)

        # Onglet 4 : Décaissements détaillés
        if decaissements:
            self._write_detail_sheet(workbook, "Décaissements", decaissements, formats)

        workbook.close()
        output.seek(0)
        return output

    def _create_formats(self, workbook) -> dict:
        """Crée les formats de cellules."""
        return {
            "header": workbook.add_format({
                "bold": True,
                "bg_color": "#2F5496",
                "font_color": "white",
                "border": 1,
                "text_wrap": True,
                "align": "center",
            }),
            "money": workbook.add_format({
                "num_format": "#,##0 F",
                "border": 1,
            }),
            "money_neg": workbook.add_format({
                "num_format": "#,##0 F",
                "border": 1,
                "font_color": "red",
            }),
            "money_bold": workbook.add_format({
                "num_format": "#,##0 F",
                "border": 1,
                "bold": True,
            }),
            "text": workbook.add_format({
                "border": 1,
            }),
            "date": workbook.add_format({
                "num_format": "dd/mm/yyyy",
                "border": 1,
            }),
            "title": workbook.add_format({
                "bold": True,
                "font_size": 14,
            }),
            "subtitle": workbook.add_format({
                "bold": True,
                "font_size": 11,
                "bottom": 1,
            }),
            "negative_bg": workbook.add_format({
                "num_format": "#,##0 F",
                "border": 1,
                "bg_color": "#FFC7CE",
                "font_color": "#9C0006",
                "bold": True,
            }),
        }

    def _write_summary_sheet(
        self, workbook, sheet_name: str, summaries: list[MonthSummary], formats: dict,
    ):
        """Écrit l'onglet de synthèse mensuelle."""
        ws = workbook.add_worksheet(sheet_name)
        ws.set_column("A:A", 18)
        ws.set_column("B:G", 18)

        # Titre
        ws.write(0, 0, "Prévisionnel de Trésorerie - Synthèse", formats["title"])
        ws.write(1, 0, f"Généré le {date.today().strftime('%d/%m/%Y')}")

        # En-têtes
        headers = [
            "Mois", "Trésorerie début", "Encaissements",
            "Décaissements", "Flux net", "Trésorerie fin",
        ]
        for col, header in enumerate(headers):
            ws.write(3, col, header, formats["header"])

        # Données
        for row, s in enumerate(summaries, start=4):
            ws.write(row, 0, format_month_fr(s.mois), formats["text"])
            ws.write(row, 1, s.tresorerie_debut, formats["money"])
            ws.write(row, 2, s.total_encaissements, formats["money"])
            ws.write(row, 3, abs(s.total_decaissements), formats["money_neg"])
            ws.write(row, 4, s.flux_net, formats["money_bold"])

            # Trésorerie fin : rouge si négative
            if s.tresorerie_fin < 0:
                ws.write(row, 5, s.tresorerie_fin, formats["negative_bg"])
            else:
                ws.write(row, 5, s.tresorerie_fin, formats["money_bold"])

    def _write_comparison_sheet(
        self, workbook, forecast_data: dict[str, list[MonthSummary]], formats: dict,
    ):
        """Écrit l'onglet de comparaison des 3 scénarios."""
        ws = workbook.add_worksheet("3 Scénarios")
        ws.set_column("A:A", 18)
        ws.set_column("B:J", 16)

        ws.write(0, 0, "Comparaison des scénarios", formats["title"])

        # En-têtes
        headers = ["Mois"]
        for scenario in ["Prudent", "Central", "Ambitieux"]:
            headers.extend([f"{scenario} Enc.", f"{scenario} Déc.", f"{scenario} Tréso."])

        for col, header in enumerate(headers):
            ws.write(2, col, header, formats["header"])

        # Trouver le max de mois
        all_months = set()
        for summaries in forecast_data.values():
            for s in summaries:
                all_months.add(s.mois)
        sorted_months = sorted(all_months)

        # Index par scénario et mois
        idx = {}
        for scenario, summaries in forecast_data.items():
            for s in summaries:
                idx[(scenario, s.mois)] = s

        for row, month in enumerate(sorted_months, start=3):
            ws.write(row, 0, format_month_fr(month), formats["text"])
            col = 1
            for scenario in ["prudent", "central", "ambitieux"]:
                s = idx.get((scenario, month))
                if s:
                    ws.write(row, col, s.total_encaissements, formats["money"])
                    ws.write(row, col + 1, abs(s.total_decaissements), formats["money_neg"])
                    fmt = formats["negative_bg"] if s.tresorerie_fin < 0 else formats["money_bold"]
                    ws.write(row, col + 2, s.tresorerie_fin, fmt)
                col += 3

    def _write_detail_sheet(
        self, workbook, sheet_name: str, lines: list[LignePrevisionnel], formats: dict,
    ):
        """Écrit un onglet de détail (encaissements ou décaissements)."""
        ws = workbook.add_worksheet(sheet_name)
        ws.set_column("A:A", 16)
        ws.set_column("B:B", 14)
        ws.set_column("C:C", 30)
        ws.set_column("D:E", 22)
        ws.set_column("F:F", 16)

        headers = ["Mois", "Date échéance", "Tiers", "Catégorie", "Sous-catégorie", "Montant"]
        for col, header in enumerate(headers):
            ws.write(0, col, header, formats["header"])

        for row, line in enumerate(lines, start=1):
            ws.write(row, 0, format_month_fr(line.mois), formats["text"])
            if line.date_echeance:
                ws.write(row, 1, line.date_echeance.strftime("%d/%m/%Y"), formats["text"])
            ws.write(row, 2, line.nom_tiers or "", formats["text"])
            ws.write(row, 3, line.categorie, formats["text"])
            ws.write(row, 4, line.sous_categorie or "", formats["text"])
            ws.write(row, 5, abs(line.montant), formats["money"])

        # Total
        total_row = len(lines) + 1
        ws.write(total_row, 4, "TOTAL", formats["subtitle"])
        ws.write(total_row, 5, sum(abs(l.montant) for l in lines), formats["money_bold"])
