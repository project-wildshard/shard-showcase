"""Measure visible weapon contribution in paired native screenshots (Pillow)."""
import json
import math
import sys
from pathlib import Path
from PIL import Image

ROOT = Path(sys.argv[1])
VIEWS = ("stock", "left", "right", "raised", "raised-right")
REPLAY = json.loads((ROOT / "proof.json").read_text())["left"]
FRAMES = REPLAY["shoulder"]
HIT = REPLAY["contact"]["frame"]
assert [frame[0]["frame"] for frame in FRAMES] == [HIT - 2, HIT, HIT + 2]


def changed(x, y):
    return sum(max(abs(a-b) for a,b in zip(px,py)) >= 16 for px,py in zip(x,y))


def inspect(frame, name):
    shown, hidden, restored = (row for row in frame if row["name"] == name)
    assert [r["visible"] for r in (shown, hidden, restored)] == [True, False, True]
    assert shown["camera"] == hidden["camera"] == restored["camera"]
    base, tip = shown["base"], shown["tip"]
    roi = (
        max(0, math.floor(min(base[0], tip[0]) - 22)),
        max(0, math.floor(min(base[1], tip[1]) - 22)),
        min(402, math.ceil(max(base[0], tip[0]) + 22)),
        min(874, math.ceil(max(base[1], tip[1]) + 22)),
    )

    def pixels(row):
        crop = Image.open(ROOT / row["png"]).convert("RGB").crop(roi)
        return list(crop.get_flattened_data() if hasattr(crop, "get_flattened_data") else crop.getdata())

    a,b,c = map(pixels, (shown, hidden, restored))
    contribution, noise = changed(a,b), changed(a,c)
    assert noise <= 5 and contribution > noise + 10, (name, contribution, noise)
    return {
        "weaponChangedPixels": contribution,
        "restorationNoisePixels": noise,
        "spanPx": math.dist(base[:2], tip[:2]),
        "eye": shown["enemyEye"],
        "core": shown["enemyCore"],
        "heroHead": shown["head"],
        "base": base,
        "tip": tip,
        "cameraDeltaMeters": [shown["offset"], shown["lift"]],
        "localLensSweep": shown["sweep"],
        "roiExclusive": roi,
    }


data = {
    "referenceCommit": "3afcd880b397e9703e906a7e66b42e8447e59519",
    "viewport": [402,874],
    "confirmedDamageFrame": HIT,
    "pixelRule": "per-view blade socket rectangle plus 22 px; maximum channel difference >= 16, weapon on/off",
    "frames": [
        {"frame": frame[0]["frame"], "hp": frame[0]["hp"],
         "views": {name: inspect(frame,name) for name in VIEWS}}
        for frame in FRAMES
    ],
}
print(json.dumps(data,indent=2))
