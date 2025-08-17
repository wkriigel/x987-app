# FILE: x987/pipeline/options.py
"""
Forward legacy API to v2 implementation.
"""
from .options_v2 import recompute_options_v2

def recompute_top5_options(rows, cfg):
    """Legacy name kept for backward compatibility; delegates to v2."""
    return recompute_options_v2(rows, cfg)
