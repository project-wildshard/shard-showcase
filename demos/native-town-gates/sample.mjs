import assert from 'node:assert/strict'
import {createHash} from 'node:crypto'
import {readFileSync,writeFileSync} from 'node:fs'
import {createRequire} from 'node:module'
import {dirname,join,resolve} from 'node:path'
import {pathToFileURL} from 'node:url'
const req=createRequire(process.env.WSC_NODE_PROJECT
  ? join(resolve(process.env.WSC_NODE_PROJECT),'package.json') : import.meta.url)
const packagePath=req.resolve('@wildshard/engine/package.json')
assert.equal(JSON.parse(readFileSync(packagePath)).version,'0.1.44')
const root=dirname(packagePath)
const at=p=>import(pathToFileURL(join(root,p)).href)
await at('scripts/sim-node-loader.mjs')
const {SimHost}=await at('src/server/engine/sim.ts')
const {SIM_API_VERSION}=await at('src/shared/engine/sim/apiVersion.ts')
const {loadRapier}=await at('src/shared/engine/physics/rapier.ts')
const {groups}=await at('src/shared/engine/physics/groups.ts')
const R=await loadRapier(readFileSync(join(dirname(req.resolve('@dimforge/rapier3d-simd/package.json')), 'rapier_wasm3d_bg.wasm')))
assert(process.argv[2]&&process.argv[3],'Expected geometry input and replay JSON output')
const raw=readFileSync(process.argv[2]), geometry=JSON.parse(raw)
const hash=createHash('sha256').update(raw).digest('hex')
const dt=1/60
// Starts are selected scene-test waypoints, not a claim about the game spawn.
const start=[-120,0]
const routes={
  West:{mouth:[-128,0],out:[-132,0],points:[]},
  East:{mouth:[-8,0],out:[-5,0],points:[[-55,0],[-50,-4.35],[-23,-4.35],[-16,0]]},
  Stable:{mouth:[-36,-60],out:[-36,-63],points:[[-55,0],[-47,-4.4],[-31.5,-4.4],[-31.5,-22],[-36,-26]]},
  Movers:{mouth:[-95,-60],out:[-95,-63],points:[[-95,0]]},
  Park:{mouth:[-95,60],out:[-95,63],points:[[-95,0]]},
  Range:{mouth:[-36,60],out:[-36,63],points:[[-54,0],[-48,4],[-35.4,4],[-35.4,24],[-36,30]]},
}
function play(name,gate,offset,wall=false){
  const axis=gate.mouth[0]===gate.out[0]?0:1;
  const shift=p=>p.map((v,i)=>v+(i===axis?offset:0));
  const route=[start,...gate.points,shift(gate.mouth),shift(gate.out)];
  const [x,z]=start;
  const host=new SimHost({version:SIM_API_VERSION,id:'w0b-six-gate-bench',seed:25,
    ground:{size:500,height:.1},player:{at:{x,y:.18,z},yaw:Math.PI,speed:4.3},
    entities:[],quests:[],weapon:{id:'disabled-calibration-strike',damage:0}}, {rapier:R,ground:false});
  const p=host.players.get('actor.player'), W=host.physics.world;
  try{
    for(const g of geometry) W.createCollider(R.ColliderDesc.trimesh(new Float32Array(g.vertices),new Uint32Array(g.triangles))
      .setCollisionGroups(groups('WORLD')));
    if(wall) W.createCollider(R.ColliderDesc.cuboid(.18,1,2.2).setTranslation(-128,1,0).setCollisionGroups(groups('WORLD')));
    for(let k=0;k<50;k++) host.step();
    assert(p.hasMotor&&p.motor.opts.radius===.38&&p.fall.grounded);
    let waypoint=1,stall=0,longestStall=0,longestAir=0,air=0,distance=0,tick=0;
    const frames=[],turns=[];
    for(tick=1;tick<=2200&&waypoint<route.length;tick++){
      let [tx,tz]=route[waypoint]
      let dx=tx-p.position.x,dz=tz-p.position.z,left=Math.hypot(dx,dz)
      if(left<.105){
        turns.push({tick,waypoint,feet:p.position.toArray(),grounded:p.fall.grounded})
        waypoint++
        if(waypoint===route.length)break
        ;[tx,tz]=route[waypoint]
        dx=tx-p.position.x;dz=tz-p.position.z;left=Math.hypot(dx,dz)
      }
      const before=p.position.clone();
      const speed=Math.min(1,left/(4.3*dt));
      host.step(new Map([[p.id,{moveX:speed*dx/left,moveZ:speed*dz/left,yaw:Math.atan2(-dx,-dz)}]]));
      const moved=Math.hypot(p.position.x-before.x,p.position.z-before.z);
      distance+=moved;
      stall=moved<.004?stall+1:0;
      longestStall=Math.max(longestStall,stall);
      air=p.fall.grounded?0:air+1;
      longestAir=Math.max(longestAir,air);
      if(tick%18===0||stall===30||tick===1)frames.push({tick,feet:p.position.toArray(),grounded:p.fall.grounded});
      if(stall>=30||p.position.y<-.38)break;
    }
    return {name,offset,route,turns,completed:waypoint===route.length&&p.fall.grounded,
      reachedMouth:turns.length>=route.length-2,longestStall,longestAir,distance,tick,
      last:p.position.toArray(),frames,blockedMouth:wall};
  }finally{host.dispose();}
}
const samples=Object.entries(routes).flatMap(([name,gate])=>[-.42,0,.42].map(offset=>play(name,gate,offset)));
const wall=play('West',routes.West,0,true);
for(const r of [...samples,wall]) console.log(r.name,r.offset,r.reachedMouth,r.completed,r.longestStall,r.longestAir,r.last.map(n=>n.toFixed(3)).join(','));
assert(!wall.reachedMouth&&wall.longestStall===30);
assert.deepEqual(samples.find(r=>r.name==='East'&&r.offset===0),play('East',routes.East,0));
writeFileSync(process.argv[3],JSON.stringify({engine:'0.1.44',clockHz:60,geometrySha256:hash,
  meshes:geometry.length,triangles:geometry.reduce((s,g)=>s+g.triangles.length/3,0),samples,wall})+'\n')
