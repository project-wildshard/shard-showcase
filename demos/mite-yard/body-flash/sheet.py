"""Stack two time samples side by side; all portrait images retain their bounds."""
from PIL import Image,ImageDraw,ImageFont
import sys
from pathlib import Path
p=Path(sys.argv[1]); out=Path(sys.argv[2])
im=Image.new('RGB',(1320,889),'#101b24');d=ImageDraw.Draw(im)
fonts=Path('/usr/share/fonts/truetype/dejavu')
def word(at,value,size,color='#eef5fb',bold=False):
    f=ImageFont.truetype(str(fonts/('DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf')),size)
    d.text(at,value,font=f,fill=color)
cyan='#7ce3dd';gold='#f7b568';gray='#a9bbc7'
word((24,20),'WILDSHARD   /   COMBAT LAB',15,cyan,True)
word((24,43),'Keep Jack’s armor readable on impact',36,bold=True)
word((26,94),'Same model, camera, light and sparks. Only the body flash changes.',20,gray)
cols=[
    (24,2,'ORIGINAL WASH','99% white mix',gold),
    (349,2,'CAPPED PULSE','7% white mix',cyan),
    (674,6,'ORIGINAL WASH','97% white mix',gold),
    (999,6,'CAPPED PULSE','Wash already gone',cyan),
]
word((24,136),'+33 ms AFTER CONTACT',16,gray,True)
word((674,136),'+100 ms AFTER CONTACT',16,gray,True)
for x,n,label,sub,c in cols:
    key='original' if 'ORIGINAL' in label else 'candidate'
    d.rounded_rectangle((x,169,x+298,833),radius=9,fill='#1c2b37',outline='#405462')
    word((x+12,178),label,14,c,True)
    im.paste(Image.open(p/f'wash-{n}-{key}.jpg').convert('RGB').resize((274,596),Image.Resampling.LANCZOS),(x+12,207))
    word((x+12,809),sub,14,gray)
word((24,850),'Staged material A/B. Percentages are linear mix weights from the hit-stop model, not pixel luminance.',16,gray)
im.save(out,quality=92,subsampling=0)
