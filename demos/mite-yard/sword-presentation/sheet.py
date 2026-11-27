"""Draw a measured (not gameplay) contact-frame comparison."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json, math, sys
proof=json.loads(Path(sys.argv[1]).read_text())
take={a['move']:a for a in proof['cases'] if a['hz']==60 and a['wind']==1}
im=Image.new('RGB',(1200,770),'#0d1821'); d=ImageDraw.Draw(im)
fonts=Path('/usr/share/fonts/truetype/dejavu')
muted='#a5b6c1'; cyan='#7ce3dd'; amber='#f7b568'; white='#f2f7fa'
def text(x,y,s,k,c=white,b=False):
    f=ImageFont.truetype(str(fonts/('DejaVuSans-Bold.ttf' if b else 'DejaVuSans.ttf')),k)
    d.text((x,y),s,font=f,fill=c)
text(29,20,'WILDSHARD   /   COMBAT LAB',16,cyan,True)
text(29,50,'Read the blade on the hit frame',37,white,True)
text(31,105,'Measured Shop Blade sockets on the existing Rook rig · 60 Hz · fixed-root test',18,muted)
def panel(x,key,title,sub):
    row=take[key]
    d.rounded_rectangle((x,155,x+552,678),radius=15,fill='#162631',outline='#425a68',width=2)
    text(x+18,172,title,23,white,True)
    text(x+19,205,sub,16,muted)
    cx=x+276; cy=520; scale=107
    def point(p):
        xx,y,z=p
        return cx+scale*(.87*xx+.57*z),cy+scale*(-.8*y+.30*xx-.43*z)
    def line(a,b,c,w=1):
        d.line([point(a),point(b)],fill=c,width=w)
    for i in range(-3,4):
        t=i/2
        line((t,0,-1.5),(t,0,1.5),'#263c49')
        line((-1.5,0,t),(1.5,0,t),'#263c49')
    line((0,0,0),(0,0,.8),'#678791',3)
    ax,ay=point((0,0,.89));text(ax-5,ay+3,'FORWARD',10,muted)
    a=point((0,0,0)); d.ellipse((a[0]-5,a[1]-5,a[0]+5,a[1]+5),fill=muted)
    text(a[0]-51,a[1]+11,'ROOT',10,muted)
    for c,k in [(amber,'old'),(cyan,'new')]:
        f=row[k]; a=point(f['start']); b=point(f['tip'])
        dx,dy=b[0]-a[0],b[1]-a[1]; length=math.hypot(dx,dy)
        px,py=dy/length*6,-dx/length*6
        d.line([a,b],fill='#0a131a',width=20)
        d.polygon([(a[0]+px,a[1]+py),(b[0]-dx*.10+px*.65,b[1]-dy*.10+py*.65),b,
                   (b[0]-dx*.10-px*.65,b[1]-dy*.10-py*.65),(a[0]-px,a[1]-py)],fill=c)
        d.ellipse((b[0]-5,b[1]-5,b[0]+5,b[1]+5),fill=c,outline='#0a131a')
        d.ellipse((a[0]-6,a[1]-6,a[0]+6,a[1]+6),fill='#0a131a',outline=c,width=2)
    a,b=point(row['old']['tip']),point(row['new']['tip'])
    for i in range(0,18,2):
        d.line([(a[0]+(b[0]-a[0])*i/18,a[1]+(b[1]-a[1])*i/18),
                (a[0]+(b[0]-a[0])*(i+1)/18,a[1]+(b[1]-a[1])*(i+1)/18)],fill='#d7e5ed',width=2)
    d.rectangle((x+2,582,x+550,662),fill='#162631')
    text(x+19,584,f"{row['tipDelta']:.2f} m",34,white,True)
    text(x+160,602,'tip shift in one update',20,muted)
    text(x+19,638,f"Previous phase {row['old']['actionT']:.3f}   →   Hit phase {row['new']['actionT']:.3f}",16,muted)
panel(28,'sword3','Third sword cut','Ordinary combo hit, not the Finish action')
panel(620,'swordRise','Dodge counter','Rising sword, starting from the counter phase')
text(31,711,'●  Previous-tick blade',17,amber,True)
text(297,711,'●  Current hit-phase blade',17,cyan,True)
text(616,712,'Socket diagram only. No collision or phone claim.',17,muted)
im.save(sys.argv[2],quality=94,subsampling=0)
