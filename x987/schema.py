from dataclasses import dataclass, field
from typing import Optional, List
@dataclass
class Listing:
    timestamp_run_id: str
    source: str
    listing_url: str
    vin: Optional[str]=None
    year: Optional[int]=None
    model: Optional[str]=None
    trim: Optional[str]=None
    transmission_norm: Optional[str]=None
    transmission_raw: Optional[str]=None
    mileage: Optional[int]=None
    price_usd: Optional[int]=None
    exterior_color: Optional[str]=None
    interior_color: Optional[str]=None
    color_ext_bucket: Optional[str]=None
    color_int_bucket: Optional[str]=None
    raw_options: List[str]=field(default_factory=list)
    top5_options_count: int=0
    top5_options_present: List[str]=field(default_factory=list)
    location: Optional[str]=None
    adj_price_usd: Optional[int]=None
    baseline_adj_price_usd: Optional[int]=None
    deal_delta_usd: Optional[int]=None
def completeness_score(lst: Listing)->int:
    score=0
    for f in ["vin","price_usd","mileage","year","model","trim","exterior_color","interior_color","location"]:
        score+=1 if getattr(lst,f) not in (None,"",[]) else 0
    return score

