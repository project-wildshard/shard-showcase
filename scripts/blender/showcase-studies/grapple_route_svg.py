"""W7a review plate. X/Z are at scale; the labels show true 3D center spans."""
import json
from pathlib import Path
import sys
from xml.sax.saxutils import escape

src,dest=map(Path,sys.argv[1:])
d=json.loads(src.read_text())
parts=['<svg xmlns="http://www.w3.org/2000/svg" width="972" height="692" viewBox="0 0 972 692" role="img" aria-labelledby="title desc">',
       '<title id="title">West grapple reference centers</title>',
       '<desc id="desc">Five reference hoop centers, with 3D spans and the old roof proxy, plus the separate W7b zipline.</desc>',
       '<rect width="972" height="692" rx="19" fill="#112831"/>',
       '<rect x="34" y="125" width="904" height="466" rx="9" fill="#0c1e26" stroke="#2e4750"/>']
def label(x,y,s,size=20,c="#e9eee9",align="start",halo=False):
    p=' paint-order="stroke" stroke="#0c1e26" stroke-width="7" stroke-linejoin="round"' if halo else ''
    parts.append(f'<text x="{x}" y="{y}" fill="{c}" font-family="system-ui,sans-serif" font-size="{size}" text-anchor="{align}"{p}>{escape(s)}</text>')
# For a north-up view, negative Z goes up. Use a single scale for both axes.
def map_coord(p):return 112+(p[0]+238)*3.8, 188+(p[2]+118)*3.8
def line(a,b,color,width=3,dash=""):
    x,y=a;X,Y=b
    p=f' stroke-dasharray="{dash}"' if dash else ''
    parts.append(f'<path d="M{x:.1f} {y:.1f}L{X:.1f} {Y:.1f}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round"{p}/>')
def dot(p,r,fill,stroke="#0e222a",width=2):
    x,y=p
    parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>')
label(38,55,"WEST GRAPPLE  /  REFERENCE CENTERS",29)
label(39,91,"WSC-KIT-004 • W7a tank placement study • world X/Z viewed from above",18,"#a9c5cb")
for x in range(-230,-104,10):
    a=map_coord((x,0,-118));b=map_coord((x,0,-17))
    line(a,b,"#233b43",1)
for z in range(-110,-19,10):
    line(map_coord((-238,0,z)),map_coord((-107,0,z)),"#233b43",1)
nodes=[map_coord(c["world_m"]) for c in d["centers"]]
old=map_coord(d["old_roof_proxy_m"])
line(nodes[1],old,"#9c8d82",2,"5 6")
dot(old,6,"#0c1e26","#baa798",2)
label(old[0]-16,old[1]-11,"Old roof proxy",15,"#ddcdc1",halo=True)
label(old[0]-17,old[1]+29,"51.05 m from pole 2",15,"#ddcdc1",halo=True)
zip1,zip2=[map_coord(p) for p in d["w7b_separate_endpoints_m"]]
line(zip1,zip2,"#7688a7",3,"11 5")
for z in [zip1,zip2]:dot(z,5,"#b2bad5")
label(407,551,"W7b zipline • separate points",16,"#bfcbec")
shifts=[(17,8),(17,-12),(-128,38),(14,-12),(-17,-16)]
for i,span in enumerate(d["adjacent_spans_m"]):
    a,b=nodes[i:i+2]
    focus=i==1 or i==3
    hue="#ffd582" if i==3 else "#62deca"
    line(a,b,hue,4 if focus else 3)
    x,y=((a[0]+b[0])/2,(a[1]+b[1])/2)
    x+=16 if i==1 else (-25 if i==3 else 14)
    y+=-5 if i==1 else 7
    label(x,y,f"{span:.2f} m",16,hue,align="end" if i==3 else "start",halo=True)
for (x,y),c,(dx,dy) in zip(nodes,d["centers"],shifts):
    dot((x,y),8,"#a2f5dd")
    label(x+dx,y+dy,c["label"],17,halo=True)
parts.append('<rect x="664" y="179" width="226" height="233" rx="5" fill="#162c36" stroke="#314c58"/>')
label(682,211,"READING THE SPANS",16,"#9fe7dd")
label(682,245,"38 m is the default game",17)
label(682,269,"eye-to-hook limit.",17)
label(682,308,"The map shows reference",16,"#b7cbd1")
label(682,333,"centers, not takeoff eyes",16,"#b7cbd1")
label(682,358,"or line-of-sight results.",16,"#b7cbd1")
label(682,392,"Tank rim is a proposal.",16,"#ffd582")
line((850,472),(850,437),"#a7bcc7",3)
label(850,429,"−Z",17,"#adc5d3","middle")
line((674,548),(750,548),"#adc5d3",2)
label(712,573,"20 m plan scale",15,"#adc5d3","middle")
label(38,630,"Next: measure the player’s actual eye positions and obstructions before setting hook rows.",17,"#b8d1d3")
label(38,657,"Drawing uses the existing tower proxy and does not move the W7b zip attachments.",16,"#90a8ac")
dest.write_text("\n".join([*parts,"</svg>"])+"\n")
