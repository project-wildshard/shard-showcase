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
const {tagCollider}=await at('src/shared/engine/physics/surface.ts');
const {installDeclaredRiding}=await at('src/server/game/shardfile/declaredRiding.ts');
const R=await loadRapier(readFileSync(join(dirname(req.resolve('@dimforge/rapier3d-simd/package.json')),'rapier_wasm3d_bg.wasm')));
const raw=readFileSync(process.argv[2]), parts=JSON.parse(raw);
const hash=createHash('sha256').update(raw).digest('hex');
const spec={kind:'horse', label:'Calibration horse', variant:'stock', rarity:'common', hp:100, aggressive:false,
  dims:{bodyY:1.44, bodyHalfLen:.78, bodyRadius:.38, headRadius:.22, legLen:1.02,
        feet:[[-.26,.62],[.26,.62],[-.26,-.62],[.26,-.62]], halfWidth:.36},
  mods:{speed:1,chargeDist:1,damageTaken:1,chargeDamage:0,relentless:false}};
const gaits={walk:2.8,trot:5.6,canter:8.5,gallop:13};
const center=-125, yaw=-Math.PI/2;
const rail=parts.filter(p=>p.name.startsWith('Jump rail stripe')||p.name.startsWith('Pole end cap'));
assert.equal(parts.length,32);
assert.equal(rail.length,12);
const crest=Math.max(...rail.flatMap(p=>p.v.filter((_,i)=>i%3===1)));
const railXs=rail.flatMap(p=>p.v.filter((_,i)=>i%3===0));
const xSpan=[Math.min(...railXs)-1.2,Math.max(...railXs)+1.2]; // full 2.4 m stock body
function minimumOverSpan(frames){
  const y=frames.filter(f=>f.x>=xSpan[0]&&f.x<=xSpan[1]).map(f=>f.y);
  for(const x of xSpan) for(let i=1;i<frames.length;i++){
    const a=frames[i-1],b=frames[i];
    if(a.x>x&&b.x<x)y.push(a.y+(b.y-a.y)*(x-a.x)/(b.x-a.x));
  }
  return y.length?Math.min(...y):null;
}
assert.ok(Math.abs(crest-1.198)<1e-6);
assert.equal(hash,'ba1e9e88fe9c210f14aea7ed0f6f9a5fc887d0f8d9b5455baf19803c7e7a635d');
const apron=JSON.parse(readFileSync(process.argv[3]));
const measured=apron.worldHalfExtent, centerAt=apron.worldCenter;
function run({collision='mesh',speed='gallop',press=null,start=-85,offset=0}={}){
  const z=-148+offset;
  const at={x:start,y:.025,z};
  const sim=new SimHost({version:SIM_API_VERSION,id:'w10b-rail-bench',seed:25,
    ground:{size:500,height:.025},player:{at:{...at,z:z+1},yaw,speed:4.3},
    entities:[{id:'horse.rail',spec,seed:5,scale:1,at,yaw}],quests:[],
    weapon:{id:'disabled-calibration-strike',damage:0}}, {rapier:R});
  try{
    const horse=sim.entities.get('horse.rail');
    horse.species='w10b-calibration-horse';
    const rider=sim.players.get('actor.player');
    const riding=installDeclaredRiding(sim,{rows:{species:[{id:horse.species,mount:{gaits}}]}});
    assert.equal(riding.mount(rider.id,horse.entityId),true);
    assert.equal(rider.ridden,horse.entityId);
    if(collision!=='none'&&sim.physics!==null) {
      for(const p of parts){
        const c=sim.physics.world.createCollider(R.ColliderDesc.trimesh(new Float32Array(p.v),new Uint32Array(p.t)).setCollisionGroups(groups('WORLD')));
        tagCollider(c,'wood',p.name);
      }
      if(collision==='apron'){
        const c=sim.physics.world.createCollider(R.ColliderDesc.cuboid(...measured).setTranslation(...centerAt).setCollisionGroups(groups('WORLD')));
        tagCollider(c,'wood','w10b-apron-candidate');
      }
    }
    assert.ok(sim.physics);
    for(let i=0;i<24;i++)sim.step();
    const frames=[];let pressed=false, lastX=start;
    for(let tick=0;tick<650;tick++){
      const jump=!pressed&&press!==null&&horse.position.x<=center+press;
      if(jump)pressed=true;
      sim.step(new Map([[rider.id,{commandVersion:1,moveX:0,moveZ:0,yaw,sprint:speed==='gallop',
         ...(jump?{jump:true}:{}),steer:{keyX:0,keyY:0,stickX:0,stickY:speed==='walk'?.38:1}}]]));
      const [x,y,pz]=horse.position.toArray();
      const rollingSpeed=(lastX-x)*60;
      lastX=x;
      frames.push({tick, x,y,z:pz,v:rollingSpeed,jump,hp:horse.hp});
      if(x<-137&&y<.06)break;
    }
    assert.equal(rider.ridden,horse.entityId);
    return {collision,speed,press,start,offset,frames};
  }finally{sim.dispose();}
}
const summary=r=>{
 const {frames,...params}=r;
 const best=frames.reduce((a,b)=>a.y>b.y?a:b);
 const air=frames.filter(a=>a.y>.07);
 const close=frames.find(f=>f.x<=center);
 const last=frames.at(-1);
 return {...params,peakY:best.y, takeoffX:air[0]?.x??null,touchdownX:air.at(-1)?.x??null,
   centerPoint:close??null,spanMinY:minimumOverSpan(frames),last,
   railClear:!!close&&last.x<-137&&best.y>.4};
};

const auto=[], manual=[], slow=[], replay=[];
const round=x=>+x.toFixed(5);
const shape=(r)=>{
  const s=summary(r);
  return {...s,peakY:round(s.peakY),crestGap: s.spanMinY===null?null:round(s.spanMinY-crest),
    maxSpeed:round(Math.max(...r.frames.map(f=>f.v)))};
};
for(const start of [-86,-85,-84])for(const offset of [-1.1,-.55,0,.55,1.1]){
 const raw=run({collision:'mesh',start,offset}), add=run({collision:'apron',start,offset});
 const same=run({collision:'none',start,offset});
 const a=shape(add), b=shape(raw), c=shape(same);
 assert.ok(b.peakY<.04 && b.last.x<-137 && c.peakY<.04);
 assert.ok(a.railClear&&a.peakY>1.42&&a.crestGap>.025&&a.last.hp===100, JSON.stringify(a));
 assert.ok(a.maxSpeed>=12.9);
 auto.push([a,b]);
 if(start===-85&&offset===0)replay.push({id:'auto',frames:add.frames},{id:'under',frames:raw.frames});
 for(const press of [5.4,4.8,4.1]){
   const r=run({collision:'mesh',start,offset,press});
   manual.push(shape(r));
   if(start===-85&&offset===0&&press===4.8)replay.push({id:'manual',frames:r.frames});
 }
}
for(const offset of [-.7,0,.7]){
 const a=run({collision:'apron',speed:'walk',start:-113,offset});
 const b=run({collision:'mesh',speed:'walk',start:-113,offset});
 const before=shape(b), after=shape(a);
 assert.ok(before.last.x<-130&&before.peakY<.04);
 assert.ok(after.last.x>-124.9&&after.peakY<.07&&after.last.hp===100);
 slow.push([after,before]);
 if(offset===0)replay.push({id:'walk-stop',frames:a.frames});
}
const proof={engine:'0.1.44',gaits,donorGeometrySha256:hash,partCount:parts.length,crest:round(crest),xSpan:xSpan.map(round),apron,
  minimumAutoGapM:Math.min(...auto.map(([a])=>a.crestGap)),
  manualConservativeClears:manual.filter(a=>a.railClear&&a.crestGap>=0).length,
  auto,manual,slow};
writeFileSync(process.argv[4],JSON.stringify(proof,null,2)+'\n');
writeFileSync(process.argv[5],JSON.stringify(replay)+'\n');
console.log(JSON.stringify({auto:auto.length,minimumAutoGapM:proof.minimumAutoGapM,manual:manual.length,
  manualConservativeClears:proof.manualConservativeClears,slow:slow.length}));
