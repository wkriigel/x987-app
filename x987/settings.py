# FILE: x987/settings.py
# CONTRACT: load human-friendly TOML config from persistent path; create default if missing

import os
import pathlib

APP = "x987"

# Default config written to %APPDATA%\x987\config.toml on first run
DEFAULT_CFG = r"""# Config lives in %APPDATA%/x987/config.toml (auto-created on first run)
debug = true
concurrency = 2
polite_delay_ms = 900
cap_listings = 150
search_urls = [
  "https://www.autotempest.com/results?localization=country&make=porsche&maxyear=2012&minyear=2009&model=cayman&transmission=auto&zip=30214"
]
min_year = 2009
max_year = 2012
[fair_value]
s_premium_usd=6000
per_option_usd=500
exterior_color_usd=1000
interior_color_usd=0
per_year_usd=500
[special_trim_premiums]
"Cayman R"=30000
"Boxster Spyder"=30000
[top5_options]
list=["Sport Chrono","PASM","PSE","LSD","Sport Seats"]
[baseline]
group_keys=["model","transmission"]
stat="median"
band_1_max=39999
band_2_max=59999
band_3_max=79999
band_4_max=99999
[scrapers]
cars_com=true
carvana_com=false
"""


def user_dir() -> pathlib.Path:
    appdata = os.getenv("APPDATA")
    base = pathlib.Path(appdata) / APP if appdata else pathlib.Path.home() / ("." + APP)
    base.mkdir(parents=True, exist_ok=True)
    return base


def get_paths():
    code = pathlib.Path(__file__).resolve().parents[1]
    data = code.parent / "x987-data"
    data.mkdir(parents=True, exist_ok=True)
    usr = user_dir()
    return {
        "CODE_ROOT": code,
        "DATA_ROOT": data,
        "USER_ROOT": usr,
        "USER_CONFIG": usr / "config.toml",
        "USER_RULES": usr / "rules",
        "USER_INPUT_MANUAL": usr / "input" / "manual",
        "RAW_DIR": data / "raw",
        "NORM_DIR": data / "normalized",
        "META_DIR": data / "meta",
    }


def _read_toml(fp: pathlib.Path):
    try:
        import tomllib  # Py 3.11+

        with open(fp, "rb") as f:
            return tomllib.load(f)
    except Exception:
        import tomli

        with open(fp, "rb") as f:
            return tomli.load(f)


def load_config():
    p = get_paths()
    for k in ["RAW_DIR", "NORM_DIR", "META_DIR", "USER_RULES", "USER_INPUT_MANUAL"]:
        p[k].mkdir(parents=True, exist_ok=True)
    cfgp = p["USER_CONFIG"]
    if not cfgp.exists():
        cfgp.write_text(DEFAULT_CFG, encoding="utf-8")
        print(f"[x987] Created default config at {cfgp}")
    cfg = _read_toml(cfgp)
    # helpful: include resolved paths in runtime cfg for reference
    cfg["_paths"] = {k: str(v) for k, v in p.items()}
    return cfg


