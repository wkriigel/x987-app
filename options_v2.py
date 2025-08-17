# FILE: x987/pipeline/options_v2.py
import re
from types import SimpleNamespace
from ..utils import log

def _norm(s): 
    return (s or "").strip()

def _is_cayman_r(row):
    model = _norm(getattr(row, "model", ""))
    trim  = _norm(getattr(row, "trim", ""))
    ymt   = f"{model} {trim}".strip().lower()
    return "cayman r" in ymt or (model.lower() == "cayman" and trim.lower() == "r")

def _compile_catalog(cfg):
    v2 = (cfg.get("options_v2") or {})
    catalog_cfg = v2.get("catalog") or []
    compiled = []
    for item in catalog_cfg:
        cid = item.get("id") or ""
        display = item.get("display") or cid
        value = int(item.get("value_usd") or 0)
        codes_alias = list(item.get("codes_alias") or [])
        standard_on = [str(x) for x in (item.get("standard_on") or [])]
        syns = item.get("synonyms") or []
        pats = []
        for pat in syns:
            try:
                pats.append(re.compile(pat, re.I))
            except re.error:
                # ignore malformed pattern
                pass
        compiled.append(SimpleNamespace(
            id=cid, display=display, value=value, codes_alias=codes_alias,
            standard_on=standard_on, patterns=pats,
            # hide PDK from Top Options column; we still store its code
            show_in_view=(cid != "250")
        ))
    # deterministic order: by value desc, then display asc
    compiled.sort(key=lambda x: (-x.value, x.display.lower()))
    return compiled

def recompute_options_v2(rows, cfg):
    """
    Populate per-row:
      - option_codes_present: list[str] of codes/ids detected (includes aliases)
      - option_labels_display: list[str] compact labels, ordered by value desc
      - option_value_usd_total: int sum of values (excludes items standard_on trim)
      - top5_options_present: legacy compatible (same as labels)
      - top5_options_count: legacy compatible (len(labels))
    """
    if not (cfg.get("options_v2") or {}).get("enabled", False):
        return rows

    log.step("options")
    catalog = _compile_catalog(cfg)
    count = 0

    for r in rows:
        # Build haystack from curated raw_options; fall back to minimal composite
        raw_opts = getattr(r, "raw_options", []) or []
        haystack = "\n".join(_norm(x) for x in raw_opts)

        is_r = _is_cayman_r(r)
        codes, labels = [], []
        total_value = 0

        for ent in catalog:
            # suppress if standard on this trim (e.g., Cayman R → LSD/19" wheels not counted)
            if is_r and any("cayman r" == s.lower() for s in ent.standard_on):
                present = False
            else:
                present = any(p.search(haystack) for p in ent.patterns)

            # special: 987.2 automatics are PDK → store code 250 even if not text-matched
            if ent.id == "250":
                trans = _norm(getattr(r, "transmission_norm", "")) or _norm(getattr(r, "transmission_raw", ""))
                year  = getattr(r, "year", None)
                if year and 2009 <= int(year) <= 2012 and trans.lower() == "automatic":
                    present = True

            if present:
                codes.append(ent.id)
                codes.extend(ent.codes_alias)
                if not (is_r and any("cayman r" == s.lower() for s in ent.standard_on)):
                    total_value += ent.value
                if ent.show_in_view and ent.display not in labels:
                    labels.append(ent.display)

        setattr(r, "option_codes_present", codes)
        setattr(r, "option_labels_display", labels)
        setattr(r, "option_value_usd_total", total_value)

        # legacy compatibility for existing views/pipelines
        setattr(r, "top5_options_present", labels)
        setattr(r, "top5_options_count", len(labels))

        count += 1

    log.ok(count=count)
    return rows
