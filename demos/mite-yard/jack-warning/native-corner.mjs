// Screen shipped Pallet Docks colliders, then run matched native ram replays.
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {readFileSync,writeFileSync,mkdtempSync} from 'node:fs';
import {createRequire} from 'node:module';
import {join} from 'node:path';
import {tmpdir} from 'node:os';
import {pathToFileURL} from 'node:url';
const [root,dep,arg='3',only]=process.argv.slice(2);
if(!root||!dep||only&&!['inside','outside'].includes(only))throw Error('Usage: node native-corner.mjs FABLE_CHECKOUT DEPENDENCY_PROJECT [PAIR_INDEX|-1] [inside|outside]');
const index=Number(arg);
const pin='3afcd880b397e9703e906a7e66b42e8447e59519';
assert.equal(execFileSync('git',['-C',root,'rev-parse','HEAD'],{encoding:'utf8'}).trim(),pin);
const load=createRequire(join(dep,'package.json'));
const pw=await import(pathToFileURL(load.resolve('playwright')).href);
const {default:shell}=await import(pathToFileURL(load.resolve('@sparticuz/chromium')).href);
const chromium=pw.chromium??pw.default.chromium;
const out=mkdtempSync(join(tmpdir(),'jack-world-corner-'));
console.log(out);
const browser=await chromium.launch({executablePath:await shell.executablePath(),headless:true,args:shell.args});
try{
 const result={pin,index};
 for(const setup of index<0?['scan']:only?[only]:['inside','outside']){
  const ctx=await browser.newContext({viewport:{width:402,height:874},deviceScaleFactor:1,hasTouch:true,isMobile:true,serviceWorkers:'block'});
  await ctx.addInitScript({content:readFileSync(join(root,'tools/golden/init.js'),'utf8')});
  const page=await ctx.newPage();
  page.on('pageerror',error=>console.error(error));
  await page.goto(`http://127.0.0.1:${Number(process.env.FABLE_PROBE_PORT??5174)}/?golden&dev&q=medium`,{waitUntil:'domcontentloaded'});
  await page.waitForFunction(()=>window.game?.started&&game.renderer.gl.info.render.frame>0,null,{timeout:90000});
  const {start,candidates}=await page.evaluate(({setup,index})=>{
   const g=game,p=g.player,h=__golden;
   h.freeze();
   g.mobs.manageCamps=()=>{};g.mobs.clear();g.mobs.spawnQueue.length=0;
   const jack=g.mobs.spawn('pallet',{x:33,z:120,level:4,variant:'normal'});
   if(!jack)throw Error('No Jack');
   const pos=(x,y,z)=>p.pos.clone().set(x,y,z);
   const ground=(x,z)=>g.groundY(x,z,40);
   const cast=(mx,mz,px,pz,height,targetHeight=height)=>{
    const my=ground(mx,mz),py=ground(px,pz);
    const o=pos(mx,my+height,mz),d=pos(px,py+targetHeight,pz).sub(o);
    if(height===.7)d.y=0;
    const l=d.length();
    const hit=g.physics.raycast(o,d.multiplyScalar(1/l),l-(height===.7?0:.5));
    return hit?.collider.handle??null;
   };
   const room=(x,z,r)=>{
    const y=ground(x,z);
    for(let k=0;k<8;k++){
     const a=k*Math.PI/4;
     if(g.physics.raycast(pos(x,y+.74,z),pos(Math.sin(a),0,Math.cos(a)),r))return false;
    }
    return true;
   };
   const candidates=[], eye=Math.max(.6,jack.height*.8);
   g.physics.world.forEachCollider(c=>{
    if((c.collisionGroups()>>>16)!==1)return;
    const ce=c.translation(),he=c.halfExtents();
    if(!he||ce.x<15||ce.x>115||ce.z<87||ce.z>245||he.y<.37||he.y>.65||he.x<.36||he.x>.66||he.z<.36||he.z>.66)return;
    const q=c.rotation();
    if(Math.abs(q.x)+Math.abs(q.z)>.02)return;
    const yaw=2*Math.atan2(q.y,q.w);
    for(const axis of [0,1])for(const direction of [-1,1])for(const side of [-1,1]){
     const a=yaw+axis*Math.PI/2, f=[Math.sin(a)*direction,Math.cos(a)*direction], s=[f[1],-f[0]];
     const extent=axis?he.z:he.x;
     const pair=[Math.max(0,extent-.40),extent+.28].map(off=>{
      const x=ce.x+s[0]*off*side,z=ce.z+s[1]*off*side;
      const m=[x+f[0]*4.0,z+f[1]*4.0],p=[x-f[0]*5.1,z-f[1]*5.1];
      return {m,p,top:cast(...m,...p,eye,1.2),low:cast(...m,...p,.7),bearing:Math.atan2(-f[0],-f[1])};
     });
     if(pair[0].low!==c.handle||pair[1].low!==null||pair.some(z=>z.top!==null))continue;
     if(pair.some(({m,p})=>Math.min(m[0],p[0])<18||Math.abs(ground(...m)-ground(...p))>.22||
       !room(...m,1.28)||!room(...p,.65)||
       !room(m[0]-f[0]*.68,m[1]-f[1]*.68,.76)||
       !room(m[0]+f[0]*1.1,m[1]+f[1]*1.1,.95)))continue;
     const score=Math.hypot(ce.x-33,ce.z-113)+Math.abs(he.x-he.z)*10;
     candidates.push({score,center:[ce.x,ce.y,ce.z],half:[he.x,he.y,he.z],handle:c.handle,axis,direction,side,pair});
    }
   });
   candidates.sort((a,b)=>a.score-b.score||a.axis-b.axis||a.side-b.side);
   if(setup==='scan')return {candidates};
   const chosen=candidates[index];
   if(!chosen)throw Error('No shipped matched corner at index '+index);
   const {m,p:pp,bearing}=chosen.pair[setup==='inside'?0:1];
   g.mobs.clear();
   h.seed(0x628d);
   const mob=g.mobs.spawn('pallet',{x:m[0],z:m[1],level:4,variant:'normal'});
   if(!mob)throw Error('Jack setup failed');
   mob.yaw=bearing; // Initial orientation only; no post-start AI overrides.
   g.state.d.level=4;g.state.d.hp=g.state.maxHp;g.state.d.energy=g.state.maxEnergy;
   if(g.state.god)throw Error('God must be off');
   p.teleport(pp[0],ground(...pp)+.12,pp[1],bearing+Math.PI);
   g.cameraRig.snap(bearing,.20);
   g.combat.target=null;g.env.clockRunning=false;g.env.hour=12.5;g.env.forcedHour=12.5;
   document.querySelector('#dev')?.style.setProperty('display','none');
   const base=g.physics.raycast.bind(g.physics),draw=g.renderer.render.bind(g.renderer),sfx=g.sfx.bind(g);
   const began=h.frame;
   const fixture=window.cornerFixture={phase:null,trace:[],collisions:[],sounds:[],chosen};
   g.physics.raycast=(o,d,len,filter,...rest)=>{
    const hit=base(o,d,len,filter,...rest);
    if(hit&&filter===undefined&&mob.state==='active'&&mob.atk?.id==='charge'&&
        Math.abs(o.y-mob.pos.y-.7)<1e-5&&Math.hypot(o.x-mob.pos.x,o.z-mob.pos.z)<1e-5)
     fixture.collisions.push({frame:h.frame-began,candidate:hit.collider.handle===chosen.handle,dist:hit.dist,point:hit.point.toArray()});
    return hit;
   };
   g.sfx=(id,...args)=>{
    if(id==='enemy_crash')fixture.sounds.push(h.frame-began);
    return sfx(id,...args);
   };
   g.renderer.render=(...args)=>{
    if(mob.atk?.id==='charge'&&((mob.state==='windup'&&mob.locked&&!fixture.lock)||(mob.state==='recover'&&!fixture.recovery)))draw(...args);
   };
   h.post=()=>{
    const r={frame:h.frame-began,state:mob.state,attack:mob.atk?.id??null,hp:g.state.d.hp,
      m:mob.pos.toArray(),p:p.pos.toArray(),rolling:p.rolling,god:g.state.god};
    fixture.trace.push(r);
    const sight=(o,w,trim)=>{
     const dir=w.clone().sub(o),len=dir.length();
     return base(o,dir.multiplyScalar(1/len),Math.max(.05,len-trim))?.collider.handle??null;
    };
    if(mob.state==='windup'&&mob.atk?.id==='charge'&&mob.locked&&!fixture.lock){
     const o=mob.pos.clone();o.y+=mob.lift+mob.fly+Math.max(.6,mob.height*.8);
     const w=p.pos.clone(); w.y+=1.2;
     const top=sight(o,w,.5);
     const cam=g.camera.position;
     const camHits=Object.fromEntries(['head','core','muzzle'].map(k=>[k,sight(cam,mob.rig.sockets[k].getWorldPosition(pos(0,0,0)),.06)!==null]));
     o.copy(mob.pos);o.y+=.7;w.copy(o).addScaledVector(pos(Math.sin(mob.lockYaw),0,Math.cos(mob.lockYaw)),14);
     const direction=w.clone().sub(o).normalize();
     const lowHit=base(o,direction,14);
     const low=lowHit?.collider.handle??null, lowDistance=lowHit?.dist??null;
     // Do not infer protection from a static setup or the camera's ray.
     // This one-frame candidate samples the native locked heading at ram height.
     fixture.renderWarning=(clip)=>{
      const mesh=mob.tele.mesh, old=mesh.position.clone(),sz=mesh.scale.z,yaw=mesh.rotation.y;
      const stock=sz*2;
      const length=clip&&low===chosen.handle?Math.min(stock,Math.max(.2,lowDistance)):stock;
      if(length<stock){
       mesh.scale.z=length/2;mesh.rotation.y=mob.lockYaw;
       mesh.position.x=mob.pos.x+direction.x*length/2;mesh.position.z=mob.pos.z+direction.z*length/2;
       g.fx.marks.update(0);
      }
      draw(g.scene,g.camera,0);
      mesh.position.copy(old);mesh.scale.z=sz;mesh.rotation.y=yaw;
      if(length<stock)g.fx.marks.update(0);
      return {length,width:mesh.scale.x*2,t:mob.tele.u.uT.value,frame:h.frame,
       rot:g.camera.quaternion.toArray(),camera:g.camera.position.toArray(),hp:g.state.d.hp};
     };
     fixture.lock={...r,topBlocked:top!==null,lowBlocked:low!==null,lowIsCandidate:low===chosen.handle,lowDistance,camHits};
     fixture.phase='windup';h.freeze();
    }else if(mob.state==='recover'&&mob.atk?.id==='charge'&&fixture.lock&&!fixture.recovery){
     fixture.recovery={...r,fired:mob.fired};fixture.phase='recover';h.freeze();
    }else if(r.frame>430){fixture.phase='timeout';h.freeze();}
   };
   const start={hp:g.state.d.hp,enemyHp:mob.hp,eye,chosen,matchedCandidates:candidates.length};
   h.thaw();
   return {start};
  },{setup,index});
  if(setup==='scan'){
   console.log(JSON.stringify(candidates.slice(0,14)));
   await ctx.close();continue;
  }
  for(const phase of ['windup','recover']){
   await page.waitForFunction(()=>['windup','recover','timeout'].includes(window.cornerFixture?.phase),null,{timeout:90000,polling:100});
   const reached=await page.evaluate(()=>cornerFixture.phase);
   if(reached==='timeout')break;
   assert.equal(reached,phase);
   await page.screenshot({path:join(out,setup+'-'+phase+'.jpg'),type:'jpeg',quality:91});
   if(phase==='windup'){
    const pair=[];
    for(const clip of [false,true]){
     pair.push(await page.evaluate(clip=>cornerFixture.renderWarning(clip),clip));
     await page.screenshot({path:join(out,setup+(clip?'-clipped.jpg':'-stock.jpg')),type:'jpeg',quality:91});
    }
    const {length:first,...a}=pair[0],{length:second,...b}=pair[1];
    assert.deepEqual(a,b);
    await page.evaluate(pair=>{cornerFixture.warning=pair;cornerFixture.phase=null;__golden.thaw();},pair);
   }
  }
  result[setup]={start,...await page.evaluate(()=>cornerFixture)};
  writeFileSync(join(out,'proof.json'),JSON.stringify(result,null,2)+'\n');
  const {lock,recovery,sounds,collisions}=result[setup];
  console.log(JSON.stringify({setup,lock,recovery,sounds,collisions,center:start.chosen.center,pair:start.chosen.pair}));
  await ctx.close();
 }
 if(index>=0&&!only){
  for(const r of [result.inside,result.outside]){
   assert(r.lock&&r.recovery);
   assert(!r.lock.topBlocked);
   assert(r.trace.every(t=>!t.god&&!t.rolling));
  }
  assert(result.inside.lock.lowIsCandidate);
  assert(result.inside.collisions.some(hit=>hit.candidate));
  assert.equal(result.inside.sounds.length,1);
  assert.equal(result.inside.recovery.hp,result.inside.start.hp);
  assert(!result.outside.lock.lowIsCandidate);
  assert(result.inside.warning[1].length<result.inside.warning[0].length);
  assert.equal(result.outside.warning[1].length,result.outside.warning[0].length);
  assert(result.outside.recovery.hp<result.outside.start.hp);
 }
}finally{await browser.close();}
