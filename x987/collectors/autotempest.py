from playwright.sync_api import sync_playwright

BLOCK_URL_SUBSTR = [
    "googletagmanager.com", "google-analytics.com", "doubleclick.net",
    "facebook.net", "adservice.google", "adsystem", "scorecardresearch",
    "criteo", "hotjar", "optimizely", "segment.io", "newrelic", "snowplow"
]

def _install_blocking(context, cfg):
    nw = cfg.get("network", {}) or {}
    block_types = set()
    if nw.get("block_images", True):
        block_types.add("image")
    if nw.get("block_media", True):
        block_types.add("media")
    if nw.get("block_fonts", True):
        block_types.add("font")
    if nw.get("block_stylesheets", True):
        block_types.add("stylesheet")
    block_analytics = nw.get("block_analytics", True)

    def _maybe_block(route):
        req = route.request
        if req.resource_type in block_types:
            return route.abort()
        if block_analytics and any(s in req.url for s in BLOCK_URL_SUBSTR):
            return route.abort()
        return route.continue_()

    context.route("**/*", _maybe_block)

def _auto_reveal(page, cfg):
    nw = cfg.get("network", {}) or {}
    max_clicks = int(nw.get("max_clicks_more", 6))
    max_scrolls = int(nw.get("max_scroll_rounds", 8))

    # Try clicking the "More Cars.com Results" button up to N times
    for _ in range(max_clicks):
        try:
            loc = page.locator(r'text=/More\s+Cars\.com\s+Results/i').first
            if loc.count() > 0:
                loc.click(timeout=1000)
                page.wait_for_timeout(300)
            else:
                break
        except Exception:
            break

    # Then auto-scroll to bottom a few rounds to trigger lazy lists
    last_count = -1
    for _ in range(max_scrolls):
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(300)
        # If no new links appear, stop
        count = page.locator('a[href*="cars.com/vehicledetail"], a[href*="truecar.com/used-cars-for-sale/listing"]').count()
        if count == last_count:
            break
        last_count = count

def _collect_from_page(page):
    # Collect Cars.com + TrueCar listing links
    urls = set()
    try:
        # Cars.com
        links1 = page.locator('a[href*="cars.com/vehicledetail"]')
        n1 = links1.count()
        for i in range(n1):
            href = links1.nth(i).get_attribute("href")
            if href and "cars.com/vehicledetail" in href:
                urls.add(("cars.com", href.split("?")[0]))
        # TrueCar
        links2 = page.locator('a[href*="truecar.com/used-cars-for-sale/listing"]')
        n2 = links2.count()
        for i in range(n2):
            href = links2.nth(i).get_attribute("href")
            if href and "/used-cars-for-sale/listing" in href:
                urls.add(("truecar", href.split("?")[0]))
    except Exception:
        pass
    return [{"source": s, "listing_url": u} for (s, u) in urls]

def collect_autotempest(urls, cfg):
    out = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(ignore_https_errors=True)
        context.set_default_timeout(10_000)
        _install_blocking(context, cfg)
        page = context.new_page()

        for u in urls:
            page.goto(u, wait_until="domcontentloaded")
            page.wait_for_timeout(500)
            _auto_reveal(page, cfg)
            out += _collect_from_page(page)

        browser.close()
    return out













