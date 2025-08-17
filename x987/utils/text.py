import re
import math

MONO = {"black", "white", "gray", "grey", "silver"}


def parse_int(s):
    if s is None:
        return None
    m = re.findall(r"\d[\d,]*", str(s))
    return int(m[0].replace(",", "")) if m else None


def round_up_1k(n):
    if n is None:
        return ""
    return f"{int(math.ceil(n / 1000.0)) * 1_000 // 1000}k".replace("1000k", "1,000k")


def is_color(name):
    if not name:
        return False
    n = str(name).lower()
    return not any(x in n for x in MONO)


def mileage_band(m):
    if m is None:
        return "unknown"
    if m <= 39999:
        return "0-39999"
    if m <= 59999:
        return "40000-59999"
    if m <= 79999:
        return "60000-79999"
    if m <= 99999:
        return "80000-99999"
    return "100000+"
