from __future__ import annotations
import argparse, csv, pathlib
from playwright.sync_api import sync_playwright
from x987.collectors.autotempest import _collect_from_page
from x987.scrapers import truecar_com

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--limit", type=int, default=10)
    ap.add_argument("--timeout_ms", type=int, default=15000)
    args = ap.parse_args()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(args.url, timeout=args.timeout_ms, wait_until="domcontentloaded")
        entries = _collect_from_page(page)
        browser.close()

    urls = [e.get("listing_url") for e in entries if e.get("source") == "truecar"]
    urls = [u for u in urls if isinstance(u, str) and u][: args.limit]
    rows = truecar_com.scrape_truecar(urls, {"network": {"timeout_ms": args.timeout_ms}})

    out = (pathlib.Path(__file__).resolve().parents[2] / "x987-data" / "normalized" / "truecar_preview.csv")
    out.parent.mkdir(parents=True, exist_ok=True)
    keys = ["price","miles","year","model","trim","transmission","vin","location","source","listing_url"]
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k) for k in keys})
    print(f"Wrote {len(rows)} rows to {out}")

if __name__ == "__main__":
    main()
