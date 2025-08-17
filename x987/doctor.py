import importlib, pathlib
from .settings import get_paths
def run_doctor(cfg):
    problems=[]
    for pkg in ["playwright","rich","pydantic","rapidfuzz","tomli"]:
        if importlib.util.find_spec(pkg) is None: problems.append(f"Missing package: {pkg}")
    paths=get_paths()
    for k in ["RAW_DIR","NORM_DIR","META_DIR","USER_RULES","USER_INPUT_MANUAL"]:
        pathlib.Path(paths[k]).mkdir(parents=True,exist_ok=True)
    if not cfg.get("search_urls"): problems.append("config.search_urls is empty.")
    if problems:
        print("❌ DOCTOR FAIL:"); [print(" -",p) for p in problems]; raise SystemExit(1)
    print("✅ Doctor OK")
