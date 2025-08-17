from statistics import median
from collections import defaultdict
from ..utils import text


def _key(r):
    return (r.model or "Unknown", r.transmission_norm or "Unknown", text.mileage_band(r.mileage))


def run_baseline(rows, cfg):
    buckets = defaultdict(list)
    for r in rows:
        if r.adj_price_usd is not None:
            buckets[_key(r)].append(r.adj_price_usd)
    med = {k: int(median(v)) for k, v in buckets.items() if v}
    for r in rows:
        k = _key(r)
        base = med.get(k)
        r.baseline_adj_price_usd = base
        r.deal_delta_usd = (
            int(base - r.adj_price_usd)
            if (base is not None and r.adj_price_usd is not None)
            else None
        )
    return med
