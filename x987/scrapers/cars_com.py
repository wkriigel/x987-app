# FILE: x987/scrapers/cars_com.py
from playwright.sync_api import sync_playwright
import re

BLOCK_URL_SUBSTR = [
    "googletagmanager.com", "google-analytics.com", "doubleclick.net",
    "facebook.net", "adservice.google", "adsystem", "scorecardresearch",
    "criteo", "hotjar", "optimizely", "segment.io", "newrelic", "snowplow"
]

def _install_blocking(context, cfg):
    nw = cfg.get("network", {}) or {}
    block_types = set()
    if nw.get("block_images", True): block_types.add("image")
    if nw.get("block_media", True): block_types.add("media")
    if nw.get("block_fonts", True): block_types.add("font")
    if nw.get("block_stylesheets", True): block_types.add("stylesheet")
    block_analytics = nw.get("block_analytics", True)

    def _maybe_block(route):
        req = route.request
        if req.resource_type in block_types: return route.abort()
        if block_analytics and any(s in req.url for s in BLOCK_URL_SUBSTR): return route.abort()
        return route.continue_()

    context.route("**/*", _maybe_block)

def _text(page):
    try: return page.locator("body").inner_text()
    except Exception: return ""

def _find(pat, txt):
    m = re.search(pat, txt, re.I | re.S)
    return m.group(1).strip() if m else None

def _clean_color(val):
    if not val: return None
    s = str(val).strip()
    if len(s) <= 2: return None
    return s
def _none_if_na(s: str | None):
    if not s: 
        return None
    t = re.sub(r"\s+", "", s).lower()
    if t in {"-", "â€“", "â€”", "n/a", "na", "notspecified"}:
        return None
    return s.strip()

def _dd_for(page, label: str) -> str | None:
    # Read the first <dd> following a <dt> whose text matches `label`
    try:
        loc = page.locator(f'xpath=//dt[normalize-space()="{label}"]/following-sibling::dd[1]').first
        if loc.count() > 0:
            txt = loc.inner_text()
            # collapse whitespace
            return re.sub(r"\s+", " ", txt).strip()
    except Exception:
        pass
    return None


# Color normalization
_COLOR_CORE = r"(?:Black|White|Gray|Grey|Silver|Red|Blue|Green|Tan|Beige|Brown|Gold|Purple|Burgundy|Yellow|Orange|Ivory|Cream|Pearl|Metallic)"
_COLOR_ADJ  = r"(?:[A-Z][a-z]+|Arctic|Meteor|Classic|Carrera|Basalt|Carmine|Aqua|Racing|Guards|Seal|Sand|Sapphire|Slate|Midnight|Jet|Polar|Macadamia|Champagne)"
_COLOR_PHRASE_RE = re.compile(
    rf"^\s*((?:{_COLOR_ADJ}\s+)*{_COLOR_CORE}(?:\s+Metallic|\s+Pearl)?)\b"
)
def _norm_color_phrase(s: str | None):
    if not s: return None
    m = _COLOR_PHRASE_RE.search(s)
    return m.group(1) if m else None

# Centralized trim inference
def _infer_trim(title: str | None, body: str) -> str | None:
    t = title or ""

    # Special trims (title only)
    if re.search(r"\bCayman\s+R\b", t, re.I): return "R"
    if re.search(r"\bBoxster\s+Spyder\b", t, re.I): return "Spyder"
    if re.search(r"\bBlack\s+Edition\b", t, re.I): return "Black Edition"

    # Explicit S in title
    if re.search(r"\b(Cayman|Boxster)\s+S\b", t, re.I): return "S"

    # Explicit Base hints
    if re.search(r"\bCayman\s+Base\b", t, re.I): return "Base"
    if re.search(r"\bBASE\s+Cayman\b", body, re.I): return "Base"

    # Default to Base when title is neutral
    trim = "Base"

    # Engine displacement override (only if unambiguous)
    has29 = re.search(r"\b2[\.,]9\s*l\b|\b2\.9l\b", body, re.I)
    has34 = re.search(r"\b3[\.,]4\s*l\b|\b3\.4l\b", body, re.I)
    if has34 and not has29:
        trim = "S"
    elif has29 and not has34:
        trim = "Base"

    return trim

def scrape_cars_com(urls, cfg):
    rows = []
    polite = int(cfg.get("polite_delay_ms", 900))
    debug = bool(cfg.get("debug", True))

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(ignore_https_errors=True)
        context.set_default_timeout(10_000)
        _install_blocking(context, cfg)
        page = context.new_page()

        for url in urls:
            try:
                page.goto(url, wait_until="domcontentloaded")
                page.wait_for_timeout(polite)
                body = _text(page)

                price = _find(r"\$(\d[\d,]+)", body)
                miles = _find(r"(\d[\d,]+)\s*(?:miles|mi)\b", body) or _find(r"mileage\s*:?\s*(\d[\d,]+)", body)
                title = _find(r"(20\d\d\s+Porsche\s+\w+[^\n]+)", body) or _find(r"(20\d\d\s+Porsche\s+\w+)", body)

                # Year/model from title
                year = model = None
                if title:
                    m = re.search(r"(20\d\d)\s+Porsche\s+(Cayman|Boxster)", title, re.I)
                    if m:
                        year = int(m.group(1))
                        model = m.group(2).title()

                # Trim via consolidated logic
                trim = _infer_trim(title, body)

                # Transmission (raw)
                trans = _find(r"Transmission\s*:?\s*([A-Za-z0-9\- /]+)", body) or _find(r"([AP]utomatic|PDK|Tiptronic|Manual)", body)

                # Colors â€“ DOM first
                ext_dom = _none_if_na(_dd_for(page, "Exterior color"))
                int_dom = _none_if_na(_dd_for(page, "Interior color"))

                extc = _norm_color_phrase(_clean_color(ext_dom))
                intc = _norm_color_phrase(_clean_color(int_dom))

                # Fallbacks if DOM didnâ€™t yield values (keep our previous heuristics)
                if not extc or not intc:
                    lab_ext = _find(r"Exterior\s*color\s*:?\s*([A-Za-z \-]+)", body)
                    lab_int = _find(r"Interior\s*color\s*:?\s*([A-Za-z \-]+)", body)
                    if not extc:
                        extc = _norm_color_phrase(_clean_color(lab_ext))
                    if not intc:
                        intc = _norm_color_phrase(_clean_color(lab_int))

                if not extc or not intc:
                    m = re.search(
                        rf"(({_COLOR_ADJ}\s+)*{_COLOR_CORE}(?:\s+Metallic|\s+Pearl)?)\s+Exterior\s+(({_COLOR_ADJ}\s+)*{_COLOR_CORE}(?:\s+Metallic|\s+Pearl)?)\s+Interior",
                        body, re.I
                    )
                    if m:
                        extc = extc or _norm_color_phrase(m.group(1))
                        intc = intc or _norm_color_phrase(m.group(3))

                if not extc or not intc:
                    m = re.search(
                        rf"(({_COLOR_ADJ}\s+)*{_COLOR_CORE}(?:\s+Metallic|\s+Pearl)?)\s+(?:on|over)\s+(({_COLOR_ADJ}\s+)*{_COLOR_CORE}(?:\s+Metallic|\s+Pearl)?)",
                        body, re.I
                    )
                    if m:
                        extc = extc or _norm_color_phrase(m.group(1))
                        intc = intc or _norm_color_phrase(m.group(3))

                if not extc or not intc:
                    m = re.search(
                        rf"(({_COLOR_ADJ}\s+)*{_COLOR_CORE}(?:\s+Metallic|\s+Pearl)?)\s+Exterior\s+(({_COLOR_ADJ}\s+)*{_COLOR_CORE}(?:\s+Metallic|\s+Pearl)?)\s+Interior",
                        body, re.I
                    )
                    if m:
                        extc = extc or _norm_color_phrase(m.group(1))
                        intc = intc or _norm_color_phrase(m.group(3))
                if not extc or not intc:
                    m = re.search(
                        rf"(({_COLOR_ADJ}\s+)*{_COLOR_CORE}(?:\s+Metallic|\s+Pearl)?)\s+(?:on|over)\s+(({_COLOR_ADJ}\s+)*{_COLOR_CORE}(?:\s+Metallic|\s+Pearl)?)",
                        body, re.I
                    )
                    if m:
                        extc = extc or _norm_color_phrase(m.group(1))
                        intc = intc or _norm_color_phrase(m.group(3))

                # VIN & location
                vin  = _find(r"VIN\s*:?\s*([A-HJ-NPR-Z0-9]{11,17})", body)
                loc  = _find(r"(?:Dealer location|Location)\s*:?\s*([A-Za-z ,]+)", body) or _find(r"([A-Za-z .]+,\s*[A-Z]{2})", body)

                # Options: capture any lines that match configured option patterns
                # so transform/options.py can canonicalize later.
                opt_lines = set()
                try:
                    # inside cars_com.py where you compile option patterns:
                    op2 = (cfg.get("options_v2") or {}).get("catalog", [])  # v2
                    pats = []
                    for item in op2:
                        for pat in (item.get("synonyms") or []):
                            try: pats.append(re.compile(pat, re.I))
                            except re.error: pass
                    # Fallback simple keywords so we don't regress if catalog is empty
                    if not pats:
                        for kw in ["sport chrono", "pasm", "sport exhaust", "pse", "limited slip", "lsd", "sport seats", "adaptive sport seats"]:
                            pats.append(re.compile(re.escape(kw), re.I))
                
                    for line in body.splitlines():
                        s = line.strip()
                        if not s:
                            continue
                        if any(p.search(s) for p in pats):
                            opt_lines.add(s)
                except Exception:
                    pass


                row = {
                    "source": "cars.com", "listing_url": url,
                    "price_usd": int(price.replace(",", "")) if price else None,
                    "mileage": int(miles.replace(",", "")) if miles else None,
                    "year": year, "model": model, "trim": trim,
                    "transmission_raw": trans,
                    "exterior_color": extc, "interior_color": intc,
                    "vin": vin, "location": loc, "description_raw": None,
                    "raw_options": sorted(opt_lines), "photos_count": None, "seller_type": None
                }

                # Optional: write trim debug into RAW CSV when debug=true
                if debug:
                    row["_trim_title"] = title or ""
                    row["_has_29L"] = bool(re.search(r"\b2[\.,]9\s*l\b|\b2\.9l\b", body, re.I))
                    row["_has_34L"] = bool(re.search(r"\b3[\.,]4\s*l\b|\b3\.4l\b", body, re.I))

                rows.append(row)

            except Exception as e:
                rows.append({"source": "cars.com", "listing_url": url, "error": str(e)})

        browser.close()
    return rows







