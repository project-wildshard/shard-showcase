"""Source-only E0f/E0g nameplate art. No native HUD code.

Usage: python3 project/ui/e0g-nameplate-study.py OUTPUT IMAGE
IMAGE is the pinned public catalogue image; it is never copied into Git.
"""
import base64
import hashlib
from pathlib import Path
import subprocess
import sys

out, image = map(Path, sys.argv[1:])
out.mkdir(parents=True,exist_ok=True)
assert hashlib.sha256(image.read_bytes()).hexdigest() == '3e75bf4ec41e5a9423f9857f9bca31982168688ac7649c1b85f81b72010528c6'

BG = '#111c22'
GOLD = '#f6dc9d'
INK = '#edf2e4'
MUTED = '#abc4bf'
HP = '#97dcb9'
BUILD = '#e6bc73'
FULL = '#f6f0ce'
TINT = {'none':'#7c9693','burn':'#ff9b61','shock':'#8bdafa'}
STATES = (
    dict(id='steady', top='01  /  NEUTRAL', heading='Baseline',
         copy='HP and stagger stay separate.', tint='none', hp=.93, meter=.09),
    dict(id='burn', top='02  /  BURN TINT', heading='Build-up + burn',
         copy='Orange edge; no extra tick text.', tint='burn', hp=.76, meter=.69),
    dict(id='full', top='03  /  FULL BAR', heading='Staggered',
         copy='Full striped bar; no duplicate tint.', tint='none', hp=.54, meter=1, full=True),
    dict(id='shock', top='04  /  SHOCK TINT', heading='Shock replaces burn',
         copy='Cyan edge; never both at once.', tint='shock', hp=.48, meter=.18),
)

def lin(n):
    c=int(n,16)/255
    return c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4

def lum(s):
    return sum(w*lin(s[i:i+2]) for w,i in zip((.2126,.7152,.0722),(1,3,5)))

def contrast(a,b):
    l,h=sorted((lum(a),lum(b)))
    return (h+.05)/(l+.05)

assert all(contrast(c,BG)>4.5 for c in (INK,GOLD,HP,BUILD,*TINT.values()))
assert {s['tint'] for s in STATES} == {'none','burn','shock'}
assert sum(s.get('full',False) for s in STATES)==1
assert all(s.get('full',False)==(s['meter']==1) for s in STATES)

def text(x,y,s,size,fill=INK,weight=700,spacing=0):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}" letter-spacing="{spacing}">{s}</text>'

def rect(x,y,w,h,fill,r=0,stroke='none'):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}"/>'

WIDTH,HEIGHT=144,39
def nameplate(state):
    tint=TINT[state['tint']]
    p=[
        rect(.5,.5,143,38,BG,4,'#385159'),
        rect(2,5,2,29,tint,1),
        text(10,15,'Lv 2',10,GOLD),
        text(39,15,'Crate Mite',11),
        rect(10,20,124,5,'#2e4844',2),
        rect(10,20,round(124*state['hp']),5,HP,2),
        rect(10,29,124,3,'#3c3931',1),
        rect(10,29,round(124*state['meter']),3,FULL if state.get('full') else BUILD,1),
    ]
    if state.get('full'):
        p.extend(rect(i,29,2,3,'#5f4d30') for i in range(18,131,8))
    return ''.join(p)

def svg(w,h,body,title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="DejaVu Sans, sans-serif" role="img"><title>{title}</title>'+body+'</svg>\n')

sprite = ''.join(f'<symbol id="{s["id"]}" viewBox="0 0 {WIDTH} {HEIGHT}">{nameplate(s)}</symbol>' for s in STATES)
(out/'e0g-nameplate-elements.svg').write_text(svg(WIDTH,HEIGHT,'<defs>'+sprite+'</defs>'+nameplate(STATES[0]),'Four nameplate states; neutral shown'))

# Portrait cards show the same original art plate and camera crop each time.
decoded=subprocess.run(['convert',str(image),'png:-'],check=True,stdout=subprocess.PIPE).stdout
u='data:image/png;base64,'+base64.b64encode(decoded).decode()
p=[rect(0,0,1092,675,'#142128'),text(28,31,'WILDSHARD  /  COMBAT UI',12,GOLD,700,2),
   text(28,71,'Read the hit, not the HUD',34,INK),
   text(28,99,'Four proposed nameplate states, on the same art plate. 144 CSS px nameplate prototype.',14,MUTED,600),
   text(28,649,'ILLUSTRATIVE   ·   NO NATIVE GAMEPLAY OR MOBILE CAPTURE',11,MUTED,700,1.5)]
for j,st in enumerate(STATES):
    x=28+262*j
    y=124
    c=st['id']
    p.extend([
        rect(x,y,248,492,'#192a31',10,'#415f64'),
        text(x+14,y+23,st['top'],10,TINT[st['tint']],700,1.1),
        f'<defs><clipPath id="clip-{c}"><rect x="{x+12}" y="{y+42}" width="224" height="364" rx="5"/></clipPath></defs>',
        f'<g clip-path="url(#clip-{c})"><image href="{u}" width="569" height="364" x="{x-116}" y="{y+42}"/></g>',
        # The repaint is anchored above the original crate at the same screen y in all four crops.
        f'<g transform="translate({x+63} {y+255})">{nameplate(st)}</g>',
        text(x+14,y+441,st['heading'],16),
        text(x+14,y+464,st['copy'],10,MUTED,600),
    ])
board=out/'e0g-nameplate-comparison.svg'
board.write_text(svg(1092,675,''.join(p),'Static comparison of four combat nameplate proposals'))
png=out/'e0g-nameplate-comparison.png'
subprocess.run(['inkscape',str(board),'--export-type=png','--export-filename='+str(png)],check=True)
subprocess.run(['convert',str(png),'-sampling-factor','4:4:4','-quality','91',
                str(out/'nov24-e0g-nameplate-comparison.jpg')],check=True)
print('Contrast vs nameplate backing:', {c:round(contrast(c,BG),2) for c in (INK,GOLD,HP,BUILD,*TINT.values())})
