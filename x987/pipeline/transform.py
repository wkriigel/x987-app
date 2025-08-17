from ..schema import Listing
from ..utils import text, log
import re

# Expand top-5 matching tokens (simple substrings)
TOP5 = [
    "sport chrono", "pasm", "pse", "sport exhaust",
    "limited slip", "lsd", "sport seats", "adaptive sport seats"
]

def _norm_trans(raw: str | None):
    s = (raw or "").lower()

    # Manual first to avoid "7-speed manual" misclassifying as auto
    if re.search(r"\b(manual|6[-\s]?speed|6\s*spd|6spd|6mt)\b", s):
        return "Manual"

    # Automatic / PDK / Tiptronic patterns
    if (
        re.search(r"\b(pdk|doppelkupplung|tiptronic|automatic|auto|a/?t)\b", s)
        or (re.search(r"\b7[-\s]?speed\b", s) and "manual" not in s)
    ):
        return "Automatic"

    return None  # unknown; weâ€™ll still display raw text

def _top5_detect(raw_options: list[str]):
    present = set()
    raw = " | ".join([o.lower() for o in (raw_options or [])])
    for key in TOP5:
        if key in raw:
            if "sport exhaust" in key or "pse" in key:
                present.add("PSE")
            elif "limited slip" in key or "lsd" in key:
                present.add("LSD")
            elif "sport chrono" in key:
                present.add("Sport Chrono")
            elif "pasm" in key:
                present.add("PASM")
            elif "sport seats" in key:
                present.add("Sport Seats")
    return sorted(present)

def _norm_trim(trim: str | None):
    if not trim:
        return None
    t = trim.strip()
    # Common cases: "s" -> "S"; otherwise keep original (some trims contain words)
    return "S" if t.lower() == "s" else t

def run_transform(raw_rows, cfg, run_id):
    log.step("transform")
    out = []
    miny, maxy = int(cfg.get("min_year", 2009)), int(cfg.get("max_year", 2012))

    for r in raw_rows:
        year = r.get("year")
        if year and (year < miny or year > maxy):
            continue

        # Coerce options defensively (manual CSVs)
        raw_opts = r.get("raw_options") or []
        if isinstance(raw_opts, str):
            raw_opts = [p.strip() for p in raw_opts.split(";") if p.strip()]

        v = Listing(
            timestamp_run_id=run_id,
            source=r.get("source", ""),
            listing_url=r.get("listing_url", ""),
            vin=r.get("vin"),
            year=year,
            model=(r.get("model") or None),
            trim=_norm_trim(r.get("trim")),
            transmission_raw=r.get("transmission_raw"),
            transmission_norm=_norm_trans(r.get("transmission_raw")),
            mileage=r.get("mileage"),
            price_usd=r.get("price_usd"),
            exterior_color=r.get("exterior_color"),
            interior_color=r.get("interior_color"),
            color_ext_bucket="color" if text.is_color(r.get("exterior_color")) else "mono",
            color_int_bucket="color" if text.is_color(r.get("interior_color")) else "mono",
            raw_options=raw_opts,
            location=r.get("location"),
        )

        present = _top5_detect(v.raw_options) if not _v2_enabled else []
        v.top5_options_present = present
        v.top5_options_count = len(present)
        out.append(v)

    log.ok(count=len(out))
    return out


