import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFileSync,writeFileSync} from 'node:fs';
import {createRequire} from 'node:module';
import {dirname,join,resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
const req=createRequire(process.env.WSC_NODE_PROJECT
  ? join(resolve(process.env.WSC_NODE_PROJECT),'package.json') : import.meta.url);
const packagePath=req.resolve('@wildshard/engine/package.json');
assert.equal(JSON.parse(readFileSync(packagePath)).version,'0.1.44');
const root=dirname(packagePath), at=p=>import(pathToFileURL(join(root,p)).href);
await at('scripts/sim-node-loader.mjs');
const {SimHost}=await at('src/server/engine/sim.ts');
const {SIM_API_VERSION}=await at('src/shared/engine/sim/apiVersion.ts');
const {loadRapier}=await at('src/shared/engine/physics/rapier.ts');
const {groups}=await at('src/shared/engine/physics/groups.ts');
const {installDeclaredRiding}=await at('src/server/game/shardfile/declaredRiding.ts');
const R=await loadRapier(readFileSync(join(dirname(req.resolve('@dimforge/rapier3d-simd/package.json')),'rapier_wasm3d_bg.wasm')));
const spec={kind:'horse', label:'Calibration horse', variant:'stock', rarity:'common', hp:100, aggressive:false,
  dims:{bodyY:1.44, bodyHalfLen:.78, bodyRadius:.38, headRadius:.22, legLen:1.02,
        feet:[[-.26,.62],[.26,.62],[-.26,-.62],[.26,-.62]], halfWidth:.36},
  mods:{speed:1,chargeDist:1,damageTaken:1,chargeDamage:0,relentless:false}};
const gaits={walk:2.8,trot:5.6,canter:8.5,gallop:13};
const raw=readFileSync(new URL('../../project/layouts/w10b-riding-course-study.json',import.meta.url));
const hash=createHash('sha256').update(raw).digest('hex');
assert.equal(hash,'2e5470d81f6a525194da2c143720c5d245cfb871dcc609a46e747ae2403c868f');
const art=JSON.parse(raw), RADIUS=art.oval.centerline_radius_m, half=art.oval.half_straight_m;
const [cx,bz]=art.oval.center_blender_xy_m, cz=-bz, left=cx-half, right=cx+half;
const [lineX,lineBz]=art.timer.gantry_blender_xy_m, lineZ=-lineBz;
const arc=Math.PI*RADIUS, lap=4*half+2*arc;
assert(Math.abs(lap-art.oval.centreline_m)<.001);
const startStraight=lineX-left, home=right-lineX, hz=60, look=9.7;
const clamp=(v,lo,hi)=>Math.max(lo,Math.min(hi,v));
const wrap=(v,m)=>((v%m)+m)%m;
const guide=s=>{
  s=wrap(s,lap);
  if(s<startStraight)return [lineX-s,cz+RADIUS];
  s-=startStraight;
  if(s<arc)return [left-RADIUS*Math.sin(s/RADIUS),cz+RADIUS*Math.cos(s/RADIUS)];
  s-=arc;
  if(s<2*half)return [left+s,cz-RADIUS];
  s-=2*half;
  if(s<arc)return [right+RADIUS*Math.sin(s/RADIUS),cz-RADIUS*Math.cos(s/RADIUS)];
  s-=arc;
  assert(s<=home+1e-7);
  return [right-s,cz+RADIUS];
};
const distance=(p,x,z)=>Math.hypot(p[0]-x,p[1]-z);
const nearest=(x,z,min,max,step)=>{
  let best=Infinity, where=min;
  for(let s=min;s<=max+1e-8;s+=step){const d=distance(guide(s),x,z);if(d<best){best=d;where=s}}
  return {d:best,s:where};
};
const gate=(id,x,z)=>{
  const {s}=nearest(x,z,0,lap,.10),a=guide(s-.2), b=guide(s+.2),mag=distance(a,...b);
  return {id,at:[x,z],s,tangent:[(b[0]-a[0])/mag,(b[1]-a[1])/mag]};
};
const rings=art.rings.placements.map(({number,origin_blender_m:[x,z]})=>gate(number,x,-z)).sort((a,b)=>a.s-b.s);
assert.deepEqual(rings.map(x=>x.id),[2,1,8,7,6,5,4,3]);
const line={id:'gantry', at:[lineX,lineZ],tangent:[-1,0]};
function crossing(g,a,b){
  if(!a)return null;
  const [x,z]=g.at,[dx,dz]=g.tangent;
  const dot=p=>(p.x-x)*dx+(p.z-z)*dz;
  const u=dot(a), v=dot(b);
  if(!(u<0&&v>=0))return null;
  const f=-u/(v-u), x0=a.x+(b.x-a.x)*f, z0=a.z+(b.z-a.z)*f;
  const lateral=(z0-z)*dx-(x0-x)*dz;
  return {id:g.id, tick:a.tick+(b.tick-a.tick)*f,lateral,x:x0,z:z0};
}
const sec=t=>+(t/hz).toFixed(3);
function score(trace){
  let begin=null,end=null,index=0;
  const events=[];
  for(let i=1;i<trace.length;i++){
    const [a,b]=[trace[i-1],trace[i]];
    const gantry=crossing(line,a,b);
    if(begin===null){
      if(gantry&&Math.abs(gantry.lateral)<=6)begin=gantry;
      continue;
    }
    if(gantry&&Math.abs(gantry.lateral)<=6){
      if(index===rings.length){end=gantry;break}
      return null; // cutting straight back to the finish doesn't count as a lap
    }
    const g=rings[index];
    if(!g)continue;
    const c=crossing(g,a,b);
    if(c&&Math.abs(c.lateral)<=6){index++;events.push({...c,hit:Math.abs(c.lateral)<=2});}
  }
  if(!begin||!end)return null;
  const misses=events.filter(e=>!e.hit).map(e=>e.id);
  return {events,startTick:begin.tick,finishTick:end.tick,elapsed:sec(end.tick-begin.tick),
    misses,penalty:misses.length*5,total:sec(end.tick-begin.tick+hz*5*misses.length)};
}
export function drive(offset,skip,options={}){
  const yaw=-Math.PI/2, p={x:lineX+10,y:.025,z:lineZ+offset};
  const sim=new SimHost({version:SIM_API_VERSION,id:'w10b-lap-bench',seed:27,
    ground:{size:500,height:.025},player:{at:{...p,z:p.z+1},yaw,speed:4.3},
    entities:[{id:'horse.lap',spec,seed:5,scale:1,at:p,yaw}],quests:[],
    weapon:{id:'disabled-calibration-strike',damage:0}}, {rapier:R,ground:false});
  try{
    sim.physics.world.createCollider(R.ColliderDesc.cuboid(250,1,250).setTranslation(0,-.975,0).setCollisionGroups(groups('WORLD')));
    options.install?.(sim,R,groups);
    const h=sim.entities.get('horse.lap'), r=sim.players.get('actor.player');
    h.species='w10b-calibration-horse';
    const ride=installDeclaredRiding(sim,{rows:{species:[{id:h.species,mount:{gaits}}]}});
    assert(ride.mount(r.id,h.entityId));
    const trace=[];
    let s=-10, maxError=0;
    for(let tick=0;tick<4400;tick++){
      const [x,y,z]=h.position.toArray();
      const close=nearest(x,z,s-1.4,s+2.0,.10);
      s=close.s;
      if(s>=0&&s<lap)maxError=Math.max(maxError,close.d);
      const targetS=s+look, target=guide(targetS);
      if(skip && targetS>48&&targetS<82){
        const t=(targetS-48)/34;
        target[1]+=3.4*Math.sin(Math.PI*t)**2;
      }
      const angle=Math.atan2(target[0]-x,target[1]-z);
      const delta=Math.atan2(Math.sin(angle-h.yaw),Math.cos(angle-h.yaw));
      const steer=clamp(-4.5*delta,-1,1);
      assert(r.ridden===h.entityId);
      trace.push({tick,x,y,z,s,...(options.withHp?{hp:h.hp}:{})});
      if(s>lap+1.6)break;
      sim.step(new Map([[r.id,{commandVersion:1,moveX:0,moveZ:0,yaw:h.yaw,sprint:true,
        steer:{keyX:0,keyY:0,stickX:steer,stickY:1}}]]));
    }
    return {offset,skip,trace,result:score(trace),maxError};
  } finally {sim.dispose()}
}
if(process.argv[1] && pathToFileURL(resolve(process.argv[1])).href===import.meta.url){
const runs=[];
for(const off of [-.5,0,.5])for(const skip of [false,true])runs.push(drive(off,skip));
console.table(runs.map(r=>({offset:r.offset,skip:r.skip,lap:r.trace.at(-1).s,maxError:r.maxError,
  finish:r.result?.elapsed,penalty:r.result?.penalty,missed:r.result?.misses.join(',')})));
const [proof,trace]=process.argv.slice(2);
assert(proof&&trace);
for(const r of runs){
  assert(r.result && r.result.elapsed>35 && r.result.elapsed<64, JSON.stringify(r.result));
  assert.deepEqual(r.result.misses,r.skip?[1]:[]);
  assert(r.maxError<5);
  assert(r.trace.every(f=>Number.isFinite(f.y)&&Math.abs(f.y-.025)<.001));
  assert.equal(+(r.result.total-r.result.elapsed).toFixed(3),r.skip?5:0);
}
assert.equal(score(runs[2].trace.slice(0,500)),null);
assert.equal(score([...runs[2].trace.slice(0,200),...runs[2].trace.slice(-40)]),null);
assert.equal(score([...runs[2].trace].reverse()),null);
assert.deepEqual(drive(0,false),runs[2]);
const compact=r=>({offset:r.offset,skip:r.skip,maxError:+r.maxError.toFixed(3),yRange:[Math.min(...r.trace.map(f=>f.y)),Math.max(...r.trace.map(f=>f.y))],result:r.result});
writeFileSync(proof,JSON.stringify({engine:'0.1.44',hz,layoutSHA256:hash,lap,halfWidth:2,gantry:line,rings,runs:runs.map(compact)},null,2)+'\n');
writeFileSync(trace,JSON.stringify({gantry:line,rings,clean:runs[2],bypass:runs[3]})+'\n');
}
