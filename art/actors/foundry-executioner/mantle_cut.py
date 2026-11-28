"""Patterned shoulder wrap for the single Executioner, in authoring coordinates."""
from math import pi, sin, cos
from mathutils import Vector

def make_wrap(surface, line, fabric, leather, edge):
    """An open pattern sewn at the back, pulled across one shoulder, with no mirrored copy."""
    n,m=25,11
    def point(u,v):
        # Free front edge crosses from sternum to upper shoulder as the cloth descends.
        # Back edge wraps just around the spine; the rigid pauldron stays exposed.
        a=-.36-3.50*u-.32*(1-u)**4*v
        shoulder=sin(pi*u)**1.32
        left=sin(a)<0
        sx=.081+.008*cos(5*pi*u)
        sy=.077+.012*sin(3*pi*u)
        shoulder_width=.290 if left else .120
        rx=(1-v)*sx+v*(.096+shoulder_width*shoulder)
        ry=(1-v)*sy+v*(.132+.115*shoulder)
        gather=(.005+.016*shoulder*v)*sin(7*pi*u+1.3*v)
        billow=.021*shoulder*sin(pi*v)
        local=(rx+gather+billow)*sin(a)
        dept=-(ry+gather+billow)*cos(a)
        front_rise=.145*max(0,1-u*5)
        z=1.657-v*(.211+.146*shoulder-front_rise)
        z+=.029*shoulder*sin(4*pi*u+v*.25)*(.25+.75*v)
        z+=.009*sin(8*u*pi+v*2.4)*sin(v*pi)
        # Pull the wrap over the outer upper sleeve rather than through its shoulder.
        z+=.116*max(0,-sin(a))**4*v**1.10
        return local+.007,dept+.022,z
    shoulder=Vector((-.186,.027,1.537))
    upper=Vector((-.322,.041,1.263))-shoulder
    def clear_sleeve(p):
        q=Vector(p)
        t=max(0,min(1,(q-shoulder).dot(upper)/upper.length_squared))
        axis=shoulder+upper*t
        delta=q-axis
        # Draw the patterned wrap over a conservative sleeve envelope.
        # Keeps the authored shoulder legible without a cloth simulation.
        radius=.128-.035*t
        if .0001<delta.length<radius:
            q=axis+delta.normalized()*radius
        return tuple(q)
    verts=[clear_sleeve(point(i/(n-1),j/(m-1))) for j in range(m) for i in range(n)]
    faces=[]
    for j in range(m-1):
        for i in range(n-1):
            k=j*n+i;faces.append((k,k+1,k+n+1,k+n))
    surface('Shoulder mantle | asymmetric fireproof cloth',verts,faces,fabric,sub=1,thickness=.0045)
    # Diagonal lap hangs over the front, distinct from the heavier steel side.
    # The short lower edge never reaches the belt; the breastplate stays legible.
    nu,nv=18,7
    lap=[]
    for j in range(nv):
        v=j/(nv-1)
        for i in range(nu):
            u=i/(nu-1)
            x=-.219+.286*u+.021*sin(pi*u)*v
            y=-.098-.064*sin(pi*.72*u)-.014*sin(pi*v)-.008*sin(5*pi*u+3*v)
            z=1.572+.033*sin(pi*u)-.010*u-v*(.102-.071*u+.008*sin(3*pi*u))
            lap.append(clear_sleeve((x,y,z)))
    quads=[]
    for j in range(nv-1):
        for i in range(nu-1):
            k=j*nu+i;quads.append((k,k+1,k+1+nu,k+nu))
    surface('Shoulder mantle | asymmetric front lap',lap,quads,fabric,sub=1,thickness=.004)
    # One small clasp fastens the cut at the throat. Its positions follow the pattern.
    x,y,z=point(.024,.51)
    line('Shoulder mantle | throat clasp',[(x-.016,y-.004,z-.012),(x-.010,y-.008,z+.008),
         (x+.013,y-.008,z+.011),(x+.020,y-.004,z-.006)],.0025,edge)
