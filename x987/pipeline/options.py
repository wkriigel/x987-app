# FILE: x987/pipeline/options.py
import re
from ..utils import log

def _compile_option_patterns(cfg):
    patmap = {}
    op = (cfg.get("option_patterns") or {})
    for canon, arr in op.items():
        pats = []
        for pat in (arr or []):
            try:
                pats.append(re.compile(pat, re.I))
            except re.error:
                # Ignore bad patterns instead of failing the run
                pass
        # Fallback: literal word match on the canonical name if no valid patterns
        if not pats and canon:
            try:
                pats.append(re.compile(r"\b" + re.escape(canon) + r"\b", re.I))
            except re.error:
                pass
        patmap[canon] = pats
    return patmap

def recompute_top5_options(rows, cfg):
    """
    Re-derives `top5_options_present` and `top5_options_count` for each row
    from `raw_options` using regex synonyms defined in config.

    Works in both full and cached runs.
    """
    log.step("options")
    top5_list = (cfg.get("top5_options") or {}).get("list", []) or []
    patmap = _compile_option_patterns(cfg)

    count = 0
    for r in rows:
        # Candidate text: joined raw_options lines (already split by cache/ingest).
        raw_opts = getattr(r, "raw_options", None) or []
        haystack = "\n".join(raw_opts)

        present = []
        for canon in top5_list:
            pats = patmap.get(canon, [])
            if any(p.search(haystack) for p in pats):
                present.append(canon)

        # Sort & de-dup
        present = sorted(set(present))
        setattr(r, "top5_options_present", present)
        setattr(r, "top5_options_count", len(present))
        count += 1

    log.ok(count=count)
    return rows
