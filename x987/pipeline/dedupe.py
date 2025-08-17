from ..schema import completeness_score
from ..utils import log

def run_dedupe(rows):
    log.step('dedupe'); by_vin={}; no_vin=[]
    for r in rows:
        if r.vin:
            prev=by_vin.get(r.vin)
            if not prev or completeness_score(r)>completeness_score(prev): by_vin[r.vin]=r
        else: no_vin.append(r)
    out=list(by_vin.values())+no_vin; log.ok(count=len(out)); return out
