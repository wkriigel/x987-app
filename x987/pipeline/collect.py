from ..collectors.autotempest import collect_autotempest
from ..utils import log

def run_collect(cfg):
    log.step('collect'); urls=cfg.get('search_urls',[])
    out=collect_autotempest(urls, cfg); log.ok(count=len(out)); return out

