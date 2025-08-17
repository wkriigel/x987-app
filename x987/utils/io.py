import csv
import os
import shutil
import datetime
import pathlib


def _ordered_headers(rows):
    if not rows:
        return []
    keys = set()
    for r in rows:
        keys.update(r.keys())
    hint = [
        "source",
        "listing_url",
        "vin",
        "year",
        "model",
        "trim",
        "transmission_raw",
        "transmission_norm",
        "mileage",
        "price_usd",
        "exterior_color",
        "interior_color",
        "color_ext_bucket",
        "color_int_bucket",
        "raw_options",
        "top5_options_count",
        "top5_options_present",
        "location",
        "adj_price_usd",
        "baseline_adj_price_usd",
        "deal_delta_usd",
        "error",
        "timestamp_run_id",
    ]
    ordered = [k for k in hint if k in keys]
    ordered += [k for k in keys if k not in set(ordered)]
    return ordered


def safe_write_csv(rows, out_path):
    if not rows:
        return
    p = pathlib.Path(out_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".tmp")
    headers = _ordered_headers(rows)
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    os.replace(tmp, p)


def write_latest_alias(actual_path, latest_path):
    shutil.copyfile(actual_path, latest_path)


def timestamp_run_id():
    return datetime.datetime.now(datetime.UTC).strftime("%Y%m%d_%H%M%S")

