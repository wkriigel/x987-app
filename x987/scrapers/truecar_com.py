"""
Minimal TrueCar scraper (starter).
Dependency-free: expects raw HTML string and extracts a few fields.
Extend patterns as needed in your pipeline.
"""
from __future__ import annotations
import re
from typing import Any, Dict

_PRICE = re.compile(r"\$[\s,]*([0-9][0-9,]+)")
_MILES = re.compile(r"([0-9][0-9,]+)\s*miles", re.I)
_TITLE = re.compile(r"(\d{4})\s+Porsche\s+(Cayman|Boxster)\s*(S|Spyder)?", re.I)
_TRANS = re.compile(r"\b(Manual|PDK|Automatic|Auto)\b", re.I)
_VIN = re.compile(r"\b([A-HJ-NPR-Z0-9]{17})\b")

def _to_int(s: str | None) -> int | None:
    if not s: return None
    return int(s.replace(",", ""))

def parse(html: str) -> Dict[str, Any]:
    """
    Returns a normalized dict with keys:
      price, miles, year, model, trim, transmission, vin
    Missing fields are None when not found.
    """
    price = _to_int(_first(_PRICE, html))
    miles = _to_int(_first(_MILES, html))
    year, model, trim = _title_parts(html)
    trans = _first(_TRANS, html)
    vin = _first(_VIN, html)
    return {
        "price": price,
        "miles": miles,
        "year": _to_int(year) if year else None,
        "model": _cap(model),
        "trim": _cap(trim),
        "transmission": _norm_trans(trans),
        "vin": vin,
    }

def _first(rx: re.Pattern[str], text: str) -> str | None:
    m = rx.search(text)
    return m.group(1) if m else None

def _title_parts(html: str) -> tuple[str | None, str | None, str | None]:
    m = _TITLE.search(html)
    if not m: return (None, None, None)
    return m.group(1), m.group(2), (m.group(3) or None)

def _cap(s: str | None) -> str | None:
    return s.capitalize() if isinstance(s, str) else None

def _norm_trans(s: str | None) -> str | None:
    if not s: return None
    v = s.lower()
    if "pdk" in v: return "PDK"
    if "manual" in v: return "Manual"
    if "auto" in v: return "Automatic"
    return s
