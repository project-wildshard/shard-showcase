"""Summarize one exactly matched native frame without writing reference images."""
import json,sys
from pathlib import Path
from PIL import Image
p=Path(sys.argv[1])
bounds=(0,267,176,693)
with (p/'frozen-receipt.json').open() as f: cases=json.load(f)
assert len(cases)==8
same=('frame','gameTime','simTime','hp','yaw','camera')
base=cases[0]
assert all(all(c[k]==base[k] for k in same) for c in cases)
assert cases[5]['ribbonSelected'] and cases[6]['ribbonSelected']
rows=[]
for c in cases:
    m=c['mode']
    raw=Image.open(p/f'frozen-{m}.png').convert('RGB')
    assert raw.size==(402,874)
    patch=raw.crop(bounds)
    rgb=getattr(patch,'get_flattened_data',patch.getdata)()
    rows.append(dict(mode=m,bright=sum(r>=235 and g>=196 for r,g,b in rgb),
        nearWhite=sum(min(r,g,b)>=220 for r,g,b in rgb),
        tagCounts=dict(zip(c['labels'],c['counts'])),ribbonRow=c['ribbonRow'],ribbonVertices=c['ribbonSelected']))
assert rows[-1]['bright']<.7*rows[0]['bright']
out=dict(reference='3afcd880b397e9703e906a7e66b42e8447e59519',viewport=[402,874],
    scope='Same frozen original Fable gameplay frame, local renderer controls only. Matched camera, state and HP. All variants use body mix capped to .22; world point lights, spark heads, state timers, FX/exposure and simulation unchanged. Not a screen-luminance or phone test.',
    hp=base['hp'],roi=list(bounds),bright='R at least 235 and G at least 196 in the fixed ROI',nearWhite='R, G and B at least 220 in the fixed ROI',
    compact={'worldScale':.58,'goldAlphaScale':.65,'darkTrackRetained':True}, cases=rows)
print(json.dumps(out,indent=2))
