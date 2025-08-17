# x987/view/report.py
from rich.table import Table
from rich.console import Console
from rich.text import Text
from rich import box
import re, os, math, json
from pathlib import Path
from typing import Any, Iterable, Optional

# =========================
# THEME
# =========================
THEME = {
    "bg":            "#0B0F14",
    "surface":       "#121820",
    "surface_alt":   "#0E141B",

    "text":          "#C9D1D9",
    "text_muted":    "#8A97A6",
    "text_dim":      "#55616E",

    "gray_900": "#1A222C",
    "gray_800": "#252F3A",
    "gray_700": "#3A4654",
    "gray_600": "#4D5967",
    "gray_500": "#6B7785",
    "gray_400": "#8794A2",
    "gray_300": "#A5AFBA",
    "gray_200": "#C2CBD6",
    "gray_100": "#DEE4EC",

    # Teal ramp (cheap = bright)
    "teal_1": "#5FFBF1",
    "teal_2": "#37E9DF",
    "teal_3": "#19E1D6",
    "teal_4": "#3FB8B0",
    "teal_5": "#5E8F91",
    "teal_6": "#6F7F82",

    # Oranges
    "orange_cayman_s":  "#FF6A1A",
    "orange_cayman":    "#FFC04D",
    "orange_boxster_s": "#FFD137",
    "orange_boxster":   "#FFE394",
    "orange_special_1": "#FF3B1A",
    "orange_special_2": "#E62500",

    # Warm dim ramp (manual de-emphasis)
    "warm_dim_1": "#6E5A4E",
    "warm_dim_2": "#665247",
    "warm_dim_3": "#5D4B41",
    "warm_dim_4": "#54443B",
    "warm_dim_5": "#4B3C35",
    "warm_dim_6": "#43362F",

    # Row stripe (subtle; only used on every 2nd row)
    "stripe_1": "#11151B",
}

NEAREST_ANSI = [
    ("black","#000000"),("dark_gray","#808080"),("bright_black","#555555"),
    ("white","#C0C0C0"),("bright_white","#E6EDF3"),("red","#CC0000"),
    ("bright_red","#FF6A00"),("green","#00A86B"),("bright_green","#24D67A"),
    ("yellow","#FFC300"),("bright_yellow","#FFD966"),("blue","#3A8EDB"),
    ("bright_blue","#66A8EA"),("purple","#A888FF"),("bright_purple","#C9A8FF"),
    ("cyan","#00CFC7"),("bright_cyan","#19E1D6"),
]
_num_re = re.compile(r"[-+]?\d[\d,]*\.?\d*")

def _hex_to_rgb(h: str) -> tuple[int,int,int]:
    h=h.lstrip("#"); return int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)

def _nearest_ansi_name(hex_color: str) -> str:
    r,g,b=_hex_to_rgb(hex_color); best,bd="white",10**9
    for name,hx in NEAREST_ANSI:
        r2,g2,b2=_hex_to_rgb(hx); d=(r-r2)**2+(g-g2)**2+(b-b2)**2
        if d<bd: bd,best=d,name
    return best

def theme_style(color_key_or_hex: Optional[str], *, bold: bool=False, dim: bool=False, bg: Optional[str]=None) -> str:
    """Foreground + optional background style."""
    console = Console()
    def resolve(c: Optional[str]) -> Optional[str]:
        if not c: return None
        return THEME.get(c, c)
    fg_hex = resolve(color_key_or_hex) or THEME["text"]
    bg_hex = resolve(bg)
    if console.color_system in ("truecolor","256"):
        parts=[]
        if bold: parts.append("bold")
        if dim:  parts.append("dim")
        parts.append(fg_hex)
        if bg_hex: parts.append(f"on {bg_hex}")
        return " ".join(parts)
    parts=[]
    if bold: parts.append("bold")
    if dim:  parts.append("dim")
    parts.append(_nearest_ansi_name(fg_hex))
    if bg_hex: parts.append(f"on {_nearest_ansi_name(bg_hex)}")
    return " ".join(parts)

def bg_style(bg_key_or_hex: str) -> str:
    """Background-only style (no foreground)."""
    console = Console()
    hx = THEME.get(bg_key_or_hex, bg_key_or_hex)
    if console.color_system in ("truecolor","256"):
        return f"on {hx}"
    return f"on {_nearest_ansi_name(hx)}"

# =========================
# Toggles & widths
# =========================
BG_PRICE = os.environ.get("X987_BG_PRICE","1") in ("1","true","TRUE","yes","YES")
BG_MILES = os.environ.get("X987_BG_MILES","1") in ("1","true","TRUE","yes","YES")

K_COL_WIDTH = 5   # fits $999k / 999k
PRICE_W = K_COL_WIDTH
MILES_W = K_COL_WIDTH

COLOR_SWATCH_W = 10  # 5 ext + 5 int
SWATCH_HALF = 5

# =========================
# Paint DB + interior guess
# =========================
BUILTIN_PAINTS = {
    "arctic silver metallic":"#C9CCCE",
    "classic silver metallic":"#C6C9CB",
    "meteor gray":"#6E7479",
    "gray":"#8F969C",
    "black":"#0C0E10",
    "white":"#E9EAEA",
    "guards red":"#D0191A",
    "red":"#B0201B",
    "carrara white":"#EDEDED",
    "aqua blue metallic":"#2E6C8E",
    "malachite green metallic":"#2C5F51",
    "silver":"#C9CCCE",
    "midnight blue metallic":"#1A2C4E",
    "basalt black metallic":"#0B0F14",
}
PAINT_DB_PATHS = [Path("x987-data/paint/porsche_swatches.json"), Path("porsche_swatches.json")]

def load_paint_db()->dict[str,str]:
    for p in PAINT_DB_PATHS:
        if p.exists():
            try:
                data=json.loads(p.read_text(encoding="utf-8"))
                if isinstance(data,list):
                    return {d["name"].strip().lower(): d["hex"] for d in data if "name" in d and "hex" in d}
                elif isinstance(data,dict):
                    return {k.strip().lower(): v for k,v in data.items()}
            except Exception:
                pass
    return {}
PAINT_DB = load_paint_db()

def norm(s: str) -> str: return re.sub(r"[^a-z0-9]+"," ", s.lower()).strip()

def get_paint_hex(ext_name: str) -> Optional[str]:
    if not ext_name: return None
    key=norm(ext_name)
    if key in PAINT_DB: return PAINT_DB[key]
    if key in BUILTIN_PAINTS: return BUILTIN_PAINTS[key]
    try:
        from rapidfuzz import process, fuzz
        choices=list({*PAINT_DB.keys(), *BUILTIN_PAINTS.keys()})
        if choices:
            cand,score,_=process.extractOne(key,choices,scorer=fuzz.WRatio)
            if score>=85: return (PAINT_DB.get(cand) or BUILTIN_PAINTS.get(cand))
    except Exception:
        pass
    return None

INTERIOR_GUESS = [
    (r"black|anthracite|graphite|charcoal", "#0E1114"),
    (r"sand\s*beige|beige",                  "#CBB68B"),
    (r"tan|camel|savanna",                   "#B48A60"),
    (r"cocoa|espresso|chocolate|brown",      "#6B4A2B"),
    (r"stone|platinum\s*gray|platinum\s*grey|gray|grey", "#A7ADB5"),
    (r"red|carmine|bordeaux",                "#7E1C1C"),
    (r"blue|navy",                            "#2F3A56"),
    (r"white|ivory|alabaster",                "#E8E8E8"),
]
def guess_interior_hex(int_name: str) -> str:
    s=norm(int_name or "")
    for pat,hx in INTERIOR_GUESS:
        if re.search(pat,s): return hx
    return "#777777"

# =========================
# Helpers
# =========================
def parse_price_to_int(v: Any)->Optional[int]:
    if v is None: return None
    if isinstance(v,(int,float)): return int(round(float(v)))
    s=str(v).strip().lower()
    if not s: return None
    if s.endswith("k"):
        m=_num_re.search(s)
        if not m: return None
        try: return int(float(m.group().replace(",",""))*1000)
        except: return None
    m=_num_re.search(s)
    if not m: return None
    try: return int(float(m.group().replace(",","")))
    except: return None

def parse_int_with_commas(v: Any)->Optional[int]:
    if v is None: return None
    if isinstance(v,(int,float)): return int(round(float(v)))
    m=_num_re.search(str(v))
    if not m: return None
    try: return int(float(m.group().replace(",","")))
    except: return None

def pick(row: dict, *candidates: str, default: Any="")->Any:
    lower={k.lower():k for k in row.keys()}
    for cand in candidates:
        k=lower.get(cand.lower())
        if k is not None: return row[k]
    return default

# =========================
# Price & Miles
# =========================
def price_style_key(price_int: Optional[int])->str:
    if price_int is None: return "text_muted"
    if price_int < 20_000:  return "teal_1"
    if price_int < 25_000:  return "teal_2"
    if price_int < 30_000:  return "teal_3"
    if price_int < 35_000:  return "teal_4"
    if price_int < 40_000:  return "teal_5"
    return "teal_6"

def render_price_cell(price_value: Any, *, is_manual: bool=False)->Text:
    price_int=parse_price_to_int(price_value)
    if price_int is None:
        disp=(str(price_value).strip() if isinstance(price_value,str) else "").rjust(PRICE_W); key="text_muted"
    else:
        k=math.ceil(price_int/1000.0); disp=f"${k}k".rjust(PRICE_W); key=price_style_key(price_int)
    bold = key in ("teal_1","teal_2")
    bg_key="gray_700" if (BG_PRICE and bold) else None
    return Text(disp, style=theme_style(key, bold=bold, dim=(is_manual or key=="teal_6"), bg=bg_key))

_miles_k_pat = re.compile(r"(\d+(?:\.\d+)?)\s*[kK]\b")
def miles_to_k_and_val(src: Any)->tuple[Optional[int],Optional[int]]:
    if src is None: return None,None
    if isinstance(src,str):
        s=src.strip().lower(); m=_miles_k_pat.search(s)
        if m: k=math.ceil(float(m.group(1))); return k, k*1000
    n=parse_int_with_commas(src)
    if n is None: return None,None
    if n<1000: k=int(n); return k, k*1000
    else: k=math.ceil(n/1000.0); return k, n

def miles_style_key(miles_val: Optional[int])->str:
    if miles_val is None: return "text_muted"
    if miles_val < 30_000:  return "teal_1"
    if miles_val < 45_000:  return "teal_2"
    if miles_val < 60_000:  return "teal_3"
    if miles_val < 80_000:  return "teal_4"
    if miles_val < 100_000: return "teal_5"
    return "teal_6"

def render_miles_cell(miles_value: Any, *, is_manual: bool=False)->Text:
    k,miles_val=miles_to_k_and_val(miles_value)
    if k is None:
        disp=("".rjust(MILES_W) if miles_value is None else str(miles_value).rjust(MILES_W)); key="text_muted"
    else:
        disp=f"{k}k".rjust(MILES_W); key=miles_style_key(miles_val)
    bold = key in ("teal_1","teal_2")
    bg_key="gray_700" if (BG_MILES and bold) else None
    return Text(disp, style=theme_style(key, bold=bold, dim=(is_manual or key=="teal_6"), bg=bg_key))

# =========================
# Model + Transmission utils (Tx not displayed; still used for logic)
# =========================
def _model_category(model_text: str) -> str:
    s=model_text.lower()
    if "spyder" in s or re.search(r"\b(cayman|boxster)\s+r\b", s): return "special"
    if "cayman"  in s: return "cayman_s" if re.search(r"\bcayman\s+s\b", s) or re.search(r"\bs\b", s) else "cayman"
    if "boxster" in s: return "boxster_s" if re.search(r"\bboxster\s+s\b", s) or re.search(r"\bs\b", s) else "boxster"
    return "other"

_gear_pat = re.compile(r"(\d)\s*[- ]*(?:speed|spd)\b", re.I)
def abbreviate_transmission(tx: str) -> str:
    s=(tx or "").strip().lower()
    g=None
    m=_gear_pat.search(s)
    if m: g=m.group(1)
    elif re.search(r"\b(\d)\b", s): g=re.search(r"\b(\d)\b", s).group(1)
    if "manual" in s or re.search(r"\bm/t\b", s): return f"M{g}" if g else "M"
    if "pdk" in s or "dual clutch" in s or "doppelkupplung" in s: return "PDK"
    if "tiptronic" in s: return "T"
    if "dct" in s: return "DCT"
    if "cvt" in s: return "CVT"
    if "auto" in s or "at" in s or "automatic" in s: return f"A{g}" if g else "A"
    return (tx or "").strip().split()[0][:4].upper() or "â€”"

def render_model_cell(model_text: str, tx_text: str) -> Text:
    cat=_model_category(model_text)
    abbr=abbreviate_transmission(tx_text)
    is_manual=abbr.startswith("M")
    if not is_manual:
        key_map={
            "cayman_s":"orange_cayman_s","cayman":"orange_cayman",
            "boxster_s":"orange_boxster_s","boxster":"orange_boxster",
            "special":"orange_special_1","other":"orange_special_2",
        }
        key=key_map.get(cat,"orange_special_2")
        return Text(model_text, style=theme_style(key, bold=(cat in {"cayman_s","boxster_s","special"})))
    dim_map={
        "cayman_s":"warm_dim_1","cayman":"warm_dim_2",
        "boxster_s":"warm_dim_3","boxster":"warm_dim_4",
        "special":"warm_dim_5","other":"warm_dim_6",
    }
    return Text(model_text, style=theme_style(dim_map.get(cat,"warm_dim_6"), dim=True))

# Deal (manual rows use manual dim color)
def render_deal_cell(deal_value: Any, *, is_manual: bool=False) -> Text:
    val=parse_int_with_commas(deal_value)
    s=f"{val:+,}" if val is not None else str(deal_value)
    return Text(s, style=theme_style("text_dim", dim=True) if is_manual else theme_style("text_muted"))

# =========================
# Colors (Ext/Int) â€” two 5-char blocks
# =========================
def render_color_swatches_cell(value: str) -> Text:
    s=(value or "").strip()
    ext,intn="",""
    if "/" in s: ext,intn=[p.strip() for p in s.split("/",1)]
    elif s: ext=s
    ext_hex=get_paint_hex(ext) or "#6E7479"
    int_hex=guess_interior_hex(intn) if intn else "#777777"
    t=Text()
    t.append(" "*SWATCH_HALF, style=theme_style(None, bg=ext_hex))
    t.append(" "*SWATCH_HALF, style=theme_style(None, bg=int_hex))
    return t

# =========================
# Options â€” smart capitalization; manual rows prepend "Manual"
# =========================
_CAP_FIXES=[(r"\bPcm/Nav\b","PCM/Nav"),(r"\bPcm\b","PCM"),(r"\bPdk\b","PDK"),
            (r"\bLsd\b","LSD"),(r"\bBose\b","BOSE"),(r"\bPccb\b","PCCB"),(r"\bPasm\b","PASM")]
def _cap_phrase(s: str) -> str:
    t=re.sub(r"\s+"," ",s.strip()).title()
    for pat,rep in _CAP_FIXES: t=re.sub(pat,rep,t,flags=re.I)
    return t

def render_options_cell(options: str, *, is_manual: bool=False) -> Text:
    parts=[p.strip() for p in re.split(r"\s*,\s*", options or "") if p.strip()]
    if is_manual:
        parts = ["Manual"] + parts
    out=", ".join(_cap_phrase(p) for p in parts)
    if is_manual:
        return Text(out, style=theme_style("text_dim", dim=True))
    return Text(out)

# =========================
# Table
# =========================
def print_table(rows: Iterable[dict]) -> None:
    console=Console()
    mode=os.environ.get("X987_VIEW_MODE","COMPACT").upper()
    is_wide=mode in ("AUTO","WIDE")

    table=Table(
        show_header=True,
        header_style=theme_style("orange_cayman", bold=True),
        expand=is_wide,
        pad_edge=False,
        show_lines=False,            # no row lines
        show_edge=False,             # no outer frame
        box=box.SIMPLE,              # inner borders on
        border_style="black",        # black inner borders (hairline)
        padding=(0, 1),              # tiny horizontal padding
        row_styles=["", bg_style("stripe_1")],  # first row unstriped, then subtle stripe
    )

    # Columns (Tx removed)
    table.add_column("Deal",  justify="right",  no_wrap=True, min_width=9,       max_width=9)
    table.add_column("Price", justify="right",  no_wrap=True, min_width=PRICE_W, max_width=PRICE_W)
    table.add_column("Miles", justify="right",  no_wrap=True, min_width=MILES_W, max_width=MILES_W)
    table.add_column("Year/Model/Trim",         no_wrap=True, min_width=20,      max_width=24)
    table.add_column("Colors", no_wrap=True, min_width=COLOR_SWATCH_W, max_width=COLOR_SWATCH_W)
    # No Tx column
    table.add_column("Top Options", no_wrap=False, overflow="fold", min_width=28)
    table.add_column("Source", no_wrap=True, min_width=8, max_width=10)

    for r in rows:
        deal_raw=pick(r,"Deal Î” ($)","Deal","deal_delta", default="")
        price_raw=pick(r,"Price","price")
        miles_raw=pick(r,"Miles","miles")
        model=pick(r,"Year/Model/Trim","model","title", default="")
        transmission=pick(r,"Transmission","gearbox", default="")
        colors=pick(r,"Colors (Ext / Int)","colors","color", default="")
        options=pick(r,"Top Options","options", default="")
        source=pick(r,"Source","site", default="")

        abbr=abbreviate_transmission(str(transmission))
        is_manual=abbr.startswith("M")

        table.add_row(
            render_deal_cell(deal_raw, is_manual=is_manual),
            render_price_cell(price_raw, is_manual=is_manual),
            render_miles_cell(miles_raw, is_manual=is_manual),
            render_model_cell(str(model), str(transmission)),
            render_color_swatches_cell(str(colors)),
            render_options_cell(str(options), is_manual=is_manual),
            str(source),
        )

    console.print(table)

# --- smoke test
if __name__=="__main__":
    demo=[
        {"Deal":"+7,159","Price":"$24,900","Miles":34123,"Year/Model/Trim":"2010 Boxster S",
         "Transmission":"Automatic 7-speed (PDK)","Colors (Ext / Int)":"Arctic Silver Metallic / Black",
         "Top Options":"heated seats, pcm/nav, bose","Source":"cars.com"},
        {"Deal":"-1,498","Price":"$43k","Miles":"44k","Year/Model/Trim":"2011 Cayman S",
         "Transmission":"6-speed Manual","Colors (Ext / Int)":"Malachite Green Metallic / Sand Beige",
         "Top Options":"lsd, sport seats, bi-xenon","Source":"cars.com"},
    ]
    print_table(demo)

