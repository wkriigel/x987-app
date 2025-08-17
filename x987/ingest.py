# FILE: x987/ingest.py
# CONTRACT: read latest raw scrape CSV and any manual CSVs; return list[dict] with best-effort coercions

import csv
import pathlib
import ast
from .settings import get_paths
from .utils import text


def _read_csv(fp: pathlib.Path):
    rows = []
    try:
        with open(fp, "r", encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                rows.append(dict(row))
    except Exception:
        pass
    return rows


def _coerce_row(r: dict) -> dict:
    # Best-effort numeric coercions
    for k in ("price_usd", "mileage", "year"):
        if r.get(k) not in (None, ""):
            v = text.parse_int(r.get(k))
            r[k] = int(v) if v is not None else None
        else:
            r[k] = None

    # raw_options: list[str]
    ro = r.get("raw_options")
    if isinstance(ro, list):
        pass
    elif isinstance(ro, str):
        s = ro.strip()
        parsed = None
        if s.startswith("[") and s.endswith("]"):
            try:
                parsed = ast.literal_eval(s)
            except Exception:
                parsed = None
        if parsed is None:
            parsed = [p.strip() for p in s.split(";") if p.strip()] if s else []
        r["raw_options"] = parsed
    else:
        r["raw_options"] = []

    # normalize keys that might appear with different casing
    if r.get("Transmission"):
        r["transmission_raw"] = r.get("Transmission")
    if r.get("URL") and not r.get("listing_url"):
        r["listing_url"] = r["URL"]
    if r.get("Source") and not r.get("source"):
        r["source"] = r["Source"]

    return r


def load_raw_and_manual():
    paths = get_paths()
    raw_latest = pathlib.Path(paths["RAW_DIR"]) / "latest.csv"
    all_rows = []

    # Latest raw (from last scrape)
    if raw_latest.exists():
        all_rows += _read_csv(raw_latest)

    # Manual CSVs (drop files into %APPDATA%/x987/input/manual/)
    manual_dir = pathlib.Path(paths["USER_INPUT_MANUAL"])
    if manual_dir.exists():
        for fp in manual_dir.glob("*.csv"):
            all_rows += _read_csv(fp)

    # Coerce fields
    all_rows = [_coerce_row(r) for r in all_rows]
    return all_rows
