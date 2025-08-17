# tools/extract_swatches.py
# Extract average HEX from a grid of swatches in an image.
# Produces a JSON you can drop at x987-data/paint/porsche_swatches.json
import json, math, argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def average_hex(im, bbox, trim=4):
    x0,y0,x1,y1 = bbox
    x0+=trim; y0+=trim; x1-=trim; y1-=trim
    region = im.crop((x0,y0,x1,y1)).convert("RGB")
    # ignore highlights: median of pixels
    px = list(region.getdata())
    r = sorted(p[0] for p in px)[len(px)//2]
    g = sorted(p[1] for p in px)[len(px)//2]
    b = sorted(p[2] for p in px)[len(px)//2]
    return f"#{r:02X}{g:02X}{b:02X}"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True)
    ap.add_argument("--rows", type=int, required=True)
    ap.add_argument("--cols", type=int, required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    im = Image.open(args.image).convert("RGB")
    W,H = im.size
    pad = 10  # outer padding approximation
    gw = (W - 2*pad) / args.cols
    gh = (H - 2*pad) / args.rows

    swatches = []
    for r in range(args.rows):
        for c in range(args.cols):
            x0 = int(pad + c*gw)
            y0 = int(pad + r*gh)
            x1 = int(pad + (c+1)*gw)
            y1 = int(pad + (r+1)*gh)
            hexv = average_hex(im, (x0,y0,x1,y1), trim=8)
            swatches.append({"index": r*args.cols + c, "hex": hexv})

    # Write JSON (you can add names later)
    outp = Path(args.out)
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(json.dumps(swatches, indent=2), encoding="utf-8")

    # Preview with indices
    draw = ImageDraw.Draw(im)
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None
    for s in swatches:
        i = s["index"]; c = i % args.cols; r = i // args.cols
        x0 = int(pad + c*gw); y0 = int(pad + r*gh)
        x1 = int(pad + (c+1)*gw); y1 = int(pad + (r+1)*gh)
        draw.rectangle((x0,y0,x1,y1), outline=(255,255,255), width=1)
        draw.text((x0+6,y0+6), str(i), fill=(255,255,255), font=font)
    im.save(outp.with_suffix(".preview.png"))
    print(f"Saved {outp} and {outp.with_suffix('.preview.png')}")

if __name__ == "__main__":
    main()

