"""Compose staged reference measurements, not an in-game HUD."""
import sys,json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
p=Path(sys.argv[1]); proof=json.loads(Path(sys.argv[2]).read_text())
out=Path(sys.argv[3])
im=Image.new('RGB',(900,1166),'#101b24');d=ImageDraw.Draw(im)
font=Path('/usr/share/fonts/truetype/dejavu')
blue='#7ce3dd';gray='#9fb3bf';white='#eef5fb';orange='#f7b568'
def t(at,s,size=18,c=white,b=False):
    f=ImageFont.truetype(str(font/('DejaVuSans-Bold.ttf' if b else 'DejaVuSans.ttf')),size)
    d.text(at,s,font=f,fill=c)
t((27,21),'WILDSHARD   /   COMBAT LAB',16,blue,True)
t((27,48),'Read the charge before lock-on',37,white,True)
t((28,102),'12 m encounter fixture  ·  402 × 874  ·  Pallet Jack',19,gray)
cases={c['id']:c['summary'] for c in proof['cases']}
for x,name,key,title in [(26,'open','12m-open','OPEN LANE'),(466,'cover','12m-crate-corner','CRATE CORNER')]:
    row=cases[key]
    d.rounded_rectangle((x,148,x+407,1051),radius=12,fill='#182733',outline='#415767',width=2)
    t((x+16,161),title,17,orange if name=='cover' else blue,True)
    im.paste(Image.open(p/f'{name}.jpg').resize((348,757),Image.Resampling.LANCZOS),(x+30,193))
    t((x+16,963),f"Head or fork visible   {row['bodyFrames']}/57",17,gray)
    t((x+16,1001),f"Floor lane visible    {row['laneFrames']}/57",22,white,True)
t((28,1078),'Staged Blender comparison. Counts come from the separate 60 Hz rig and ray probe.',16,gray)
t((28,1107),'No camera lock, no new HUD for either view. Not live gameplay.',16,gray)
im.save(out,quality=93,subsampling=0)
