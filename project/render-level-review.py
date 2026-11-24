"""Rebuild the two illustrative 390×844 review boards; not browser captures."""
from pathlib import Path
import base64
import hashlib
import subprocess
import sys
import tempfile

dist = Path(__file__).resolve().parents[1] / "dist"
out = Path(sys.argv[1]).resolve()
out.mkdir(parents=True, exist_ok=True)
pins = {
    "fight": ("nov24-e5b-sweep-unmarked.jpg", "jpeg", "ce393adfa3b128330dde1aa91d56006adc24dc86319ba056e65a257298e07aed"),
    "calm": ("nov23-east-vista-seat.jpg", "jpeg", "968462ad84c57df3170a808df16f8e12fe768c7e74a294912918f8f33e2158c9"),
}
font = "DejaVu Sans"
ink, gold, green, muted = "#f5e9d4", "#ffd58d", "#a4dccc", "#b4c4bb"
def label(s,x,y,sz=12,fill=ink,w=600,align="start",ls=0):
    return f'<text x="{x}" y="{y}" font-size="{sz}" fill="{fill}" font-weight="{w}" text-anchor="{align}" letter-spacing="{ls}">{s}</text>'
def box(x,y,w,h,fill,r=6,stroke="none"):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}"/>'
def rule(x1,y1,x2,y2,stroke="#65827a",sw=1):
    return f'<path d="M{x1} {y1}H{x2}" stroke="{stroke}" stroke-width="{sw}"/>' if y1==y2 else f'<path d="M{x1} {y1}L{x2} {y2}" stroke="{stroke}" stroke-width="{sw}"/>'
def ring(cx,cy,r,c,fill="none",dash="0"):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" stroke="{c}" fill="{fill}" stroke-dasharray="{dash}"/>'
def board(state,image):
    fight=state=="fight"
    t=[f'<svg xmlns="http://www.w3.org/2000/svg" width="390" height="844" viewBox="0 0 390 844" font-family="{font}">','''<defs>
    <clipPath id="frame"><rect x="10" y="95" width="370" height="720" rx="12"/></clipPath>
    <linearGradient id="grade" x2="0" y2="1" gradientUnits="objectBoundingBox">
      <stop offset="0" stop-color="#0d161f" stop-opacity=".88"/><stop offset=".3" stop-color="#111c24" stop-opacity=".04"/>
      <stop offset=".63" stop-color="#111c24" stop-opacity=".07"/><stop offset="1" stop-color="#0e1a20" stop-opacity=".91"/>
    </linearGradient>
    <linearGradient id="card" x1="0" x2=".95" y1="0" y2="1" gradientUnits="objectBoundingBox">
      <stop stop-color="#253832"/><stop offset=".84" stop-color="#151e26"/>
    </linearGradient></defs>''',
    box(0,0,390,844,"#121a1c",0),
    label("WILDSHARD",12,27,12,gold,700,ls=1.5),
    label("PORTRAIT UI STUDY",378,26,9,muted,700,"end",1.5),
    box(10,44,182,43,"#413527" if fight else "#202d30",6,"#b8824c" if fight else "#3a5050"),
    box(199,44,181,43,"#202d30" if fight else "#413527",6,"#3a5050" if fight else "#b8824c"),
    label("01   FIGHT CUE",101,70,11,gold if fight else muted,700,"middle",.8),
    label("02   CALM CARD",290,70,11,muted if fight else gold,700,"middle",.8),
    '<g clip-path="url(#frame)">',
    f'<image href="{image}" x="10" y="95" width="370" height="720" preserveAspectRatio="xMidYMid slice"/>',
    box(10,95,370,720,"url(#grade)",0),'</g>',
    box(10,95,370,720,"none",12,"#4f5d57"),
    box(22,108,143,38,"#182327",4),
    rule(22,108,22,146,gold,2),
    label("EAST",30,123,9,gold,700,ls=1.8),
    label("CONTAINER YARD" if fight else "GATE VISTA",30,137,9,ink,700,ls=.9),
    box(258,110,110,24,"#282825",4,"#9d7749"),
    label("2.5 SEC CUE" if fight else "AFTER 5 S CALM",313,126,8,gold,700,"middle",.8)]
    if fight:
        t += [ring(195,445,103,"#f6cc84","none","5 7"),ring(195,445,93,"#f6cc8470","none","23 29")]
        for x,y in [(120,372),(286,387),(274,518),(108,499)]:
            t.append(f'<path d="M{x} {y-5}l5 5-5 5-5-5z" fill="{gold}"/>')
        t += [ring(195,445,6,"#e2f2e5"),rule(184,445,190,445,"#e2f2e5"),rule(200,445,206,445,"#e2f2e5"),
            rule(195,434,195,440,"#e2f2e5"),rule(195,450,195,456,"#e2f2e5"),
            box(24,686,144,30,"#182725",5,"#b48755"),rule(24,690,24,712,gold,2),
            label("LEVEL 7  ·  +11 VIT",34,705,10,gold,700,ls=.5)]
    else:
        t += [box(59,294,278,333,"#121a20",12),box(56,288,278,333,"url(#card)",11,"#bb955e"),
            label("FIELD RECORD",72,310,9,muted,700,ls=1.4),label("06 › 07",318,310,9,gold,700,"end",1.4),
            ring(195,346,23,"#bd925d","#48392b"),
            '<path d="M183 350l12-13 12 13m-19 7 7-8 7 8m-7-25 2-2-2-2-2 2z" stroke="#ffd58d" stroke-width="1.5" fill="none"/>',
            label("P R O G R E S S I O N",195,388,9,muted,700,"middle"),
            label("Level 7",195,427,33,gold,700,"middle")]
        for i,(name,value,c) in enumerate([("Vitality","+11",gold),("Strength","+3",green),("Agility","+2",green),("Focus","+0","#a5aeaa")]):
            y=454+i*30
            t += [rule(77,y-12,313,y-12,"#4a554e"),label(name,79,y+6,12,ink),label(value,311,y+6,13,c,700,"end")]
        t += [rule(77,562,313,562,"#4a554e"),label("Tap to skip",195,596,11,gold,700,"middle")]
    t += [box(24,726,38,19,"#1b2929",3,"#918461"),
          label("LV 7",43,739,9,gold,700,"middle"),
          box(70,733,295,4,"#677a73",2),box(70,733,53.1,4,"#e5ae57",2)]
    for x,y,txt,path in [(47,775,"MOVE","M0-10v16M-8-2H8m-8-8-3 3m3-3 3 3"),
        (274,777,"JUMP","M-7 5H7M0 1v-10m-4 4 4-4 4 4"),
        (342,775,"LOOK","M0-10v3m0 10v3M-8-2h3m10 0h3M0-7a5 5 0 1 0 0 10a5 5 0 1 0 0-10")]:
        t += [ring(x,y,23,"#7eaba3","#203239"),
              f'<path d="{path}" transform="translate({x} {y-4})" stroke="{green}" stroke-width="1.4" stroke-linejoin="round" fill="none"/>',
              label(txt,x,y+14,7,ink,700,"middle",.8)]
    t += [label("UI-01 / 02 / 03",10,834,9,muted,700,ls=.8),
          label("Illustrative HUD · Not gameplay",380,834,9,muted,500,"end"),"</svg>"]
    return "".join(t)
for state,(name,fmt,pin) in pins.items():
    raw=(dist/"media"/name).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==pin
    image=f"data:image/{fmt};base64,"+base64.b64encode(raw).decode()
    with tempfile.TemporaryDirectory() as d:
        svg=Path(d)/"board.svg"
        svg.write_text(board(state,image))
        png=Path(d)/"board.png"
        subprocess.run(["inkscape",str(svg),"-w","780","-o",str(png)],check=True)
        subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-i",str(png),"-frames:v","1","-q:v","2","-y",str(out/f"nov24-hud-level-{state}.jpg")],check=True)
