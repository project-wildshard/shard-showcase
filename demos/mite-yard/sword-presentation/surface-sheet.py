"""Comparison of static geometry measurements, not a game screenshot."""
import json, sys
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
p=json.loads(Path(sys.argv[1]).read_text())
im=Image.new('RGB',(1240,760),'#101b24');d=ImageDraw.Draw(im)
base=Path('/usr/share/fonts/truetype/dejavu'); white='#edf6fb';muted='#a7b8c4';cyan='#7ce3dd';gold='#f7b568'
def t(x,y,s,k=18,c=white,b=False):
    f=ImageFont.truetype(str(base/('DejaVuSans-Bold.ttf' if b else 'DejaVuSans.ttf')),k)
    d.text((x,y),s,font=f,fill=c)
t(29,22,'WILDSHARD   /   COMBAT LAB',16,cyan,True)
t(29,51,'A registered hit isn’t always a blade touch',37,white,True)
t(31,107,'Rig replay against Pallet Jack’s rest mesh · one centered 60 Hz sweep',21,muted)
x0,y0=129,535; sx=400;sy=160
def xy(x,y):return x0+(x-.5)*sx,y0-y*sy
d.rounded_rectangle((28,164,1210,600),radius=14,fill='#15242f',outline='#3e5563',width=2)
for y in (0,.5,1,1.5,2):
    a,b=xy(.5,y),xy(2.7,y)
    d.line((a,b),fill='#344955',width=1)
    t(62,a[1]-12,str(y),16,muted)
t(60,175,'BLADE–ARMOR GAP (m)',15,muted,True)
a,b=xy(.5,.06),xy(2.7,.06)
d.line((a,b),fill='#64817f',width=2)
t(1017,b[1]-10,'6 cm cue gate',15,muted)
cases=[r for r in p['cases'] if r['hz']==60 and r['wind']==1 and r['sideOffset']==0]
for move,c in [('sword3',cyan),('swordRise',gold)]:
    rows=[r for r in cases if r['move']==move]
    pts=[xy(r['capsuleGap'],r['sweepGapM']) for r in rows]
    d.line(pts,fill=c,width=5)
    for pos in pts:
        x,y=pos
        d.ellipse((x-6,y-6,x+6,y+6),fill=c,outline='#14232b',width=2)
    pick=next(r for r in rows if r['capsuleGap']==(1.9 if move=='sword3' else 2.1))
    x,y=xy(pick['capsuleGap'],pick['sweepGapM'])
    t(x-29,y+12 if move=='sword3' else y-36,f"{pick['sweepGapM']:.2f} m",19,c,True)
for x in (.65,1.1,1.5,1.9,2.1,2.6):
    px,_=xy(x,0);t(px-19,551,str(x),16,muted)
t(1017,551,'CAPSULE GAP (m)',13,muted,True)
t(35,622,'●  Third cut',18,cyan,True)
t(222,622,'●  Dodge counter',18,gold,True)
t(459,624,'Front capsule spacing is not distance to visible armor.',18,muted)
t(31,676,'108 farther placements across all sweeps: none within the 6 cm glint gate.',22,white,True)
t(31,713,'Fixed root, static Jack. This does not test moving combat, actual damage, or a phone.',17,muted)
im.save(sys.argv[2],quality=94,subsampling=0)
