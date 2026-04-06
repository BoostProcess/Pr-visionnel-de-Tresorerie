"""Parseur de fichiers Sage 100 (CSV et Excel)."""

from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

import pandas as pd

from app.imports.field_mappings import FIELD_MAPPINGS, DATE_FIELDS, AMOUNT_FIELDS
from config import SAGE_CSV_SEPARATOR, SAGE_DATE_FORMATS, SAGE_ENCODING


class SageFileParser:
    """Parse un fichier CSV ou Excel exporté depuis Sage 100."""

    def __init__(self, file_path: str, file_type: str, encoding: str | None = None):
        self.file_path = Path(file_path)
        self.file_type = file_type
        self.encoding = encoding or SAGE_ENCODING
        self.mapping = FIELD_MAPPINGS.get(file_type, {})

    def parse(self) -> list[dict]:
        """Lit le fichier et retourne une liste de dictionnaires normalisés."""
        df = self._read_file()
        rows = []
        for _, raw_row in df.iterrows():
            normalized = self._normalize_row(raw_row.to_dict())
            if normalized:
                rows.append(normalized)
        return rows

    def _read_file(self) -> pd.DataFrame:
        """Lit le fichier CSV ou Excel selon l'extension."""
        suffix = self.file_path.suffix.lower()
        if suffix in (".csv", ".txt"):
            return pd.read_csv(
                self.file_path,
                sep=SAGE_CSV_SEPARATOR,
                encoding=self.encoding,
                dtype=str,
                keep_default_na=False,
            )
        elif suffix in (".xlsx", ".xls"):
            return pd.read_excel(
                self.file_path,
                dtype=str,
                keep_default_na=False,
            )
        else:
            raise ValueError(f"Format de fichier non supporté : {suffix}")

    def _normalize_row(self, raw_row: dict) -> dict | None:
        """Applique le mapping et convertit les types."""
        result = {}
        for sage_col, internal_field in self.mapping.items():
            value = raw_row.get(sage_col, "")
            if isinstance(value, str):
                value = value.strip()

            if sage_col in DATE_FIELDS or internal_field in DATE_FIELDS:
                value = self._parse_date(value)
            elif sage_col in AMOUNT_FIELDS or internal_field in AMOUNT_FIELDS:
                value = self._parse_amount(value)
            elif internal_field == "is_inactive":
                value = str(value) == "1"
                internal_field = "is_active"
                value = not value

            result[internal_field] = value

        return result if result else None

    @staticmethod
    def _parse_date(value) -> date | None:
        """Parse une date Sage (JJ/MM/AAAA, AAAAMMJJ, AAAA-MM-JJ)."""
        if not value or value == "":
            return None
        if isinstance(value, (date, datetime)):
            return value if isinstance(value, date) else value.date()

        value_str = str(value).strip()
        for fmt in SAGE_DATE_FORMATS:
            try:
                return datetime.strptime(value_str, fmt).date()
            except ValueError:
                continue
        return None

    @staticmethod
    def _parse_amount(value) -> int:
        """Parse un montant Sage (virgule décimale) en entier XPF."""
        if not value or value == "":
            return 0
        value_str = str(value).strip().replace(" ", "").replace("\u00a0", "")
        value_str = value_str.replace(",", ".")
        try:
            return int(round(Decimal(value_str)))
        except (InvalidOperation, ValueError):
            return 0
