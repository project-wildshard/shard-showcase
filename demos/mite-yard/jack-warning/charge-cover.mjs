// Read-only control/cover replay in Fable's native Pallet Docks.
// Run with a loopback server rooted at the built checkout's dist directory.
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {readFileSync,writeFileSync,mkdtempSync} from 'node:fs';
import {createRequire} from 'node:module';
import {join} from 'node:path';
import {tmpdir} from 'node:os';
import {pathToFileURL} from 'node:url';

const pin='3afcd880b397e9703e906a7e66b42e8447e59519';
const [root,dep,mode='cover']=process.argv.slice(2);
if(!['cover','riposte'].includes(mode))throw Error('Expected cover or riposte');
if(!root||!dep)throw Error('Usage: node charge-cover.mjs FABLE_CHECKOUT DEPENDENCY_PROJECT [cover|riposte]');
assert.equal(execFileSync('git',['-C',root,'rev-parse','HEAD'],{encoding:'utf8'}).trim(),pin);
const load=createRequire(join(dep,'package.json'));
const pw=await import(pathToFileURL(load.resolve('playwright')).href);
const {default:shell}=await import(pathToFileURL(load.resolve('@sparticuz/chromium')).href);
const chromium=pw.chromium??pw.default.chromium;
const out=mkdtempSync(join(tmpdir(),'jack-cover-'));
console.log('Private scratch:',out);
const browser=await chromium.launch({executablePath:await shell.executablePath(),headless:true,args:shell.args});
try {
 const receipt={pin};
 for(const kind of mode==='riposte'?['early','late']:['open','cover']){
  const ctx=await browser.newContext({viewport:{width:402,height:874},deviceScaleFactor:1,hasTouch:true,isMobile:true,serviceWorkers:'block'});
  await ctx.addInitScript({content:readFileSync(join(root,'tools/golden/init.js'),'utf8')});
  await ctx.route('**/__charge_cover_three__/*',async route=>{
   const file=new URL(route.request().url()).pathname.split('/').at(-1);
   if(!['three.module.js','three.core.js'].includes(file))return route.abort();
   return route.fulfill({contentType:'text/javascript',path:join(root,'node_modules','three','build',file)});
  });
  const page=await ctx.newPage();
  page.on('pageerror',error=>console.error(error));
  await page.goto(`http://127.0.0.1:${Number(process.env.FABLE_PROBE_PORT??5174)}/?golden&dev&q=medium`,{waitUntil:'domcontentloaded'});
  await page.waitForFunction(()=>window.game?.started&&game?.mobs?.list&&game.renderer.gl.info.render.frame>0,null,{timeout:90000});
  const start=await page.evaluate(async kind=>{
   // Same local import for both runs; this module only draws the test box.
   __golden.freeze();
   const three=await import('/__charge_cover_three__/three.module.js');
   const g=game,p=g.player,h=__golden,x=33,z=108;
   const y=g.groundY(x,z,40), enemyY=g.groundY(x,z+12,40), boxY=g.groundY(x,z+4.8,40);
   if(![y,enemyY,boxY].every(Number.isFinite)||Math.abs(y-enemyY)>.18)throw Error('Unusable test site');
   g.mobs.manageCamps=()=>{};
   g.mobs.clear();
   g.mobs.spawnQueue.length=0;
   g.state.d.level=4;
   g.state.d.hp=g.state.maxHp;
   g.state.d.energy=g.state.maxEnergy;
   if(g.state.god)throw Error('God must remain false');
   h.seed(0x81ad);
   p.teleport(x,y+.12,z,0);
   g.cameraRig.snap(Math.PI,.20);
   g.combat.target=null;
   g.env.clockRunning=false;g.env.hour=12.5;g.env.forcedHour=12.5;
   document.querySelector('#dev')?.style.setProperty('display','none');
   const jack=g.mobs.spawn('pallet',{x,z:z+12,level:4,variant:'normal'});
   if(!jack)throw Error('Missing Pallet Jack');
   // Height is intentionally below the attack-choice sightline but across the ram ray.
   const dims=[2.4,1.0,1.1],center=[x,boxY+.5,z+4.8];
   let block=null;
   if(kind!=='open'){
    block=g.physics.addBox(...center,...dims.map(d=>d/2));
    const group=new three.Group();
    group.position.set(...center);
    const solid=(w,h,d,color,x=0,y=0,z=0)=>{
     const mesh=new three.Mesh(new three.BoxGeometry(w,h,d),new three.MeshStandardMaterial({color,roughness:.78}));
     mesh.position.set(x,y,z);group.add(mesh);return mesh;
    };
    solid(...dims,0x9b6238);
    for(const x of [-1.04,1.04])solid(.16,1.008,1.118,0x635146,x);
    for(const y of [-.39,.38])solid(2.414,.12,1.12,0x684d37,0,y);
    g.scene.add(group);
   }
   const baseRay=g.physics.raycast.bind(g.physics),baseSfx=g.sfx.bind(g),draw=g.renderer.render.bind(g.renderer);
   const f=window.coverFixture={phase:null,trace:[],contacts:[],sounds:[],seen:null};
   g.physics.raycast=(origin,direction,max,filter,...rest)=>{
    const hit=baseRay(origin,direction,max,filter,...rest);
    if(jack.state==='active'&&jack.atk?.id==='charge'&&filter===undefined&&
       Math.abs(origin.y-jack.pos.y-.7)<1e-5&&Math.hypot(origin.x-jack.pos.x,origin.z-jack.pos.z)<1e-5&&
       Math.abs(direction.y)<1e-5&&max<jack.radius+1)
     f.contacts.push({frame:h.frame,cover:!!block&&hit?.collider.handle===block.handle,
       hit:!!hit,dist:hit?.dist??null,point:hit?.point.toArray()??null});
    return hit;
   };
   g.sfx=(id,...args)=>{
    if(id==='enemy_crash')f.sounds.push({id,frame:h.frame});
    return baseSfx(id,...args);
   };
   const began=h.frame;
   const isRiposte=kind==='early'||kind==='late';
   let recovery=null,moveStart=null,attack=null,contact=null,route=0;
   const keys=['KeyW','KeyA','KeyS','KeyD'];
   const fwd=p.pos.clone();
   const move=(dx,dz)=>{
    for(const k of keys)g.input.keys.delete(k);
    g.input.release('sprint');
    if(Math.hypot(dx,dz)<.001)return;
    g.cameraRig.forward(fwd);
    const turn=Math.atan2(-fwd.z*dx+fwd.x*dz,fwd.x*dx+fwd.z*dz);
    const k=(Math.round(turn/(Math.PI/4))+8)%8;
    for(const key of [[keys[0]],[keys[0],keys[3]],[keys[3]],[keys[2],keys[3]],[keys[2]],
       [keys[2],keys[1]],[keys[1]],[keys[0],keys[1]]][k])g.input.keys.add(key);
    g.input.press('sprint');
   };
   const points=[[x+1.95,z+1.55],[x+2.15,z+4.2],[x+1.96,z+5.45]];
   const clearMelee=()=>{
    const a=p.pos.clone();a.y+=.8;
    const d=jack.pos.clone();d.y+=.8;d.sub(a);const dist=d.length();d.multiplyScalar(1/dist);
    return dist<3.55&&!baseRay(a,d,Math.max(0,dist-.65));
   };
   g.renderer.render=(...args)=>{
    if(isRiposte ? (f.windup&&((!f.recover&&jack.state==='recover')||(jack.hp<f.startHp&&contact===null)||contact===h.frame-2)) :
      (jack.atk?.id==='charge'&&((jack.state==='windup'&&jack.locked&&!f.windup)||(jack.state==='recover'&&!f.recover))))draw(...args);
   };
   f.startHp=jack.hp;
   h.post=()=>{
    const row={frame:h.frame-began,sim:g.simTime,st:jack.state,t:jack.stT,atk:jack.atk?.id??null,locked:jack.locked,
     fired:jack.fired,pose:jack.pose.action,p:p.pos.toArray(),jack:jack.pos.toArray(),hp:g.state.d.hp,enemyHp:jack.hp,
     rolling:p.rolling,invuln:p.invuln,god:g.state.god,
     playerAction:p.action,sprint:p.sprinting,target:g.combat.target?.kind??null,route};
    f.trace.push(row);
    if(jack.state==='windup'&&jack.atk?.id==='charge'&&jack.locked&&!f.windup){
     const o=jack.pos.clone();o.y+=jack.lift+jack.fly+Math.max(.6,jack.height*.8);
     const d=p.pos.clone();d.y+=1.2;d.sub(o);const len=d.length();d.multiplyScalar(1/len);
     const look=baseRay(o,d,len-.5,0xffff0001);
     const low=o.copy(jack.pos);low.y+=.7;
     const aim=d.set(Math.sin(jack.lockYaw),0,Math.cos(jack.lockYaw));
     const ram=baseRay(low,aim,14);
     f.seen={highBlocked:!!look,lowBlocked:!!ram,lowHitsBox:!!block&&ram?.collider.handle===block.handle,
      lowDistance:ram?.dist??null,aim:aim.toArray()};
     // Frozen presentation-only A/B. Keep the native warning width, pulse
     // and color on the clipped section, and restore before play resumes.
     const tele=jack.tele, length=jack.atk.length;
     f.drawLocked=(candidate)=>{
      const mesh=tele.mesh,original=mesh.position.clone(),scale=mesh.scale.z,yaw=mesh.rotation.y;
      const end=candidate&&f.seen.lowHitsBox?Math.min(length,Math.max(.2,f.seen.lowDistance)):length;
      if(end<length){
       mesh.scale.z=end/2;
       mesh.rotation.y=jack.lockYaw;
       mesh.position.x=jack.pos.x+f.seen.aim[0]*end/2;
       mesh.position.z=jack.pos.z+f.seen.aim[2]*end/2;
       g.fx.marks.update(0);
      }
      draw(g.scene,g.camera,0);
      mesh.position.copy(original);mesh.scale.z=scale;mesh.rotation.y=yaw;
      if(end<length)g.fx.marks.update(0);
      return {length:end,width:mesh.scale.x*2,frame:h.frame,sim:g.simTime,hp:g.state.d.hp,
       jack:jack.pos.toArray(),camera:g.camera.position.toArray(),angle:g.camera.quaternion.toArray(),
       clock:tele.u.uT.value};
     };
     f.windup=row;
     if(!isRiposte){f.phase='windup';h.freeze();}
    }else if(jack.state==='recover'&&jack.atk?.id==='charge'&&!f.recover){
     f.recover=row;recovery=h.frame;
     if(!isRiposte){f.phase='recover';h.freeze();}
    }else if(!isRiposte&&f.recover&&jack.state!=='recover'){
     f.phase='end';h.freeze();
    }else if(row.frame>480){
     f.phase='timeout';h.freeze();
    }
    if(isRiposte&&f.windup){
     if(recovery!==null&&!f.recoveryExit&&jack.state!=='recover')f.recoveryExit=row;
     if(moveStart===null&&(kind==='early'||(recovery!==null&&h.frame-recovery>=46))){
      moveStart=h.frame;f.moveStart=row;
     }
     if(moveStart!==null){
      if(attack===null){
       // The waypoints route around the right edge of the fixture. No actor
       // transform or velocity is overwritten after the start.
       if(clearMelee()&&p.pos.z>z+4.0){
        move(0,0);g.input.press('attack');attack=h.frame;f.attack=row;
       }else{
        while(route<points.length&&Math.hypot(points[route][0]-p.pos.x,points[route][1]-p.pos.z)<.42)route++;
        const [tx,tz]=points[route]??[jack.pos.x,jack.pos.z];
        move(tx-p.pos.x,tz-p.pos.z);
       }
      }else if(h.frame===attack+1)g.input.release('attack');
      if(jack.hp<f.startHp&&contact===null){contact=h.frame;f.contact=row;}
      if(contact!==null&&h.frame>=contact+2){f.phase='end';h.freeze();}
      if(moveStart!==null&&h.frame-moveStart>125){f.phase='miss';h.freeze();}
     }
    }
   };
   h.thaw();
   return {kind,center,dims,hp:g.state.d.hp,firstMobHp:jack.hp};
  },kind);
  if(mode==='riposte'){
   await page.waitForFunction(()=>['timeout','end','miss'].includes(window.coverFixture?.phase),null,{timeout:90000,polling:100});
   await page.screenshot({path:join(out,kind+'-sword.jpg'),type:'jpeg',quality:91});
   receipt[kind]={start,...await page.evaluate(()=>coverFixture)};
   const {phase,moveStart,attack,contact,recover,recoveryExit,sounds}=receipt[kind];
   console.log(JSON.stringify({kind,phase,moveStart,attack,contact,recover,recoveryExit,sounds}));
   writeFileSync(join(out,'proof.json'),JSON.stringify(receipt,null,2)+'\n');
   await ctx.close();
   continue;
  }
  for(const phase of ['windup','recover','end']){
   await page.waitForFunction(()=>['timeout','windup','recover','end'].includes(window.coverFixture?.phase),null,{timeout:90000,polling:100});
   const reached=await page.evaluate(()=>coverFixture.phase);
   assert.equal(reached,phase,'Native replay did not reach expected phase');
   if(phase==='windup'){
    const stock=await page.evaluate(()=>coverFixture.drawLocked(false));
    await page.screenshot({path:join(out,kind+'-windup.jpg'),type:'jpeg',quality:91});
    const clipped=await page.evaluate(()=>coverFixture.drawLocked(true));
    await page.screenshot({path:join(out,kind+'-clipped.jpg'),type:'jpeg',quality:91});
    const {length:oldLength,...oldVars}=stock,{length:newLength,...newVars}=clipped;
    assert.deepEqual(oldVars,newVars);
    assert(kind==='cover'?newLength<oldLength:newLength===oldLength);
    await page.evaluate(rows=>{coverFixture.warning=rows;coverFixture.phase=null;__golden.thaw();},[stock,clipped]);
   }else if(phase!=='end'){
    await page.screenshot({path:join(out,kind+'-'+phase+'.jpg'),type:'jpeg',quality:91});
    await page.evaluate(()=>{coverFixture.phase=null;__golden.thaw();});
   }
  }
  receipt[kind]={start,...await page.evaluate(()=>coverFixture)};
  writeFileSync(join(out,'proof.json'),JSON.stringify(receipt,null,2)+'\n');
  await ctx.close();
 }
 if(mode==='riposte'){
  for(const r of [receipt.early,receipt.late]){
   assert(r.windup&&r.recover&&r.moveStart);
   assert(r.contacts.some(c=>c.cover),'No native charge collision with fixture');
   assert.equal(r.sounds.length,1);
   assert.equal(r.recover.hp,r.start.hp);
   assert(r.trace.every(t=>!t.god&&!t.rolling));
  }
  assert(receipt.early.contact?.st==='recover','Early light swing did not hit during recovery');
  assert(receipt.early.contact?.playerAction==='sword1');
  assert(receipt.late.recoveryExit&&receipt.late.recoveryExit.enemyHp===receipt.late.start.firstMobHp,'Late move damaged Jack before recovery finished');
 }else{
 for(const run of [receipt.open,receipt.cover]){
  assert.equal(run.seen.highBlocked,false,'Stock high line of sight was blocked');
  assert(run.trace.some(r=>r.st==='active'&&r.atk==='charge'));
  assert.equal(run.recover.enemyHp,run.start.firstMobHp);
  assert(run.trace.every(r=>!r.god&&!r.rolling));
 }
 assert.equal(receipt.open.seen.lowBlocked,false);
 assert.equal(receipt.cover.seen.lowHitsBox,true);
 assert(receipt.open.recover.hp<receipt.open.start.hp,'Open control did not take damage');
 assert.equal(receipt.cover.recover.hp,receipt.cover.start.hp,'Cover did not prevent damage');
 assert.equal(receipt.open.sounds.length,0);
 assert.equal(receipt.cover.sounds.length,1);
 assert(receipt.cover.contacts.some(c=>c.cover),'No native ram ray hit the fixture collider');
 assert.equal(receipt.cover.recover.fired,2);
 for(const {start,windup,recover,contacts,trace} of [receipt.open,receipt.cover])
  console.log(JSON.stringify({case:start.kind,hp:[start.hp,recover.hp],windup:windup.frame,recover:recover.frame,firstHit:contacts.find(c=>c.hit),active:trace.filter(r=>r.st==='active').length,recoverFrames:trace.filter(r=>r.st==='recover').length}));
 }
}finally{await browser.close();}
