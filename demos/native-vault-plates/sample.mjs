import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFileSync,writeFileSync} from 'node:fs';
import {createRequire} from 'node:module';
import {dirname,join,resolve} from 'node:path';
import {pathToFileURL} from 'node:url';

const req=createRequire(process.env.WSC_NODE_PROJECT?
  join(resolve(process.env.WSC_NODE_PROJECT),'package.json'):import.meta.url);
const pkg=req.resolve('@wildshard/engine/package.json');
assert.equal(JSON.parse(readFileSync(pkg)).version,'0.1.44');
const at=p=>import(pathToFileURL(join(dirname(pkg),p)).href);
await at('scripts/sim-node-loader.mjs');
const {SimHost}=await at('src/server/engine/sim.ts');
const {SIM_API_VERSION}=await at('src/shared/engine/sim/apiVersion.ts');
const {loadRapier}=await at('src/shared/engine/physics/rapier.ts');
const {groups}=await at('src/shared/engine/physics/groups.ts');
const {plateOverlap}=await at('src/shared/engine/world/interact/barrel.ts');
const R=await loadRapier(readFileSync(join(dirname(req.resolve('@dimforge/rapier3d-simd/package.json')),'rapier_wasm3d_bg.wasm')));
const raw=readFileSync(process.argv[2]);
const geo=JSON.parse(raw);
const floor=.112, height=.8635/2;
const padZ=-2.35, Bx=2.2, Ax=-2.2;
const dimensions=[.558,height,.5192];
const maxY=p=>Math.max(...p.v.filter((_,i)=>i%3===1));
const levels=[maxY(geo.plates['Plate A'][1]),maxY(geo.plates['Plate B'][1])];
assert.deepEqual(levels,[.25825,.28325]);
const rect=(x,y,z)=>({x,y,z});
const round=n=>+n.toFixed(5);
function run(add,offset,push,lockYaw=false,alignBias=.29){
  const density=140;
  const host=new SimHost({version:SIM_API_VERSION,id:'vault-room-one-push-bench',seed:25,
    ground:{size:500,height:floor},player:{at:{x:-.25,y:floor+.05,z:2.32},yaw:0,speed:4.3},
    entities:[],quests:[],weapon:{id:'vault-calibration-disabled',damage:0}},{rapier:R,ground:false});
  const player=host.players.get('actor.player'),w=host.physics.world;
  const spawn=(x,y,z)=>{
    const body=w.createRigidBody(R.RigidBodyDesc.dynamic().setTranslation(x,y+height+.003,z).setCcdEnabled(true).setAngularDamping(6).enabledRotations(false,!lockYaw,false));
    body.shape=w.createCollider(R.ColliderDesc.cuboid(...dimensions).setCollisionGroups(groups('ITEM')).setDensity(density).setFriction(.62),body);
    return body;
  };
  try{
    const slab=(x,z,hx,hz)=>w.createCollider(R.ColliderDesc.cuboid(hx,.15,hz).setTranslation(x,floor-.15,z)
      .setCollisionGroups(groups('WORLD')).setFriction(.62));
    const loadFaces=[];
    const shared=slab(0,-.2,5,6.8);
    if(add){
      loadFaces.push(shared,shared);
    } else {
      for(const [i,parts] of Object.values(geo.plates).entries())for(const part of parts){
        const coll=w.createCollider(R.ColliderDesc.trimesh(new Float32Array(part.v),new Uint32Array(part.t))
          .setCollisionGroups(groups('WORLD')).setFriction(.62));
        if(part.name==='Moving_Tread')loadFaces[i]=coll;
      }
    }
    const support=add?[floor,floor]:levels;
    const a=spawn(Ax,support[0],padZ), b=spawn(1.25,floor,2.32);
    const bears=(shape,face)=>{
      let found=false;
      w.contactPair(shape,face,m=>{
        for(let i=0;i<m.numSolverContacts();i++)if(m.solverContactDist(i)<.004)found=true;
      });
      return found;
    };
    const occupied=(x,y)=>plateOverlap(host.physics,rect(x,y,padZ),0,1.77,{sees:['ITEM']});
    const doorZ=-5.8;
    const door=w.createCollider(R.ColliderDesc.cuboid(1.12,1.18,.125)
      .setTranslation(0,floor+1.18,doorZ).setCollisionGroups(groups('WORLD')));
    const fit=(body,cx,face)=>{
      const p=body.translation(),q=body.rotation();
      const yaw=2*Math.atan2(q.y,q.w);
      const c=Math.abs(Math.cos(yaw)),d=Math.abs(Math.sin(yaw));
      const clearance=Math.min(.885-Math.abs(p.x-cx)-c*dimensions[0]-d*dimensions[2],
        .885-Math.abs(p.z-padZ)-d*dimensions[0]-c*dimensions[2]);
      const contact=bears(body.shape,face);
      // On the trimmed original mesh Rapier can report an empty solver manifold when sleeping.
      // Retain the original mask and tread height together rather than trusting a proximity hit alone.
      const y=support[cx===Ax?0:1], bottom=p.y-height;
      const loaded=add?contact:Math.abs(bottom-y)<.006&&occupied(cx,y);
      return {clearance:round(clearance),bottom:round(bottom),held:clearance>.008&&loaded&&
        Math.hypot(body.linvel().x,body.linvel().z)<.15};
    };
    const fits=()=>[fit(a,Ax,loadFaces[0]),fit(b,Bx,loadFaces[1])];
    let tickNo=0;
    const frames=[];
    const tick=(moveX=0,moveZ=0)=>{
      host.step(new Map([[player.id,{moveX,moveZ,yaw:Math.atan2(-moveX,-moveZ)}]]));tickNo++;
      // Prototype ownership rule, not shipped QuestFlagGates. Don't close on an actor in the aperture.
      const canClose=Math.abs(player.position.x)>1.48||Math.abs(player.position.z-doorZ)>.50;
      const enabled=!fits().every(p=>p.held)&&(door.isEnabled()||canClose);
      if(door.isEnabled()!==enabled)door.setEnabled(enabled);
      if(tickNo%6===0){
        const c=b.translation(),rot=b.rotation();
        frames.push({n:tickNo,player:player.position.toArray().map(round),crate:[c.x,c.y,c.z].map(round),
          rotation:[rot.x,rot.y,rot.z,rot.w].map(round),held:fits().map(p=>p.held)});
      }
    };
    const idle=n=>{for(let i=0;i<n;i++)tick()};
    const walk=(x,z)=>{
      for(let i=0;i<420;i++){
        const dx=x-player.position.x,dz=z-player.position.z,d=Math.hypot(dx,dz);
        if(d<.035)return;
        const s=Math.min(1,d*10);
        tick(dx/d*s,dz/d*s);
      }
      throw Error('waypoint blocked '+JSON.stringify({x,z,pos:player.position.toArray()}));
    };
    const status=(name)=>{
      const p=b.translation(),q=b.rotation(),within=fits(),held=within.map(p=>p.held);
      const ray=w.castRay(new R.Ray(rect(0,1.05,doorZ+1),rect(0,0,-1)),2,true,
        undefined,undefined,undefined,undefined,c=>c.handle===door.handle);
      const overlap=[occupied(Ax,support[0]),occupied(Bx,support[1])];
      return {name,tickNo,crate:[p.x,p.y,p.z].map(round),rotation:[q.x,q.y,q.z,q.w].map(round),held,overlap,within,both:held.every(Boolean),doorBlocked:ray!==null,
        bearing:[bears(a.shape,loadFaces[0]),bears(b.shape,loadFaces[1])],feet:player.position.toArray().map(round),aFixed:Math.hypot(a.translation().x-Ax,a.translation().z-padZ)<.015};
    };
    idle(40);
    const initial=status('initial');
    {
      const alignTarget=Bx+offset+alignBias;
      const stopX=Bx+offset+(alignBias===.29?.275:alignBias-.015);
      for(let i=0;i<220&&b.translation().x<stopX;i++)
        tick(Math.max(.18,Math.min(.58,(alignTarget-b.translation().x)*2)),0);
      idle(55);
      const c=b.translation();
      walk(player.position.x,3.95);
      walk(c.x,3.95);
    }
    const aligned=status('aligned');
    for(let i=0;i<1200&&b.translation().z>padZ+.225;i++){
      if(player.position.z<b.translation().z-.1)break; // Don't walk past a wedged crate.
      tick(0,-push);
    }
    const release=status('input released');
    idle(110);
    const settled=status('settled');
    let crossed=null,relocked=null;
    if(settled.both&&add){
      walk(0,Math.max(player.position.z,-.5));
      walk(0,-6.55);
      crossed=status('ordinary walk through open gate');
      // Use the aisle beside the tread to circle behind B, then push it back toward the entry.
      walk(2.55,-6.55);walk(b.translation().x,-3.94);
      for(let i=0;i<960&&b.translation().z<padZ+1.38;i++)tick(0,push);
      idle(85);
      relocked=status('crate removed by ordinary walk');
    }

    return {add,offset,push,...(alignBias!==.29||lockYaw?{lockYaw,alignBias}:{}),density,initial,aligned,release,settled,crossed,relocked,frames};
  }finally{host.dispose()}
}
if(process.argv[5]==='--lock-yaw'){
  const offsets=[-.1,0,.1], inputs=[.42,.67,.8,1];
  const scenarios=[
    {name:'original yaw and lateral compensation',lock:false,bias:.29,count:3},
    {name:'fixed yaw with old lateral compensation',lock:true,bias:.29,count:8},
    {name:'free yaw with centered alignment',lock:false,bias:0,count:1},
    {name:'fixed yaw with centered alignment',lock:true,bias:0,count:12},
  ];
  const sets=scenarios.map(({name,lock,bias,count})=>{
    const runs=offsets.flatMap(offset=>inputs.map(push=>run(true,offset,push,lock,bias)));
    const successes=runs.filter(a=>a.settled.both);
    assert.equal(successes.length,count,name);
    for(const a of runs){
      const opens=a.settled.both;
      assert.deepEqual(a.initial.held,[true,false]);
      assert(a.initial.doorBlocked&&a.settled.aFixed);
      assert.equal(a.settled.doorBlocked,!opens);
      if(opens){
        assert(a.crossed.feet[2]<-6.4&&!a.crossed.doorBlocked);
        assert.deepEqual(a.relocked.held,[true,false]);
        assert(a.relocked.doorBlocked);
      }else assert(a.crossed===null&&a.relocked===null);
      if(lock)assert.deepEqual(a.settled.rotation,[0,0,0,1]);
    }
    return {name,lock,bias,runs,successes:successes.length};
  });
  const candidate=sets.at(-1);
  assert(candidate.runs.every(a=>a.settled.within[1].clearance>.18));
  const full=s=>s.runs.find(a=>a.offset===0&&a.push===1);
  assert.deepEqual(run(true,0,1,true,0),full(candidate));
  const compact=a=>({offset:a.offset,push:a.push,alignedCrate:a.aligned.crate,settledCrate:a.settled.crate,
    yawQuaternion:a.settled.rotation,clearanceM:a.settled.within[1].clearance,
    open:a.settled.both,crossedZ:a.crossed?.feet[2]??null,relocked:a.relocked?.doorBlocked??false});
  const receipt={scope:'Isolated stock player, flush plate floor, proxy door; no install, human or phone test.',
    engine:'0.1.44',plateGeometrySha256:createHash('sha256').update(raw).digest('hex'),floor,dimensions,
    cases:sets.map(({runs,...s})=>({...s,runs:runs.map(compact)})),repeatReplayMatched:true};
  writeFileSync(process.argv[3],JSON.stringify(receipt,null,2)+'\n');
  writeFileSync(process.argv[4],JSON.stringify([full(sets[0]),full(candidate)])+'\n');
  console.table(sets.map(({name,successes,runs})=>({name,passes:successes,total:runs.length})));
  process.exit(0);
}
const configs=[false,true].flatMap(add=>[-.1,0,.1].flatMap(offset=>[.42,.67,.8].map(push=>[add,offset,push])));
const attempts=configs.map(args=>run(...args));
for(const a of attempts){
  const opens=a.add&&a.push===.42;
  assert.deepEqual(a.initial.held,[true,false]); assert.equal(a.initial.doorBlocked,true);
  assert.equal(a.settled.aFixed,true);
  assert.deepEqual(a.settled.held,[true,opens],JSON.stringify(a.settled));
  assert.equal(a.settled.doorBlocked,!opens);
  if(opens){
    assert.ok(a.crossed.feet[2]<-6.4&&!a.crossed.doorBlocked);
    assert.deepEqual(a.relocked.held,[true,false]);
    assert.equal(a.relocked.doorBlocked,true);
  }
}
const summary=attempts.map(({frames,...a})=>a);
const replay=attempts.filter(a=>a.offset===0&&a.push===.42);
writeFileSync(process.argv[3],JSON.stringify({engine:'0.1.44',plateGeometrySha256:createHash('sha256').update(raw).digest('hex'),
  levels,floor,dimensions,summary},null,2)+'\n');
if(process.argv[4])writeFileSync(process.argv[4],JSON.stringify(replay)+'\n');
