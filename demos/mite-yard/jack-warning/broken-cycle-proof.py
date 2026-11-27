"""Check a frozen-camera Broken countdown comparison at three native phases."""
import argparse
import json
import math
from pathlib import Path
from PIL import Image

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("default", type=Path)
parser.add_argument("zero", type=Path)
args = parser.parse_args()
proof = {
    "reference": "Raynos/showcase-zone-clean-room@3afcd880b397e9703e906a7e66b42e8447e59519",
    "viewportCssPx": [402, 874],
    "treatment": "Scale centered on dark track, head position/size match; dim gold fill only",
    "marker": "Bright-gold R>=235, G>=196 in one local union crop; not visibility or luminance",
    "runs": {},
}
for expected, path in ((1, args.default), (0, args.zero)):
    phases = json.loads((path / "broken-cycle.json").read_text())
    rows = []
    for want, (stock, compact) in zip((.99, .5, .25), phases, strict=True):
        for k in ("frame","sim","time","hp","camera","q","strobe","remaining","trackVertices","goldVertices","center"):
            assert stock[k] == compact[k], k
        assert stock["strobe"] == expected and stock["hp"][0] == 204
        assert want - .03 <= stock["remaining"] <= want
        assert stock["trackVertices"] == 58
        for key in ("radius","headSize"):
            assert math.isclose(compact[key] / stock[key], .58, abs_tol=.00015), key
        assert compact["trackBox"][2]-compact["trackBox"][0] < stock["trackBox"][2]-stock["trackBox"][0]
        ex = stock["trackBox"]
        crop = (max(0, math.floor(ex[0])-12), max(0, math.floor(ex[1])-12),
                min(402, math.ceil(ex[2])+12), min(874, math.ceil(ex[3])+12))
        assert crop[2] > crop[0] and crop[3] > crop[1], crop
        counts = {}
        for name in ("stock","compact"):
            im = Image.open(path / f"cycle-{want:g}-{name}.png").convert("RGB")
            assert im.size == (402,874)
            counts[name] = sum(r >= 235 and g >= 196 for r,g,b in im.crop(crop).getdata())
        rows.append({"remaining":round(stock["remaining"],4), "frame":stock["frame"],"hp":stock["hp"],
          "trackVertices":stock["trackVertices"],"arcVertices":stock["goldVertices"],
          "viewCenterPx":stock["center"], "stockTrackBox":stock["trackBox"],"compactTrackBox":compact["trackBox"],
          "stockHeadPx":stock["headScreen"],"compactHeadPx":compact["headScreen"],
          "headRadiusRatio":round(compact["radius"]/stock["radius"],4),"crop":crop,"brightGold":counts})
    assert all(a["arcVertices"]>b["arcVertices"] for a,b in zip(rows,rows[1:]))
    proof["runs"][str(expected)] = rows
print(json.dumps(proof,indent=2))
