"""Static Jack surface replay; public output contains only aggregate geometry metrics."""
import hashlib, json, math, sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
i=sys.argv.index('--')
p,pose,out=map(Path,sys.argv[i+1:i+4])
mesh=json.loads(p.read_text())
v=mesh["vertices"]; f=mesh["triangles"]
rig_proof=json.loads(pose.read_text())
assert mesh['sourceBlob']=='9603f6c37b94a49904f017c7ee1cd917cab36cf3'
assert mesh['truckScale']==1.18
frontal_radius=.85
threshold=.06
def v3(a): return Vector(a)
def surface():
    return BVHTree.FromPolygons(v,f,all_triangles=True)
tree=surface()
def world_to_jack(point,cx,cz):
    # Jack faces the hero. Hero's sampled rig faces +Z; Jack faces -Z.
    return v3((cx-point[0],point[1],cz-point[2]))
def gap_for(last,cur,cx,cz,phase_div,blade_div):
    best=math.inf
    for i in range(phase_div+1):
        t=i/phase_div if phase_div else 1
        base=v3(last['start']).lerp(v3(cur['start']),t)
        tip=v3(last['tip']).lerp(v3(cur['tip']),t)
        base=world_to_jack(base,cx,cz);tip=world_to_jack(tip,cx,cz)
        for j in range(blade_div+1):
            pt=base.lerp(tip,j/blade_div)
            _,_,tri,d=tree.find_nearest(pt)
            if tri is not None:best=min(best,d)
    assert math.isfinite(best)
    return best
runs=[]
for c in rig_proof['cases']:
    if c['move'] not in {'sword3','swordRise'}: continue
    for capsule_gap in (.65,1.1,1.5,1.9,2.1,2.6):
        for x in (-.55,0,.55):
            z=math.sqrt((capsule_gap+frontal_radius)**2-x*x)
            gap=gap_for(c['old'],c['new'],x,z,24,36)
            fine=gap_for(c['old'],c['new'],x,z,48,72)
            endpoint=gap_for(c['old'],c['new'],x,z,0,72)
            assert abs(gap-fine)<.013
            assert fine<=endpoint+1e-5
            runs.append(dict(move=c['move'],hz=c['hz'],wind=c['wind'],capsuleGap=capsule_gap,sideOffset=x,
                sweepGapM=round(fine,5),endPoseGapM=round(endpoint,5),
                nearby=fine<=threshold,nearAtEnd=endpoint<=threshold))
close=[r for r in runs if r['capsuleGap']<=1.5]
far=[r for r in runs if r['capsuleGap']>=1.9]
assert any(r['nearby'] for r in close), 'positive controls missing'
assert any(not r['nearby'] for r in far), 'negative controls missing'
raw=dict(scope='Fixed-root old/current blade sweep against pinned Jack rest mesh with authored truck-bone scale. No gameplay, Jack animation, actual movement, damage, or device.',
    sourceBlob=mesh['sourceBlob'],truckScale=mesh['truckScale'],
    rigProofSha256=hashlib.sha256(pose.read_bytes()).hexdigest(),triangles=len(f),markerThresholdM=threshold,
    sampling={'normal':[24,36],'fine':[48,72]},
    checks={'total':len(runs),'close':len(close),'nearClose':sum(r['nearby'] for r in close),
            'far':len(far),'nearFar':sum(r['nearby'] for r in far),
            'closeSweepOnly':sum(r['nearby'] and not r['nearAtEnd'] for r in close)},cases=runs)
out.write_text(json.dumps(raw,indent=2)+'\n')
print(raw['checks'])
