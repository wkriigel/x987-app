# v3: Universal headful scraper + options_v2 + lean repo

## Goals
- Keep pricing/scoring + table view unchanged.
- Headful-only navigation/scraping.
- AutoTempest-first collector producing mixed VDPs (cars.com, truecar.com, carvana.com).
- Universal VDP scraper with small site profiles.
- Adopt options_v2; remove legacy options logic.
- Trim deps and nonessential tests/lints.

## Changes
- [ ] Add `scrapers/universal_vdp.py` and profiles for cars_com / truecar_com / carvana_com.
- [ ] Extend `collectors/autotempest.py` to return mixed hosts.
- [ ] Route all VDPs via the universal scraper from `pipeline/scrape.py`.
- [ ] Replace legacy options with `options_v2` import in `pipeline/transform.py`.
- [ ] Prune requirements + doctor checks to minimal deps.
- [ ] Remove vestigial files and extra tests/lints.

## Acceptance
- [ ] `python -m x987` headful run completes; CSVs non-empty; table renders.
- [ ] Raw CSV shows cars.com, truecar.com, and carvana.com sources.
- [ ] Pricing/scoring/view unchanged vs. v2 Cars.com-only baseline.
- [ ] Minimal dependencies only; doctor OK.
- [ ] Repo is free of vestigial files.
