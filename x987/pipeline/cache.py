# FILE: x987/pipeline/cache.py
import csv, os
from types import SimpleNamespace
from ..utils import log
from ..settings import get_paths

_NUMERIC_INT = {
    "price_usd", "mileage", "year", "deal_delta_usd", "fair_value_usd",
    "top5_options_count"
}

_LIST_SEMI = {
    "top5_options_present",  # "A; B; C"
    "raw_options",           # "line1; line2"
}

def _to_int(v):
    if v is None or v == "": return None
    try:
        return int(str(v).replace(",", ""))
    except Exception:
        return None

def _split_semi(v):
    if not v: return []
    parts = [p.strip() for p in str(v).split(";")]
    return [p for p in parts if p]

def load_latest_normalized_rows(cfg):
    paths = get_paths()
    latest = os.path.join(paths["NORM_DIR"], "latest.csv")
    if not os.path.isfile(latest):
        raise FileNotFoundError(f"No latest normalized CSV at {latest}. "
                                f"Run once with dev.use_cached_normalized=false to create it.")
    rows = []
    with open(latest, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            obj = {}
            for k, v in row.items():
                if k in _NUMERIC_INT:
                    obj[k] = _to_int(v)
                elif k in _LIST_SEMI:
                    obj[k] = _split_semi(v)
                else:
                    obj[k] = v or ""
            # ensure attributes that ranking/fairvalue expect exist
            obj.setdefault("transmission_norm", "")
            obj.setdefault("transmission_raw", "")
            obj.setdefault("color_ext_bucket", "")
            obj.setdefault("color_int_bucket", "")
            obj.setdefault("model", "")
            obj.setdefault("trim", "")
            obj.setdefault("exterior_color", "")
            obj.setdefault("interior_color", "")
            obj.setdefault("source", "")
            obj.setdefault("listing_url", "")
            rows.append(SimpleNamespace(**obj))
    log.ok(path=latest, count=len(rows))
    return rows
