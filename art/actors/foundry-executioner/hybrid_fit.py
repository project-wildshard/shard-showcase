"""Bounded form transfer from the reconstructed underlay, not copying its guessed surfaces."""
from math import copysign
from mathutils import Vector

def smooth(x):
    t=min(1,max(0,x));return t*t*(3-2*t)

def fit(p):
    x,y,z=p
    a=abs(x)
    # The underlay has strong rear chest volume and wider shoulders. Borrow 20–30%
    # of its differences, not its depth error from the single front-view source.
    upper=smooth((z-1.06)/.19)*(1-smooth((z-1.54)/.25))
    central=1-smooth((a-.16)/.09)
    back=smooth((y+.020)/.15)
    depth=upper*central*back*(.022+.008*smooth((z-1.31)/.21))
    chest_front=upper*central*(1-back)*.007
    upper_arm=smooth((a-.17)/.18)*smooth((z-.92)/.14)*(1-smooth((z-1.50)/.14))
    low_leg=1-smooth((z-.08)/.65)
    boot=low_leg*smooth((a-.09)/.10)
    xx=x+copysign(.030*upper_arm+.025*boot,x)
    yy=y+depth-chest_front-.009*upper_arm
    return Vector((xx,yy,z))

def apply_collection(collection):
    for o in collection.objects:
        if o.type=='MESH':
            for v in o.data.vertices:v.co=fit(v.co)
        elif o.type=='CURVE':
            for spline in o.data.splines:
                for b in spline.bezier_points:
                    left=b.handle_left_type;right=b.handle_right_type
                    a,c,d=fit(b.co),fit(b.handle_left),fit(b.handle_right)
                    b.handle_left_type='FREE';b.handle_right_type='FREE'
                    b.co=a;b.handle_left=c;b.handle_right=d
                    b.handle_left_type=left;b.handle_right_type=right
