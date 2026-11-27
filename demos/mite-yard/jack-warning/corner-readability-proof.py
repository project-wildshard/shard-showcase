"""Produce a receipt from one frozen native corner replay (requires Pillow)."""
import json
import math
import sys
from pathlib import Path
from PIL import Image

ROOT = Path(sys.argv[1])
ROI = (171, 424, 394, 531)
MODES = ("stock", "armor", "tight", "stroke", "stock-repeat")
replay = json.loads((ROOT / "proof.json").read_text())["left"]
rows = {r["mode"]: r for r in replay["visuals"]}
assert tuple(rows) == MODES
first = rows["stock"]
for row in rows.values():
    for key in ("frame", "sim", "pose", "actionTime", "camera", "rotation", "lens", "hp", "sampled"):
        assert row[key] == first[key], (row["mode"], key)
def pixels(mode):
    return list(Image.open(ROOT / f"light-{mode}.png").convert("RGB").crop(ROI).getdata())

base = pixels("stock")
def stats(mode):
    a = pixels(mode)
    return {
        "nearWhite": sum(min(r, g, b) >= 220 for r, g, b in a),
        "warmBright": sum(r >= 230 and g >= 185 and r-b >= 16 for r, g, b in a),
        "paleBright": sum(r >= 230 and g >= 205 and b >= 168 for r, g, b in a),
        "changedBy12": sum(max(abs(a-b) for a, b in zip(x, y)) >= 12 for x, y in zip(a, base)),
    }

crop_stats = {mode: stats(mode) for mode in MODES}
assert crop_stats["stock-repeat"]["changedBy12"] <= 5, crop_stats
assert rows["armor"]["crescent"] == first["crescent"]
assert rows["tight"]["centralFlash"] == first["centralFlash"]
assert rows["tight"]["trailPeak"] == first["trailPeak"]
assert rows["stroke"]["trailVertices"] == first["trailVertices"] > 0
assert rows["stroke"]["trailPeak"] < first["trailPeak"]
assert crop_stats["stroke"]["paleBright"] < crop_stats["stock"]["paleBright"]

f = first["frame"]
window = [r for r in replay["blade"] if f-3 <= r["frame"] <= f+2]
assert [r["frame"] for r in window] == list(range(f-3, f+3))
hit = next(r for r in window if r["frame"] == f)
pre = next(r for r in window if r["frame"] == f-1)
origin = replay["impact"]["world"]
d = [t-b for t, b in zip(pre["tip"], pre["base"])]
t = max(0, min(1, sum((o-b)*v for o,b,v in zip(origin, pre["base"], d)) / sum(v*v for v in d)))
prior_distance = math.dist(origin, [b+t*v for b,v in zip(pre["base"], d)])
data = {
    "referenceCommit": "3afcd880b397e9703e906a7e66b42e8447e59519",
    "viewport": [402,874],
    "roiExclusive": ROI,
    "thresholds": {"nearWhite": "min(R,G,B) >= 220",
                   "warmBright": "R >= 230 and G >= 185 and R-B >= 16",
                   "paleBright": "R >= 230 and G >= 205 and B >= 168"},
    "sameFrame": f, "pose": first["pose"], "hp": first["hp"],
    "cropStats": crop_stats,
    "effectSettings": {m: {k: row[k] for k in ("bodyFlash","crescent","centralFlash","trailVertices","trailPeak")} for m,row in rows.items()},
    "bladeTipTravelM": hit["tipDelta"],
    "bladeSpanPx": math.dist(hit["basePx"][:2], hit["tipPx"][:2]),
    "priorBladeToNativeFxOriginM": prior_distance,
    "hitBladeToNativeFxOriginM": hit["fxOriginDistance"],
    "bladeSamples": window,
}
print(json.dumps(data, indent=2))
