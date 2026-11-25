"""Check the matched portrait renders without pretending this is GPU playtest."""
from pathlib import Path
import json
import sys
from PIL import Image

folder=Path(sys.argv[1])
a,b=[Image.open(folder/f"{name}.png").convert("RGB") for name in ("phone","phone-off")]
assert a.size==b.size==(402,874)
points=[]
outside=0
for y in range(a.height):
    for x in range(a.width):
        r,g,bl=a.getpixel((x,y))
        r0,g0,b0=b.getpixel((x,y))
        if g-r>=32 and bl-r>=32 and g>=128 and (g-g0)+(bl-b0)>=95:
            if 145<x<258 and 408<y<476:
                points.append((x,y))
            else:
                outside+=1
assert len(points)>=105,(len(points),outside)
assert outside<=8,(len(points),outside)
x,y=zip(*points)
report={"matched_dimensions":list(a.size),"changed_cyan_pixels":len(points),
        "cue_bbox_xyxy":[min(x),min(y),max(x),max(y)],
        "outside_cue_changed_pixels":outside}
assert max(x)-min(x)>=44 and max(y)-min(y)>=13,report
(folder/"render-check.json").write_text(json.dumps(report,indent=2)+"\n")
print(report)
