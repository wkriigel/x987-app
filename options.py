# FILE: x987/pipeline/options.py
"""
V2 is the default. This module forwards legacy calls to the v2 implementation
so existing imports keep working.
"""
from .options_v2 import recompute_options_v2 as recompute_top5_options
