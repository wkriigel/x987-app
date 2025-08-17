from ..scrapers.cars_com import scrape_cars_com
from ..utils import log

def run_scrape(collected, cfg):
    log.step('scrape')
    cars=[c['listing_url'] for c in collected if c.get('source')=='cars.com']
    rows=scrape_cars_com(cars, cfg) if cars else []
    log.ok(count=len(rows)); return rows
