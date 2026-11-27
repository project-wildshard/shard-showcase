"""Compose the two measured-view stills; labels and layout are not game HUD."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

p=Path(sys.argv[1]); out=Path(sys.argv[2])
w,h=900,1160
bg='#101b24'; muted='#92a5b4'; pale='#eef5fb'; gold='#f7b568'; cyan='#7ce3dd'
im=Image.new('RGB',(w,h),bg); d=ImageDraw.Draw(im)
base=Path('/usr/share/fonts/truetype/dejavu')
def f(s,b=False):return ImageFont.truetype(str(base/('DejaVuSans-Bold.ttf' if b else 'DejaVuSans.ttf')),s)
def word(pos,value,size,color=pale,b=False): d.text(pos,value,font=f(size,b),fill=color)
word((32,24),'WILDSHARD   /   COMBAT LAB',16,cyan,True)
word((32,54),'Keep the charge tell in view',36,pale,True)
word((34,110),'750 ms into a 950 ms wind-up  ·  Third person, 402 × 874',18,muted)
for name,x,title,by,count,color in [
 ('baseline',32,'ORIGINAL CAMERA','Jack has left the frame','34 / 57',gold),
 ('candidate',466,'CANDIDATE HOLD','Jack remains in view','57 / 57',cyan),
]:
    d.rounded_rectangle((x-2,157,x+403,1085),radius=10,fill='#1c2b37',outline='#415461',width=1)
    word((x+13,171),title,17,color,True)
    im.paste(Image.open(p/f'{name}.png').convert('RGB').resize((348,757),Image.Resampling.LANCZOS),(x+27,204))
    # Put the readout over a clean caption band, above the footer.
    d.rectangle((x,961,x+401,1084),fill='#182530')
    word((x+13,976),count,30,color,True)
    word((x+158,991),'wind-up frames visible',17,muted)
    word((x+14,1030),by,20)
word((34,1109),'Staged render from measured camera transforms. Cyan disc marks the player.',17,muted)
im.save(out,quality=92,subsampling=0)
