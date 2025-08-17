# FILE: x987/cli.py
from .settings import load_config, get_paths
from .doctor import run_doctor
from .utils.io import timestamp_run_id, safe_write_csv, write_latest_alias
from .utils import log
from .pipeline.collect import run_collect
from .pipeline.scrape import run_scrape
from .pipeline.transform import run_transform
from .pipeline.dedupe import run_dedupe
from .pipeline.fairvalue import run_fairvalue
from .pipeline.rank import run_rank
from .view.report import print_table
from .ingest import load_raw_and_manual
from .pipeline.cache import load_latest_normalized_rows

# options
from .pipeline.options_v2 import recompute_options_v2
from .pipeline.options import recompute_top5_options
import os


def main():
    cfg = load_config()
    run_doctor(cfg)
    paths = get_paths()
    run_id = timestamp_run_id()

    use_cached = bool((cfg.get("dev") or {}).get("use_cached_normalized", False))

    if use_cached:
        log.step("cached")
        deduped = load_latest_normalized_rows(cfg)
        log.ok(path=os.path.join(paths["NORM_DIR"], "latest.csv"), count=len(deduped))
    else:
        # Collect â†’ Scrape
        coll = run_collect(cfg)
        scraped = run_scrape(coll, cfg)

        # Persist raw scrape and alias latest
        raw_out = os.path.join(paths["RAW_DIR"], f"scrape_{run_id}_AT_n{len(scraped):03d}.csv")
        safe_write_csv(scraped, raw_out)
        write_latest_alias(raw_out, os.path.join(paths["RAW_DIR"], "latest.csv"))

        # Ingest latest raw + manual CSVs
        raw_rows = load_raw_and_manual()

        # Transform â†’ Dedupe
        transformed = run_transform(raw_rows, cfg, run_id)
        deduped = run_dedupe(transformed)

    # Options (v2 preferred, falls back to existing Top-5)
    if (cfg.get("options_v2") or {}).get("enabled", False):
        recompute_options_v2(deduped, cfg)
    else:
        recompute_top5_options(deduped, cfg)

    # Fair value (dollars model) â†’ Rank
    run_fairvalue(deduped, cfg)
    csv_rows, view_rows = run_rank(deduped)

    # Write normalized + show
    norm_out = os.path.join(paths["NORM_DIR"], f"run_{run_id}_n{len(csv_rows):03d}.csv")
    safe_write_csv(csv_rows, norm_out)
    write_latest_alias(norm_out, os.path.join(paths["NORM_DIR"], "latest.csv"))

    print_table(view_rows)
    log.info(f"Wrote: {norm_out}")
    log.info(f"Latest CSV: {os.path.join(paths['NORM_DIR'], 'latest.csv')}")

