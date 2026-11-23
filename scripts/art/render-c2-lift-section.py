"""Draw the measured C2 lift section from gauntlet_pit.py's validation output."""
import json
from pathlib import Path
import sys

out=Path(sys.argv[1])
m=json.loads((out/"validation.json").read_text())
width,height=1150,475
colors={"teal":"#79d4d5","amber":"#f4a451","steel":"#4e5964","floor":"#303b44","ink":"#e0e5e4","muted":"#a3b8bd"}
parts=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
  '<title id="title">C2 reveal lift fit check</title><desc id="desc">North to south section with a 5.6 metre shaft under the flush and raised lift. The fixed frame is 0.86 metres from the art wall. The moving deck stops four metres above ground and its guide is 4.959 metres below ground when flush.</desc>',
  '<rect width="1150" height="475" fill="#111b23"/>',
  '<style>text{font-family:system-ui,sans-serif} .mono{font-family:ui-monospace,monospace}</style>']
def rect(x,y,w,h,fill,stroke=None):
    edge=f' stroke="{stroke}"' if stroke else ""
    parts.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}"{edge}/>')
def label(x,y,c,size,content,style=""):
    parts.append(f'<text x="{x}" y="{y}" fill="{c}" font-size="{size}" class="{style}">{content}</text>')
def line(x,y,x2,y2,c,dash=False):
    d=' stroke-dasharray="5 4"' if dash else ''
    parts.append(f'<path d="M{x:.1f},{y:.1f} L{x2:.1f},{y2:.1f}" fill="none" stroke="{c}"{d}/>')
c=colors
label(30,42,c["ink"],26,"THE PIT  /  C2 REVEAL LIFT")
label(30,68,c["muted"],14,"NORTH → SOUTH  ·  MEASURED ART SECTION  ·  METRES","mono")
for left,phase,top in ((30,"01  FLUSH",0),(587,"02  RAISED",m["lift_top_exported_y"])):
    rect(left,89,533,341,"#162531")
    label(left+16,120,c["amber"],16,phase,"mono")
    origin=left+275; s=22; y0=256
    def x(z):return origin+(z-229)*s
    def y(yy):return y0-yy*s
    def block(z,yr,z2,yr2,fill):
        rect(x(z),y(yr2),(z2-z)*s,(yr2-yr)*s,fill)
    block(219,-5.6,225.4,0,c["floor"]);block(232.6,-5.6,235.5,0,c["floor"])
    block(225.4,-6,232.6,-5.6,c["floor"])
    block(233.35,0,234,5,c["steel"])
    block(225.51,-1.57,225.94,0,c["teal"]);block(232.06,-1.57,232.49,0,c["teal"])
    block(226,top-.38,232,top,c["amber"])
    block(228.7,m["low_guide_y"]+top,229.3,top-.38,c["amber"])
    line(left+17,y(0),left+145,y(0),c["muted"],True);label(left+16,int(y(0)-7),c["muted"],13,"COURT Y=0","mono")
    guide=m["low_guide_y"]+top
    line(x(229.3),y(guide),x(232),y(guide),c["amber"],True)
    label(int(x(229.4)),int(y(guide)-4),c["amber"],13,f"{guide:+.3f} m guide","mono")
    label(int(x(225.4)),406,c["muted"],14,f"{m['shaft_base_y']:.1f} m shaft floor","mono")
    if top:
        line(x(225.75),y(top),x(224.25),y(top),c["amber"])
        label(int(x(220.85)),int(y(top)+4),c["amber"],14,"+4.000 m","mono")
    else:
        line(x(232.49),y(3.18),x(233.35),y(3.18),c["teal"])
        label(int(x(232.12)),int(y(3.18)-6),c["teal"],13,f"{m['lift_south_wall_clearance_m']:.2f} m","mono")
label(30,453,c["muted"],14,"AMBER  moving deck and guide    ·    TEAL  fixed frame    ·    Art fit only; no gameplay collision.")
parts.append("</svg>")
(out/"nov23-gauntlet-pit-section.svg").write_text("\n".join(parts)+"\n")
