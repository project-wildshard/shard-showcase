"""Turn the normalized, pinned layout into a printable catalogue atlas."""
import json
import sys
from pathlib import Path
from xml.sax.saxutils import escape

if len(sys.argv)!=3:
    raise SystemExit("Usage: render-round5-atlas.py <layout.json> <output.svg>")
d=json.loads(Path(sys.argv[1]).read_text())
surf=d["surface"];z=d["below"];zones=surf["zones"]
assert d["cell"]==[500,250] and d["semantics"]=={"x":"east","z":"south","y":"up","dimensions":"metres"}
assert surf["seam_x"]==7.5 and surf["town_gates"][0]==["E",-8,0]
assert d["below"]["vault_bounds_D41"]==[151,221,-99,-29,-50,-30]
assert z["titan_sky_y"]==-80 and z["titan_floor_y"]==-150 and z["titan_floor_diameter"]==104
assert len(zones["TG"]["geometry"])==3
W,H=1440,1040
X,Y,S=52,181,1.52
AZ=lambda y:292-y*3.04
mapx=lambda x:X+(x+250)*S
mapy=lambda z:Y+(z+250)*S
b=['<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="1040" viewBox="0 0 1440 1040" role="img" aria-labelledby="title desc">']
b+=['<title id="title">Wildshard surface atlas and interior depths</title>',
    '<desc id="desc">Source-derived plan of a 500 metre cell with West Town, the East Gate, Gauntlet courts and Titan portal; a separate section places the Vault and hidden Titan arena below ground.</desc>',
    '<defs><pattern id="draft" width="76" height="76" patternUnits="userSpaceOnUse" x="52" y="181"><path d="M76 0H0V76" fill="none" stroke="#86a3ac" stroke-width="1" stroke-opacity=".15"/></pattern></defs>']
ink="#f4ebd5";mute="#a4b7b7";accent="#f0c376";cyan="#9dddd2";purple="#c0b2e0"
def rect(x,y,w,h,f,st="none",sw=0,r=0):
    b.append(f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="{r:g}" fill="{f}" stroke="{st}" stroke-width="{sw:g}"/>')
def line(x1,y1,x2,y2,c,sw=1,dash=""):
    b.append(f'<line x1="{x1:g}" y1="{y1:g}" x2="{x2:g}" y2="{y2:g}" stroke="{c}" stroke-width="{sw:g}"{f" stroke-dasharray={chr(34)}{dash}{chr(34)}" if dash else ""}/>')
def path(data,f="none",st="none",sw=0):
    b.append(f'<path d="{data}" fill="{f}" stroke="{st}" stroke-width="{sw:g}" stroke-linejoin="round"/>')
def circle(x,y,r,f,st="none",sw=0):
    b.append(f'<circle cx="{x:g}" cy="{y:g}" r="{r:g}" fill="{f}" stroke="{st}" stroke-width="{sw:g}"/>')
def t(x,y,word,size=20,fill=ink,weight=400,align="start",track=0):
    b.append(f'<text x="{x:g}" y="{y:g}" font-family="DejaVu Sans" font-size="{size:g}" fill="{fill}" font-weight="{weight}" text-anchor="{align}" letter-spacing="{track:g}">{escape(word)}</text>')
def wm(x,z0,*args,**kwargs):t(mapx(x),mapy(z0),*args,align="middle",**kwargs)
def rct(a,f,st="none",sw=0,r=0):
    a0,a1,b0,b1=a;rect(mapx(a0),mapy(b0),(a1-a0)*S,(b1-b0)*S,f,st,sw,r)
def shape(z,f,st,sw=2):
    k=z["shape"];v=z["geometry"]
    if k=="rect":rct(v,f,st,sw,2)
    elif k=="rects":
        for a in v:rct(a,f,st,sw)
    elif k=="disc":
        x,y,r=v;circle(mapx(x),mapy(y),r*S,f,st,sw)
    elif k=="stadium":
        x,y,r,L=v;rct([x-L-r,x+L+r,y-r,y+r],f,st,sw,r*S)
    else:raise ValueError(k)
def pill(x,y,txt,c,fill):
    w=15+8.4*len(txt);rect(x,y-17,w,22,fill,r=4);t(x+8,y-2,txt,12,c,700,track=.45)
rect(0,0,W,H,"#101d25")
t(53,54,"WILDSHARD   /   SHOWCASE FIELD ATLAS",16,accent,700,track=2.1)
t(49,114,"One cell, two worlds",53,ink,700)
t(54,147,"ROUND 5 SURFACE PLAN WITH LATER DESIGN DECISIONS",15,mute,700,track=1.7)
t(1388,54,"PLATE 01     /     WSC-SCENE-009",14,mute,700,"end",1.3)
t(1388,146,"500 × 500 m  •  NORTH UP",16,cyan,700,"end",1)
# Main map: coordinate grid, road loop and surface objects only.
rct([-250,250,-250,250],"#162c33","#79949a",1.6)
rct([-250,250,-250,250],"url(#draft)")
inner,outer=surf["ring"]
for a in [(-outer,outer,-outer,-inner),(-outer,outer,inner,outer),(-outer,-inner,-inner,inner),(inner,outer,-inner,inner)]:
    rct(a,"#405557")
for a in [surf["east_road"],surf["titan_road"]]:rct(a,"#5d5c51")
rct([-128,8,-6,6],"#52605b")
sectionx=mapx(surf["seam_x"])
for a,c in [(-237,-6),(6,237)]:line(sectionx,mapy(a),sectionx,mapy(c),"#b7b4a1",3.3)
# No level-band boundaries or heat fills: useful road and venue geometry only.
for k,item in zones.items():
    f,edge=("#28484b","#598783")
    if k=="01":f,edge="#5b4d37","#c7a66d"
    if k in {"07","08F","08A","08B","08C","M6","TG"}:f,edge="#514842","#a78365"
    if k in {"TG","TV"}:f,edge="#4d445e","#a99ac7"
    shape(item,f,edge)
for a in surf["gauntlet_passages"]:
    rct(a,"#796855")
# Trace only the bolt-on oval symbol and validated gate/mouth positions.
x,zz,r,L=zones["04"]["geometry"]
rct([x-L-r+8,x+L+r-8,zz-r+8,zz+r-8],"none","#86b7ac",1, (r-8)*S)
for _,x,zz in surf["town_gates"]:circle(mapx(x),mapy(zz),3.1,accent)
for x,zz in surf["cave_mouths"]:circle(mapx(x),mapy(zz),3.4,cyan)
circle(mapx(216),mapy(229),3.6,purple)
circle(sectionx,mapy(0),5,accent,"#172a30",2)
wm(-122,-182,"Riding Course",21,ink,700)
wm(-122,-164,"479 m lap",12,cyan)
wm(-119,-103,"Movers Run",16,ink,700)
wm(-119,-88,"six stations",11,cyan)
wm(-38,-103,"Paddock",13,ink,700)
wm(-200,-78,"Grapple",16,ink,700)
wm(-200,-62,"Course",16,ink,700)
wm(-206,42,"The Rock",13,ink,700)
wm(-206,55,"Squeeze cave",9.6,cyan)
wm(-156,38,"Climb",13,ink,700)
wm(-156,51,"Yard",13,ink,700)
wm(-65,-7,"WEST TOWN",23,ink,700)
wm(-65,12,"120 × 120 m",13,"#e4c99b")
wm(-49,119,"Weapon",15,ink,700)
wm(-49,133,"Range",15,ink,700)
wm(-53,210,"Physics Yard",14,ink,700)
wm(-168,167,"Hover Park",21,ink,700)
wm(-168,187,"Launch walls",13,cyan)
wm(-168,201,"Bowl · funbox · rails",11,cyan)
wm(175,62,"Stealth Yard",20,ink,700)
wm(175,79,"surface set",11,"#d9ae8d")
wm(80,137,"Gauntlet forecourt",11,ink,700)
wm(55,169,"C1  Loading Yard",12,ink,700)
wm(55,215,"C2  The Pit",14,ink,700)
wm(146,179,"C3",16,ink,700)
wm(146,194,"Foreman’s Floor",12,ink,700)
wm(214,215,"Titan",12,ink,700)
wm(214,225,"Portal",12,ink,700)
wm(138,-4,"East road",13,ink,700)
wm(130,-117,"E A S T   F I E L D",21,"#9db0ad",700)
wm(130,-98,"Combat regions omitted from this plate",12,"#95a9a7")
# Labels with leader lines for small true-footprint features.
line(mapx(215),mapy(-61),mapx(176),mapy(-77),purple,1.6)
t(mapx(173),mapy(-78),"Vault Gate",14,purple,700,"end")
line(mapx(96),mapy(-206),mapx(117),mapy(-218),"#c6a488",1.5)
t(mapx(121),mapy(-219),"Big Pallet",13,"#dabba0",700)
line((sectionx+mapx(-8))/2,mapy(0),mapx(25),mapy(28),accent,1.5)
t(mapx(28),mapy(32),"East Gate crossing",14,accent,700)
t(mapx(28),mapy(44),"arch + seam wall",11,accent)
t(773,218,"N",16,ink,700,"middle")
path("M773 226l8 22-8-4-8 4z",accent)
t(53,973,"← WEST",12,mute,700,track=1)
t(812,973,"EAST →",12,mute,700,"end",1)
for i in range(2):rect(578+i*76,962,76,8,accent if i==0 else "#385254","#9db2af",1)
for x,tick in [(578,"0"),(654,"50"),(730,"100 m")]:t(x,991,tick,11,mute,400,"middle")
# Separate, scale-linear altitude chart. Widths of the bars are explanatory.
rect(844,181,544,760,"#182831","#40535b",1.2,8)
t(876,225,"Below the surface",29,ink,700)
t(877,251,"SHARED ELEVATION DATUM  /  METRES",13,mute,700,track=1.4)
for h in (0,-30,-50,-80,-150):
    yy=AZ(h);line(901,yy,1360,yy,"#596b70",1,"4 5" if h else "")
    t(897,yy+5,str(h).replace("-","−"),15,mute,700,"end")
line(911,AZ(0),911,AZ(-150),"#768a8c",1.5)
t(934,AZ(0)-8,"SURFACE DATUM",12,accent,700,track=1.0)
rect(931,AZ(-30),163,AZ(-50)-AZ(-30),"#3b5260","#95bbc3",1.5,4)
t(945,AZ(-30)+25,"Training Vault",17,ink,700)
t(945,AZ(-30)+45,"20 m tall · D41",12,cyan)
t(1110,AZ(-30)+25,"70 × 70 m envelope",14,mute)
t(1110,AZ(-30)+48,"Four rooms under the east field",12,mute)
bracket=1124
line(bracket,AZ(-50)+2,bracket,AZ(-80)-2,accent,1.4)
line(bracket-6,AZ(-50)+2,bracket+6,AZ(-50)+2,accent,1.4)
line(bracket-6,AZ(-80)-2,bracket+6,AZ(-80)-2,accent,1.4)
t(bracket+17,(AZ(-50)+AZ(-80))/2+5,"30 m separation",14,accent,700)
rect(931,AZ(-80),427,AZ(-150)-AZ(-80),"#342f46","#ad9bc7",1.5,5)
t(951,AZ(-80)+34,"Hidden Titan arena",23,ink,700)
t(952,AZ(-80)+60,"Arena sky / −80 m",14,purple)
t(953,AZ(-150)-66,"140 m across the stands",14,"#d9cce9")
t(953,AZ(-150)-45,"104 m arena floor",14,"#d9cce9")
t(953,AZ(-150)-18,"Reached through the surface portal",12,purple)
circle(1255,AZ(-80)+115,63,"none","#b4a2d4",1.4)
circle(1255,AZ(-80)+115,63*104/140,"#514865","#cdbee2",1.2)
t(1255,AZ(-80)+119,"FLOOR",11,ink,700,"middle")
line(941,786,1358,786,"#536972",1)
t(933,821,"SHIFT ORIENTATION",14,accent,700,track=1.45)
t(933,851,"Yard Boss  →  Range  →  Riding lap",16,ink,700)
t(933,878,"Movers top deck  →  Zip  →  East Gate",16,ink,700)
t(933,909,"D4 approved tour stops. No navigation line is implied.",11,mute)
t(844,980,"DESIGN SCHEMATIC   •   NOT THE PLAYER MAP OR A LIVE BUILD",12,mute,700,track=.8)
line(53,1007,1388,1007,"#46575e")
t(54,1029,"R05 layout: ce1cf050b3   /   overlays: D4, D7, D41, D61, E12g",11,mute)
t(1388,1029,"Horizontal map to scale. Depth chart uses its own linear axis.",11,mute,400,"end")
b.append("</svg>")
Path(sys.argv[2]).write_text("\n".join(b)+"\n")
