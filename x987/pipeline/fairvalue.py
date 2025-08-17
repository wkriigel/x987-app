# FILE: x987/pipeline/fairvalue.py
from ..utils import log


def _cfg(d, key, default):
    return (d.get(key) if isinstance(d, dict) else None) or default


def _norm(s):
    return (s or "").strip()


def _mileage_band(miles):
    if miles is None:
        return "60-79k"  # neutral band if missing (for processing only)
    try:
        m = int(miles)
    except Exception:
        return "60-79k"
    if m < 40000:
        return "<40k"
    if m < 60000:
        return "40-59k"
    if m < 80000:
        return "60-79k"
    if m < 100000:
        return "80-99k"
    return ">=100k"


def _trim_premium(fv_cfg, row):
    # Prefer explicit trim name; fall back to empty/base
    trim = _norm(getattr(row, "trim", ""))
    premiums = fv_cfg.get("trim_premiums") or {}
    if trim in premiums:
        try:
            return int(premiums[trim])
        except Exception:
            return 0

    # map common variants (e.g. Black Edition might appear in model/trim)
    y = f"{_norm(getattr(row, 'model', ''))} {_norm(getattr(row, 'trim', ''))}".strip().lower()
    for k, v in premiums.items():
        if k.lower() in y:
            try:
                return int(v)
            except Exception:
                return 0
    return 0  # Base


def _year_step(fv_cfg, row):
    step = int(_cfg(fv_cfg, "year_step_usd", 0))
    year = getattr(row, "year", None)
    min_year = 2009
    try:
        y = int(year) if year is not None else min_year
    except Exception:
        y = min_year
    # linear steps from baseline year (2009)
    return (y - min_year) * step


def _mileage_adj(fv_cfg, row):
    bands = fv_cfg.get("mileage_band_bonus_usd") or {}
    band = _mileage_band(getattr(row, "mileage", None))
    try:
        return int(bands.get(band, 0))
    except Exception:
        return 0


def _color_adj(fv_cfg, row):
    ext_bucket = _norm(getattr(row, "color_ext_bucket", ""))  # 'color' vs mono
    int_bucket = _norm(getattr(row, "color_int_bucket", ""))
    int_bonus = (
        int(_cfg(fv_cfg, "interior_color_color_usd", 0)) if int_bucket.lower() == "color" else 0
    )
    ext_bonus = (
        int(_cfg(fv_cfg, "exterior_color_color_usd", 0)) if ext_bucket.lower() == "color" else 0
    )
    return int_bonus + ext_bonus


def _options_total(row, fv_cfg):
    # Prefer v2 option dollars if present, else fallback to legacy count if v2 labels missing (rare)
    v2_total = getattr(row, "option_value_usd_total", None)
    if v2_total is not None:
        try:
            return int(v2_total)
        except Exception:
            return 0
    per = int(_cfg(fv_cfg, "top5_option_value_usd", 0))
    cnt = int(getattr(row, "top5_options_count", 0) or 0)
    return per * cnt


def run_fairvalue(rows, cfg):
    """
    Compute fair value dollars for each row using the simple additive model:
      fair_value = base_value + trim_premium + year_step + mileage_adj + color_adj + options_total

    Write back:
      - baseline_adj_price_usd: base + trim + year + mileage + color (no options)
      - adj_price_usd: baseline + options_total
      - deal_delta_usd: adj_price_usd - price_usd  (positive = good deal)
    """
    log.step("fairvalue")
    fv_cfg = cfg.get("fair_value") or {}
    base_value = int(_cfg(fv_cfg, "base_value_usd", 0))
    count = 0

    for r in rows:
        try:
            price = getattr(r, "price_usd", None)
            price = int(price) if price is not None else None

            trim_adj = _trim_premium(fv_cfg, r)
            year_adj = _year_step(fv_cfg, r)
            mile_adj = _mileage_adj(fv_cfg, r)
            color_adj = _color_adj(fv_cfg, r)
            opt_total = _options_total(r, fv_cfg)

            baseline = base_value + trim_adj + year_adj + mile_adj + color_adj
            fair_val = baseline + opt_total

            setattr(r, "baseline_adj_price_usd", baseline)
            setattr(r, "adj_price_usd", fair_val)

            if price is not None:
                setattr(r, "deal_delta_usd", fair_val - price)
            else:
                setattr(r, "deal_delta_usd", None)
            count += 1
        except Exception:
            # keep moving; row remains without fairvalue if something is malformed
            pass

    log.ok(count=count)
    return rows
