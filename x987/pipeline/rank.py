# FILE: x987/pipeline/rank.py
from ..utils import text


def run_rank(rows):
    def sort_key(r):
        # group: Automatic (PDK/Tip) first, then Manual
        trans = (getattr(r, "transmission_norm", "") or "").lower()
        trans_group = 0 if trans == "automatic" else 1
        # sort by deal delta (desc), then price (asc)
        delta = getattr(r, "deal_delta_usd", None)
        # None-safe: if delta is None, push to worst end
        sort_delta = -delta if isinstance(delta, (int, float)) else 10**9
        price = getattr(r, "price_usd", None)
        sort_price = price if isinstance(price, (int, float)) else 10**9
        return (trans_group, sort_delta, sort_price)

    rs = sorted(rows, key=sort_key)

    view = []
    csv = []
    for r in rs:
        # build display trim (hide "Base")
        trim_val = (getattr(r, "trim", "") or "").strip()
        display_trim = "" if trim_val.lower() in ("", "base") else trim_val
        parts = [
            str(getattr(r, "year", "") or "").strip(),
            str(getattr(r, "model", "") or "").strip(),
        ]
        if display_trim:
            parts.append(display_trim)
        ymt = " ".join([p for p in parts if p])

        # Top Options labels (v2) fallback to legacy if missing
        top_labels = getattr(r, "option_labels_display", None)
        if not top_labels:
            top_labels = getattr(r, "top5_options_present", []) or []

        # CSV row (full fidelity)
        csv.append(
            {
                "timestamp_run_id": getattr(r, "timestamp_run_id", ""),
                "source": getattr(r, "source", ""),
                "listing_url": getattr(r, "listing_url", ""),
                "vin": getattr(r, "vin", ""),
                "year": getattr(r, "year", ""),
                "model": getattr(r, "model", ""),
                "trim": getattr(r, "trim", ""),
                "transmission_norm": getattr(r, "transmission_norm", ""),
                "transmission_raw": getattr(r, "transmission_raw", ""),
                "mileage": getattr(r, "mileage", ""),
                "price_usd": getattr(r, "price_usd", ""),
                "exterior_color": getattr(r, "exterior_color", ""),
                "interior_color": getattr(r, "interior_color", ""),
                "color_ext_bucket": getattr(r, "color_ext_bucket", ""),
                "color_int_bucket": getattr(r, "color_int_bucket", ""),
                "raw_options": "; ".join(getattr(r, "raw_options", []) or []),
                "option_codes_present": ";".join(getattr(r, "option_codes_present", []) or []),
                "option_value_usd_total": getattr(r, "option_value_usd_total", 0),
                "top5_options_count": getattr(r, "top5_options_count", 0),
                "top5_options_present": "; ".join(getattr(r, "top5_options_present", []) or []),
                "location": getattr(r, "location", ""),
                "baseline_adj_price_usd": getattr(r, "baseline_adj_price_usd", ""),
                "adj_price_usd": getattr(r, "adj_price_usd", ""),
                "deal_delta_usd": getattr(r, "deal_delta_usd", ""),
            }
        )

        view.append(
            {
                "Deal Î” ($)": (
                    f"+{getattr(r, 'deal_delta_usd')}"
                    if isinstance(getattr(r, "deal_delta_usd", None), (int, float))
                    and getattr(r, "deal_delta_usd") >= 0
                    else (
                        str(getattr(r, "deal_delta_usd"))
                        if getattr(r, "deal_delta_usd", None) is not None
                        else ""
                    )
                ),
                "Price": (
                    f"${text.round_up_1k(getattr(r, 'price_usd'))}"
                    if getattr(r, "price_usd", None)
                    else ""
                ),
                "Miles": (
                    text.round_up_1k(getattr(r, "mileage")) if getattr(r, "mileage", None) else ""
                ),
                "Year/Model/Trim": ymt,
                "Transmission": getattr(r, "transmission_norm", "")
                or getattr(r, "transmission_raw", ""),
                "Colors (Ext / Int)": f"{getattr(r, 'exterior_color', '') or ''} / {getattr(r, 'interior_color', '') or ''}",
                "Top Options": ", ".join(top_labels),
                "Source": getattr(r, "source", ""),
            }
        )

    return csv, view
