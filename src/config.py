"""Paths and constants."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
REPORT_DIR = ROOT / "reports"
FIG_DIR = REPORT_DIR / "figures"
PBI_DIR = ROOT / "powerbi" / "data"

YEARS = [2023, 2024, 2025]
