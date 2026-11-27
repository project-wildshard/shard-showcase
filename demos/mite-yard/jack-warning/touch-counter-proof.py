"""Verify trusted Chromium touch used the native HUD and canvas handlers."""
import argparse
import json
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
for case in ("hud-drag", "hud-tap", "hud-cancel", "canvas-drag"):
    parser.add_argument(case.replace("-", "_"), type=Path)
args = parser.parse_args()
def load(case):
    return json.loads((getattr(args, case.replace("-", "_")) / "touch-counter.json").read_text())
drag, tap, cancel, canvas = (load(case) for case in ("hud-drag", "hud-tap", "hud-cancel", "canvas-drag"))
out = {"reference":"Raynos/showcase-zone-clean-room@3afcd880b397e9703e906a7e66b42e8447e59519",
       "viewportCssPx":[402,874], "input":"Chromium CDP touch through native DOM handlers, not device", "cases":{}}
for data in (drag,tap,cancel,canvas):
    rows={x["n"]:x for x in data["snaps"]}
    assert rows[1]["attackHeld"] and rows[1]["captured"] and rows[1]["holdingMove"], rows[1]
    assert not rows[1]["hudSteer"], rows[1]
    assert data["contact"] and data["contact"]["hp"][1]<132, data["control"]
    assert data["events"] and all(e["trusted"] for e in data["events"])
    assert len({e["id"] for e in data["events"] if e["kind"]=="pointerdown"})>=2
    assert not rows[42]["attackHeld"] and not rows[42]["hudSteer"] and not rows[42]["canvasLook"], rows[42]
    out["cases"][data["control"]]={"contactHp":data["contact"]["hp"],"snapshots":[rows[n] for n in (1,19,20,36,37,42)]}
for data,end in ((drag,"pointerup"),(cancel,"pointercancel")):
    rows={x["n"]:x for x in data["snaps"]}
    paused=[l for l in data["lens"] if 21<=l["since"]<=36]
    assert len(paused)==16 and all(l["hudSteer"] and l["override"] and not l["legacyLook"] and l["holdingMove"] for l in paused), paused
    assert any(e["kind"]==end and e["act"]=="attack" for e in data["events"])
    assert rows[19]["captured"] and rows[36]["captured"] and rows[37]["captured"] and not rows[42]["holdingMove"]
    toward=next(l for l in data["lens"] if l["since"]==20)
    reverse=next(l for l in data["lens"] if l["since"]==37)
    assert toward["lookX"]<0<reverse["lookX"] and toward["lookY"]*reverse["lookY"]<0, (toward,reverse)
    out["cases"][data["control"]].update(pausedFrames=len(paused), legacyUnownedFrames=len(paused), releasedBy=end)
assert not any(l["hudSteer"] or l["canvasLook"] for l in tap["lens"])
assert any(l["engaged"] and not l["override"] and l["turn"] for l in tap["lens"])
assert any(e["kind"]=="pointerup" and e["act"]=="attack" for e in tap["events"])
assert all(l["canvasLook"] and not l["hudSteer"] and l["override"] for l in canvas["lens"] if 21<=l["since"]<=36)
print(json.dumps(out,indent=2))
