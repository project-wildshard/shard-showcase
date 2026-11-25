"""Compose two review boards from Blender's own matched inventory frames."""
import json
from pathlib import Path
import sys

from PIL import Image, ImageDraw, ImageFont

from sword_finish_materials import LABELS

out=Path(sys.argv[1])
font_dir=Path('/usr/share/fonts/truetype/dejavu')
files={'regular':'DejaVuSans.ttf','bold':'DejaVuSans-Bold.ttf','mono':'DejaVuSansMono.ttf'}
def font(k,px):
    return ImageFont.truetype(str(font_dir/files[k]),px)
def label(draw,at,string,px,color,face='regular',anchor='la'):
    draw.text(at,string,fill=color,font=font(face,px),anchor=anchor)
ink='#e8dfca'; faint='#a8b9c4'; accents=['#b7c5cc','#7fcedf','#f5a379']

def canvas(w,h,headline,subtitle):
    im=Image.new('RGB',(w,h),'#111b24')
    d=ImageDraw.Draw(im)
    label(d,(41,22),'WILDSHARD / EQUIPMENT',15,'#d7b983','mono')
    label(d,(39,51),headline,36,ink,'bold')
    label(d,(42,106),subtitle,18,faint)
    d.line([(42,145),(w-42,145)],fill='#465864',width=1)
    return im,d

def comp(dest, src, center):
    dest.paste(src,(center[0]-src.width//2,center[1]-src.height//2),src)

def tile(d,cx,y,w,h,a):
    d.rounded_rectangle((cx-w//2,y,cx+w//2,y+h),radius=14,fill='#24323c',outline='#45535e',width=1)
    d.line([(cx-w//2+17,y+10),(cx-w//2+56,y+10)],fill=a,width=3)

im,d=canvas(1500,936,'One sword. Three finishes.','Same mesh, pivot, camera and neutral lighting. Only the named materials change.')
for i,(key,(name,sub)) in enumerate(LABELS.items()):
    cx=(260,750,1240)[i]
    tile(d,cx,163,438,640,accents[i])
    pic=Image.open(out/f'{key}-large.png').convert('RGBA')
    comp(im,pic,(cx,483))
    label(d,(cx,833),name,22,ink,'bold','ma')
    label(d,(cx,868),sub,14,accents[i],'mono','ma')
im.save(out/'nov25-sword-finishes-full.webp',quality=89,method=6)
im,d=canvas(1260,654,'Do they read at inventory size?','Left in each card: native 64 px render. Right: the same pixels enlarged 3×.')
pixels={}
for i,(key,(name,sub)) in enumerate(LABELS.items()):
    cx=(229,630,1031)[i]
    tile(d,cx,173,356,355,accents[i])
    pic=Image.open(out/f'{key}-64.png').convert('RGBA')
    pixels[key]=pic
    d.rounded_rectangle((cx-148,260,cx-52,356),radius=8,fill='#18232b')
    d.rounded_rectangle((cx-28,218,cx+164,410),radius=7,fill='#18232b')
    comp(im,pic,(cx-100,308))
    comp(im,pic.resize((192,192),Image.Resampling.NEAREST),(cx+68,314))
    label(d,(cx-100,397),'64 px',13,faint,'mono','ma')
    label(d,(cx+68,425),'3× crop',13,faint,'mono','ma')
    label(d,(cx,472),name,19,ink,'bold','ma')
    label(d,(cx,506),sub,12,accents[i],'mono','ma')
label(d,(42,567),'Both wraps remain unchanged. Cyan steel and ember copper are art proposals, not live unlocks.',16,faint)
im.save(out/'nov25-sword-finishes-64px.webp',quality=89,method=6)

def rgb(pic):
    return [round(sum(c)/len(c),2) for c in zip(*(p[:3] for j,p in enumerate((pic.get_flattened_data() if hasattr(pic,"get_flattened_data") else pic.getdata())) if p[3]>=220 and j//64<37))]
samples={key:rgb(pic) for key,pic in pixels.items()}
assert samples['warden'][2]-samples['warden'][0]>=22 and samples['hot-mess'][0]-samples['hot-mess'][2]>=22,samples
p=out/'validation.json'
data=json.loads(p.read_text())
data['mask64']['solidUpperPixelsMeanSRGB255']=samples
p.write_text(json.dumps(data,indent=2)+'\n')
