"""Compose a labeled motion readout from the exact reimported Blender frame."""
import json
from pathlib import Path
import sys

from PIL import Image,ImageDraw,ImageFont

d=Path(sys.argv[1])
data=json.loads((d/'validation.json').read_text())
src=Image.open(d/'nov25-zip-sway-offset.jpg').convert('RGB')
out=Image.new('RGB',(1580,1010),'#162028')
out.paste(src,(0,0))
draw=ImageDraw.Draw(out)
t='/usr/share/fonts/truetype/dejavu/DejaVuSans'
def text(x,y,s,px,c,kind='',anchor='la'):
    draw.text((x,y),s,fill=c,anchor=anchor,font=ImageFont.truetype(t+kind+'.ttf',px))
draw.rounded_rectangle((38,36,544,187),radius=16,fill='#17262f',outline='#526772',width=2)
text(62,56,'W11a  /  WEST ZIP CROSSWIND',17,'#d6c19a','Mono')
text(61,95,'Midspan at 1.25 s',37,'#f0e9d6','-Bold')
text(62,148,'A real GLB frame with a still-air reference.',20,'#b7c6ce')
y=826
for title,col,x in [('Still-air centre','#53c6da',56),('Cable at peak','#f4ac65',350)]:
    draw.line((x,y,x+55,y),fill=col,width=8)
    text(x+73,y,title,22,'#e4e6e6',anchor='lm')
draw.line((54,868,1522,868),fill='#40515d',width=2)
for x,head,sub in [(56,'38 cm','MIDSPAN SIDE TRAVEL'),(468,'7.6 cm','EXTRA DOWNWARD DIP'),(880,'0 mm','ENDPOINT DRIFT'),(1292,'5.0 s','LOOP DURATION')]:
    text(x,892,head,31,'#f0e9d6','-Bold')
    text(x,946,sub,15,'#9fb2be','Mono')
assert data['swayPerSideMeters']==.38 and data['peakExtraDropMeters']==.076 and data['periodSeconds']==5
out.save(d/'nov25-zip-sway-offset.webp',quality=87,method=6)
