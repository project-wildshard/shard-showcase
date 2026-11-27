import {brokenCycle} from './broken-cycle.mjs';
import {touchCounter, touchMarks} from './touch-counter.mjs';
import {counterLens} from './counter-lens.mjs';
// Read-only reference playtest. Run against a loopback build of the pinned
// source. The fresh browser context will have a disposable dev game save.
import {createRequire} from 'node:module';
import {readFileSync,writeFileSync,mkdtempSync} from 'node:fs';
import {execFileSync} from 'node:child_process';
import {join} from 'node:path';
import {tmpdir} from 'node:os';
import {pathToFileURL} from 'node:url';
const [root,dep,mode='counter',control='none'] = process.argv.slice(2);
const ref='3afcd880b397e9703e906a7e66b42e8447e59519';
if(!root||!dep||!['sidestep','counter','wash','gauge','framing','live-framing','gauge-cycle'].includes(mode)||!['none','look','sprint','hud-drag','hud-tap','hud-cancel','canvas-drag','zero'].includes(control))
  throw Error('Usage: node native-probe.mjs FABLE_CHECKOUT DEPENDENCY_PROJECT [sidestep|counter|wash|gauge|framing|live-framing|gauge-cycle] [none|look|sprint|hud-drag|hud-tap|hud-cancel|canvas-drag|zero]');
if(execFileSync('git',['-C',root,'rev-parse','HEAD'],{encoding:'utf8'}).trim()!==ref)
  throw Error('Wrong reference checkout');
const load=createRequire(join(dep,'package.json'));
const pw=await import(pathToFileURL(load.resolve('playwright')).href);
const chromium=pw.chromium??pw.default?.chromium;
const {default:shell}=await import(pathToFileURL(load.resolve('@sparticuz/chromium')).href);
const out=mkdtempSync(join(tmpdir(),'jack-native-'));
const onlySide=mode==='sidestep';
const touchCase=control.startsWith('hud-')||control==='canvas-drag';
if(touchCase&&mode!=='live-framing')throw Error('Touch control requires live-framing');
const browser=await chromium.launch({executablePath:await shell.executablePath(),headless:true,args:shell.args});
try {
 const ctx=await browser.newContext({viewport:{width:402,height:874},deviceScaleFactor:1,hasTouch:true,isMobile:true,serviceWorkers:'block'});
 await ctx.addInitScript({content:readFileSync(join(root,'tools/golden/init.js'),'utf8')});
 await ctx.addInitScript({content:'window.makeCounterLens='+counterLens.toString()+';window.makeBrokenCycle='+brokenCycle.toString()+';'});
 const page=await ctx.newPage();
 page.on('pageerror',e=>console.log('pageerror',String(e).slice(0,400)));
 await page.goto(`http://127.0.0.1:${Number(process.env.FABLE_PROBE_PORT??5174)}/?golden&dev&q=medium`,{waitUntil:'domcontentloaded'});
 await page.waitForFunction(()=>window.game?.started&&game?.mobs?.list&&game.renderer.gl.info.render.frame>0,null,{timeout:90000,polling:250});
 const setup=await page.evaluate(({onlySide,mode,control,touchCase,touchMarks})=>{
  const g=game,p=g.player,h=__golden;
  const pos=(x,y,z)=>p.pos.clone().set(x,y,z);
  const ground=(x,z)=>g.groundY(x,z,40);
  const trySite=(x,z)=>{
    const gh=ground(x,z), eh=ground(x,z+12);
    if(!Number.isFinite(gh)||!Number.isFinite(eh)||Math.abs(gh-eh)>.18)return null;
    if(g.physics.raycast(pos(x,gh+1.2,z),pos(0,0,1),12))return null;
    if(g.physics.raycast(pos(x,gh+.7,z),pos(0,0,1),12))return null;
    if(g.physics.raycast(pos(x,gh+.7,z),pos(1,0,0),4.5))return null;
    if(g.physics.raycast(pos(x,gh+.7,z),pos(-1,0,0),4.5))return null;
    if(Math.abs(ground(x+4,z)-gh)>.2||Math.abs(ground(x-4,z)-gh)>.2)return null;
    return [x,z,gh,eh];
  };
  let site=null;
  for(const z of [108,118,128,138,148,158,168,178,188,198,208])
   for(const x of [33,41,49,57,65,73,81,89,97,105])if(!site)site=trySite(x,z);
  if(!site)throw new Error('No clear measured site');
  const [x,z,gh,eh]=site;
  g.mobs.manageCamps=()=>{};g.mobs.clear();
  g.mobs.spawnQueue.length=0;
  g.state.d.level=4;g.state.d.xp=0;g.state.d.hp=g.state.maxHp;g.state.d.energy=g.state.maxEnergy;
  if(g.state.god)throw new Error('God flag must stay false');
  p.teleport(x,gh+.12,z,0);
  g.cameraRig.snap(Math.PI,.20);
  g.env.clockRunning=false;g.env.hour=12.5;g.env.forcedHour=12.5;
  g.combat.target=null;
  const mob=g.mobs.spawn('pallet',{x,z:z+12,level:4,variant:'normal'});
  if(!mob)throw new Error('No real Pallet Jack');
  window.fixture={mob,trace:[],mode:onlySide?'ramp':'counter',dodgePressed:false,counterPressed:false,startEnemyHp:mob.hp};
  document.querySelector('#dev')?.style.setProperty('display','none');
  if(mode==='gauge-cycle'){
    g.state.d.settings.flash=control==='zero'?0:1;
    fixture.cycleSnap=window.makeBrokenCycle(g,fixture,h);
    fixture.phases=[.99,.50,.25];
  }
  if(mode==='gauge'){
    const fx=g.fx, labels=['other','robot.break','hit.blade','break-ring','counter-ring'];
    const pools=[fx.add,fx.alpha].map(pool=>{
      const mask=new Uint8Array(pool.life.length);
      if(!Array.isArray(pool.all))throw Error('Effect pool is not compactable');
      pool.all.push(mask);
      return {pool,mask};
    });
    let tag=0;
    function scope(id,fun){const prior=tag;tag=id;try{return fun()}finally{tag=prior}}
    const play=fx.play.bind(fx);
    fx.play=(name,...args)=>scope(Math.max(0,labels.indexOf(name)),()=>play(name,...args));
    const ring=fx.ring.bind(fx);
    fx.ring=(p,r,c,life,...rest)=>{
      const id=c===0xffd27a&&life===.45?3:c===0xffffff&&r===3&&life===.25?4:tag;
      return scope(id,()=>ring(p,r,c,life,...rest));
    };
    const emit=fx.emit.bind(fx);
    fx.emit=(...args)=>{
      const start=pools.map(({pool})=>pool.n);
      const result=emit(...args);
      pools.forEach(({pool,mask},i)=>mask.fill(tag,start[i],pool.n));
      return result;
    };
    let original=null;
    const rb=fx.ribbons;
    let baseRibbon=null;
    const rbRows={gauge:8,trail:2};
    const render=g.renderer.render.bind(g.renderer);
    const modes={base:[],break:[1,3],blade:[2],ring:[4],all:[1,2,3,4],gauge:[],trail:[],compact:[]};
    window.fixture.snap=(mode)=>{
      const mark=fixture.mob;
      for(const m of mark.rig.materials)m.flash.value.w=Math.min(m.flash.value.w,.22);
      if(!original)original=pools.map(({pool})=>pool.aCol.slice());
      const counts=[0,0,0,0,0];
      pools.forEach(({pool,mask},j)=>{
        pool.aCol.set(original[j]);
        for(let i=0;i<pool.n;i++){
          counts[mask[i]]++;
          if(modes[mode].includes(mask[i]))
            pool.aCol[i*4+3]=0;
        }
        pool.mesh.geometry.getAttribute('iCol').needsUpdate=true;
      });
      if(!baseRibbon)baseRibbon={p:rb.P.slice(),c:rb.C.slice()};
      rb.P.set(baseRibbon.p);rb.C.set(baseRibbon.c);
      const n=rb.w*2,selected=[];
      const row=mode==='trail'?rbRows.trail:rbRows.gauge;
      for(let q=0;q<n;q++)if(rb.S[q*4]===row&&rb.C[q*4+3]>0)selected.push(q);
      if((mode==='gauge'||mode==='trail')&&selected.length){
        for(const q of selected)rb.C[q*4+3]=0;
      }
      if(mode==='compact'&&selected.length){
        const c=[0,0,0];
        for(const q of selected)for(let k=0;k<3;k++)c[k]+=rb.P[q*3+k]/selected.length;
        for(const q of selected){
          for(let k=0;k<3;k++)rb.P[q*3+k]=c[k]+.58*(rb.P[q*3+k]-c[k]);
          if(rb.S[q*4+3]>0)rb.C[q*4+3]*=.65;
        }
      }
      for(const k of ['position','aCol'])rb.mesh.geometry.getAttribute(k).needsUpdate=true;
      render(g.scene,g.camera,0);
      return {labels,counts,mode,ribbonSelected:selected.length,ribbonRow:row,frame:h.frame,gameTime:g.time,simTime:g.simTime,
         hp:[g.state.d.hp,mark.hp],yaw:g.cameraRig.yaw,camera:g.camera.position.toArray()};
    };
  }
  if(mode==='live-framing'){
    const rig=g.cameraRig,cam=g.camera,step=window.makeCounterLens();
    const update=rig.update.bind(rig),rad=Math.PI/180;
    let prior=null,hold=0,last=null;
    const heading=q=>{
      const v=p.pos.clone().set(0,0,-1).applyQuaternion(q);
      return Math.atan2(-v.x,-v.z)/rad;
    };
    fixture.lensTrace=[];
    fixture.pointerEvents=[];
    if(touchCase)for(const kind of ['pointerdown','pointermove','pointerup','pointercancel','gotpointercapture','lostpointercapture'])
      document.addEventListener(kind,e=>{
        if(e.pointerType!=='touch')return;
        fixture.pointerEvents.push({kind,id:e.pointerId,frame:h.frame,
          trusted:e.isTrusted,x:e.clientX,y:e.clientY,act:e.target?.closest?.('[data-act]')?.dataset.act??null});
      },true);
    if(control==='look')h.pre=()=>{
      const since=h.frame-(fixture.counterFrame??Infinity);
      const dx=[-2,-2,-12,12,2,12][since-20];
      if(dx)g.input.dragLook(dx,0);
    };
    rig.update=(dt,focus,options)=>{
      if(prior){
        cam.quaternion.copy(prior.q);cam.fov=prior.fov;
        cam.updateProjectionMatrix();cam.updateMatrixWorld(true);
      }
      const since=h.frame-(fixture.counterFrame??Infinity);
      const testLook=control==='look'&&since>=20&&since<26;
      update(dt,focus,options);
      prior={q:cam.quaternion.clone(),fov:cam.fov};
      fixture.stockCamera=prior;
      const sprintIntent=g.input.down('sprint');
      const canvasLook=!!g.input.lookIds?.size;
      const nativeDelta=Math.abs(options.lookX??0)+Math.abs(options.lookY??0)>.0005;
      const hudSteer=Object.values(g.hud.acts).some(a=>a.ptr!==-1&&a.root.classList.contains('steer'));
      const legacyLook=nativeDelta||canvasLook;
      const looking=legacyLook||hudSteer;
      const hardStop=rig.autoFollow===false||rig.view!=='third';
      const override=p.sprinting||sprintIntent||!!options.flee||g.combat.target!==mob||looking||hardStop;
      if(p.action==='swordRise')hold=.12; else hold=Math.max(0,hold-dt);
      const engaged=g.combat.target===mob&&hold>0&&mob.alive;
      const anchors=[];
      if(engaged){
        const put=(w,hero,r=0)=>{
          w.applyMatrix4(cam.matrixWorldInverse);
          anchors.push([w.x-r,w.y,w.z,hero],[w.x+r,w.y,w.z,hero]);
        };
        const v=p.pos.clone();
        for(const k of ['head','chest','hips'])put(p.rig.sockets[k].getWorldPosition(v),true,.24);
        put(v.copy(p.pos),true,.25);
        if(p.rig.weapon?.tip)put(p.rig.weapon.tip.getWorldPosition(v),true);
        for(const k of ['head','core','muzzle','weak'])put(mob.rig.sockets[k].getWorldPosition(v),false,k==='muzzle'?.44:.32);
      }
      const adj=step({anchors,fov:cam.fov,aspect:cam.aspect,dt,engaged,override,hardStop,lookDeg:looking?(options.lookX??0)/rad:null});
      if(adj.turn||adj.widen){
        cam.rotateY(adj.turn*rad);cam.fov+=adj.widen;
        cam.updateProjectionMatrix();cam.updateMatrixWorld(true);
      }
      const shown=heading(cam.quaternion),stock=heading(prior.q);
      let immediateClearDelta=null;
      if(last){
        const d=stock-last.shown;
        immediateClearDelta=((d+540)%360)-180;
      }
      if(engaged||Number.isFinite(since)&&since<64)
        fixture.lensTrace.push({frame:h.frame,dt,since,...adj,engaged,
          override,testLook,lookX:options.lookX,lookY:options.lookY,canvasLook,hudSteer,legacyLook,holdingMove:g.input.holdingMove,sprintIntent,sprinting:p.sprinting,rigYaw:rig.yaw,
          stock,shown,immediateClearDelta,stockFov:prior.fov,shownFov:cam.fov});
      last={shown};
    };
  }
  if(mode==='framing'||mode==='live-framing'){
    const render=g.renderer.render.bind(g.renderer);
    const rigPoints=(rig)=>{
      const pts=[],v=p.pos.clone();
      rig.root.updateWorldMatrix(true,true);
      rig.root.traverseVisible(o=>{
        if(!o.isMesh||!o.geometry?.attributes.position||o===p.rig.fpDev?.mesh)return;
        const idx=o.geometry.index;
        const end=Math.min(o.geometry.drawRange.count,(idx?.count??o.geometry.attributes.position.count)-o.geometry.drawRange.start);
        const used=new Set();
        for(let i=0;i<end;i++){
          const j=idx?idx.getX(i+o.geometry.drawRange.start):i+o.geometry.drawRange.start;
          if(used.has(j))continue;
          used.add(j);o.getVertexPosition(j,v);
          pts.push(v.clone().applyMatrix4(o.matrixWorld));
        }
      });
      return pts;
    };
    fixture.framing=(draw=null)=>{
      const m=fixture.mob,cam=g.camera,probe=cam.clone(),v=p.pos.clone();
      const bases=[['rook',p.rig,['head','chest']],['jack',m.rig,['head','core','muzzle']]];
      const buttons=mode==='live-framing'?[...document.querySelectorAll('button.abtn')].flatMap(e=>{
        const r=e.getBoundingClientRect(),style=getComputedStyle(e);
        if(!r.width||!r.height||style.visibility!=='visible'||+style.opacity===0)return [];
        return [{id:e.dataset.act,cx:r.x+r.width/2,cy:r.y+r.height/2,rx:r.width/2,ry:r.height/2}];
      }):[];
      const actors=bases.map(([name,rig,labels])=>({name,pts:rigPoints(rig),sockets:Object.fromEntries(labels.map(k=>[k,rig.sockets[k].getWorldPosition(v).clone()]))}));
      // A measurement control, not a controller: stage a bounded taper on
      // these exact contact-relative samples. No input, collision or HUD changes.
      const taper={0:{plus:8,yaw:12},6:{plus:8,yaw:8},12:{yaw:4},18:{yaw:2},30:{}};
      const original=(name)=>({plus:0,yaw:0,...({taper:taper[h.frame-fixture.hitFrame],wide6:{plus:6},wide12:{plus:12},
        left4:{yaw:4},right4:{yaw:-4},left8:{yaw:8},right8:{yaw:-8},left12:{yaw:12},right12:{yaw:-12}}[name]??{})});
      const measure=(name)=>{
        const {plus,yaw}=original(name);
        const base=name==='live' ? null : fixture.stockCamera;
        probe.quaternion.copy(base?.q??cam.quaternion);
        probe.rotateY(yaw*Math.PI/180);
        probe.fov=(base?.fov??cam.fov)+plus;probe.updateProjectionMatrix();probe.updateMatrixWorld(true);
        const proj=(w)=>{
          v.copy(w).applyMatrix4(probe.matrixWorldInverse);
          if(v.z>=-probe.near)return null;
          v.copy(w).project(probe);return [(1+v.x)*201,(1-v.y)*437];
        };
        return {name,fov:probe.fov,yaw,actors:Object.fromEntries(actors.map(({name,pts,sockets})=>{
          const bounds=[Infinity,Infinity,-Infinity,-Infinity];
          let outside=0,behind=0;
          const hud={};
          for(const w of pts){
            const xy=proj(w);
            if(!xy){behind++;continue}
            const [x,y]=xy;
            if(x<0||x>402||y<0||y>874)outside++;
            for(const b of buttons)
              if(((x-b.cx)/b.rx)**2+((y-b.cy)/b.ry)**2<1)hud[b.id]=(hud[b.id]??0)+1;
            bounds[0]=Math.min(bounds[0],x);bounds[1]=Math.min(bounds[1],y);
            bounds[2]=Math.max(bounds[2],x);bounds[3]=Math.max(bounds[3],y);
          }
          return [name,{bounds,vertices:pts.length,outside,behind,hud,sockets:Object.fromEntries(Object.entries(sockets).map(([k,w])=>[k,proj(w)]))}];
        }))};
      };
      const results=(mode==='live-framing'?['stock','live']:['stock','wide6','wide12','left4','right4','left8','right8','left12','right12','taper']).map(measure);
      if(draw){
        const {plus,yaw}=original(draw);
        const f=cam.fov,q=cam.quaternion.clone();
        cam.fov+=plus;cam.rotateY(yaw*Math.PI/180);
        cam.updateProjectionMatrix();cam.updateMatrixWorld(true);
        render(g.scene,cam,0);
        cam.fov=f;cam.quaternion.copy(q);cam.updateProjectionMatrix();cam.updateMatrixWorld(true);
      }
      return {frame:h.frame,gameTime:g.time,simTime:g.simTime,hp:[g.state.d.hp,m.hp],
        yaw:g.cameraRig.yaw,camera:cam.position.toArray(),results};
    };
  }
  const draw=g.renderer.render.bind(g.renderer);
  g.renderer.render=(...args)=>{
   const x=window.fixture,m=x.mob;
   if((mode==='live-framing'&&x.counterPressed&&(touchCase?touchMarks:[9,15,20,24,29,35,44,53]).includes(h.frame-x.counterFrame))||
      (x.mode==='ramp'&&m.state==='windup'&&m.atk?.id==='charge'&&m.stT>.45)||
      (x.mode==='run'&&m.state==='recover')||(mode!=='gauge-cycle'&&x.counterPressed&&m.hp<x.startEnemyHp))draw(...args);
  };
  h.post=()=>{
    const x=window.fixture,m=x.mob;
    const row={frame:h.frame,time:g.time,sim:g.simTime,st:m.state,t:m.stT,atk:m.atk?.id??null,
      aggro:m.aggro,enabled:g.combat.enabled,target:g.combat.target?.kind??null,
      d:Math.hypot(m.pos.x-p.pos.x,m.pos.z-p.pos.z),p:p.pos.toArray(),monster:m.pos.toArray(),
      yaw:g.cameraRig.yaw,actorYaw:m.yaw,locked:m.locked,rolling:p.rolling,
      playerHp:g.state.d.hp,enemyHp:m.hp,god:g.state.god,counterT:g.combat.counterT,action:p.action,phase:p.actionT,invuln:p.invuln,
      arrow:[...document.querySelectorAll('.threat-arrow')].some(e=>e.style.display==='block')};
    x.trace.push(row);
    if(x.mode==='ramp'&&m.state==='windup'&&m.atk?.id==='charge'&&m.stT>.45){
      x.mode='windup-frozen';h.freeze();
    } else if(x.mode==='run'&&m.state==='recover'){x.mode='recover-frozen';h.freeze();}
    if(x.mode==='counter'&&!x.dodgePressed&&m.state==='active'&&m.atk?.id==='charge'&&row.d<=3.35){
      x.dodgePressed=true;x.dodgeFrame=h.frame;
      g.input.keys.add('KeyW');g.input.press('dodge');
    } else if(x.dodgePressed && h.frame===x.dodgeFrame+1) {
      g.input.release('dodge');g.input.keys.delete('KeyW');
    }
    if(x.dodgePressed&&!x.counterPressed&&g.combat.counterT>0){
      x.counterPressed=true;x.counterFrame=h.frame;
      if(touchCase){x.mode='touch-start';h.freeze();}else g.input.press('attack');
    } else if(!touchCase&&x.counterPressed&&h.frame===x.counterFrame+1)g.input.release('attack');
    if(mode==='live-framing'&&x.counterPressed){
      const since=h.frame-x.counterFrame;
      if(control==='sprint'&&since===18){g.input.keys.add('KeyS');g.input.press('sprint');}
      if(control==='sprint'&&since===33){g.input.release('sprint');g.input.keys.delete('KeyS');}
      if(m.hp<x.startEnemyHp&&!x.contact)
        x.contact={since,...x.framing()};
      if((touchCase?touchMarks:[9,15,20,24,29,35,44,53]).includes(since)){
        x.mode='framing-frozen';h.freeze();
      }
    }
    if(mode==='gauge-cycle'&&m.state==='broken'&&x.phases.length&&1-m.stT/m.brokenDur<=x.phases[0]){
      x.phase=x.phases.shift();x.mode='gauge-frozen';h.freeze();
    }
    if(mode!=='live-framing'&&mode!=='gauge-cycle'&&x.counterPressed&&m.hp<x.startEnemyHp){
      if(mode==='framing'){
        x.hitFrame??=h.frame;
        if([0,6,12,18,30].includes(h.frame-x.hitFrame)){
          x.mode='framing-frozen';h.freeze();
        }
      }else{x.mode='counter-frozen';h.freeze();}
    }
    if(h.frame>590){x.mode='ended';h.freeze();}
  };
  return {site,hp:g.state.d.hp,enabled:g.combat.enabled,god:g.state.god,touch:g.input.isTouch,view:g.cameraRig.view};
 },{onlySide,mode,control,touchCase,touchMarks});
 console.log('setup',JSON.stringify(setup));
 if(onlySide){
   await page.waitForFunction(()=>window.fixture?.mode==='windup-frozen',null,{timeout:90000,polling:200});
   await page.screenshot({path:join(out,'windup.jpg'),type:'jpeg',quality:89});
   await page.keyboard.down('a');
   await page.evaluate(()=>{fixture.mode='run';__golden.thaw();});
   await page.waitForFunction(()=>window.fixture?.mode==='recover-frozen',null,{timeout:90000,polling:200});
   await page.keyboard.up('a');
   await page.screenshot({path:join(out,'recover.jpg'),type:'jpeg',quality:89});
 }else if(mode==='gauge-cycle'){
   const phases=[];
   for(const value of [.99,.50,.25]){
     await page.waitForFunction(()=>['gauge-frozen','ended'].includes(window.fixture?.mode),null,{timeout:90000,polling:100});
     const reached=await page.evaluate(()=>fixture.phase);
     if(reached!==value)throw Error('Wrong Broken phase');
     const pair=[];
     for(const compact of [false,true]){
       pair.push(await page.evaluate(compact=>fixture.cycleSnap(compact),compact));
       await page.screenshot({path:join(out,'cycle-'+value+'-'+(compact?'compact':'stock')+'.png')});
     }
     for(const k of ['frame','sim','time','hp','camera','q','strobe','remaining','trackVertices','goldVertices','center'])
       if(JSON.stringify(pair[0][k])!==JSON.stringify(pair[1][k]))throw Error('Comparison moved '+k);
     phases.push(pair);
     if(value!==.25)await page.evaluate(()=>{fixture.mode='counter';__golden.thaw();});
   }
   writeFileSync(join(out,'broken-cycle.json'),JSON.stringify(phases,null,2)+'\n');
 }else if(touchCase){
   const evidence=await touchCounter(page,ctx,control,out);
   writeFileSync(join(out,'touch-counter.json'),JSON.stringify(evidence,null,2)+'\n');
 }else if(mode==='live-framing'){
   const samples=[];
   for(const since of [9,15,20,24,29,35,44,53]){
     await page.waitForFunction(()=>['framing-frozen','ended'].includes(window.fixture?.mode),null,{timeout:90000,polling:100});
     const row=await page.evaluate(()=>({since:__golden.frame-fixture.counterFrame,...fixture.framing()}));
     if(row.since!==since)throw Error('Wrong live sample');
     samples.push(row);
     if((control==='none'&&[20,24].includes(since))||(control==='look'&&[20,24].includes(since)))
       await page.screenshot({path:join(out,'live-'+since+'.jpg'),type:'jpeg',quality:90});
     if(since!==53)await page.evaluate(()=>{fixture.mode='counter';__golden.thaw()});
   }
   const {lens,contact}=await page.evaluate(()=>({lens:fixture.lensTrace,contact:fixture.contact??null}));
   if(control==='none'&&!lens.some(r=>r.widen>0&&r.turn!==0))throw Error('Lens did not engage');
   if(control!=='none'&&!lens.some(r=>(control==='look'?r.testLook&&r.lookX!==0:r.sprintIntent)&&r.override))throw Error('No live override');
   for(let i=1;i<lens.length;i++){
     const a=lens[i-1],b=lens[i];
     if(!b.override)continue;
     if(Math.abs(b.turn)>Math.abs(a.turn)+1e-8||b.widen>a.widen+1e-8)
       throw Error('Override increased automatic assist');
   }
   writeFileSync(join(out,'live-framing.json'),JSON.stringify({control,samples,lens,contact},null,2)+'\n');
 }else if(mode==='framing'){
   const evidence=[];
   for(const offset of [0,6,12,18,30]){
     await page.waitForFunction(()=>['framing-frozen','ended'].includes(window.fixture?.mode),null,{timeout:90000,polling:100});
     const row=await page.evaluate(()=>{
       if(fixture.mode!=='framing-frozen')throw Error('Attack did not reach sampled frame');
       return {offset:__golden.frame-fixture.hitFrame,...fixture.framing()};
     });
     if(row.offset!==offset)throw Error('Wrong hit offset');
     evidence.push(row);
     if([0,12,30].includes(offset)){
       for(const view of ['stock','taper']){
         const r=await page.evaluate(view=>fixture.framing(view),view);
         for(const k of ['frame','gameTime','simTime','hp','yaw','camera'])if(JSON.stringify(r[k])!==JSON.stringify(row[k]))throw Error('Framing moved '+k);
         await page.screenshot({path:join(out,'framing-'+offset+'-'+view+'.jpg'),type:'jpeg',quality:90});
       }
     }
     if(offset!==30)await page.evaluate(()=>{fixture.mode='counter';__golden.thaw()});
   }
   writeFileSync(join(out,'framing.json'),JSON.stringify(evidence,null,2)+'\n');
 }else{
   await page.waitForFunction(()=>['counter-frozen','ended'].includes(window.fixture?.mode),null,{timeout:90000,polling:200});
   if(await page.evaluate(()=>fixture.mode==='counter-frozen')){
     await page.screenshot({path:join(out,'counter.jpg'),type:'jpeg',quality:90});
     if(mode==='gauge'){
       const rows=[];
       for(const pick of ['base','break','blade','ring','all','gauge','trail','compact']){
         rows.push(await page.evaluate(pick=>fixture.snap(pick),pick));
         await page.screenshot({path:join(out,'frozen-'+pick+'.png'),timeout:30000});
       }
       const [first,...rest]=rows;
       for(const n of rest)for(const k of ['frame','gameTime','simTime','hp','yaw','camera'])
         if(JSON.stringify(first[k])!==JSON.stringify(n[k]))throw Error('Comparison moved '+k);
       if(!rows.find(n=>n.mode==='gauge')?.ribbonSelected)throw Error('No gauge ribbon detected');
       writeFileSync(join(out,'frozen-receipt.json'),JSON.stringify(rows,null,2)+'\n');
     }
     if(mode==='wash'){
       const original=await page.evaluate(()=>{
         const g=game,m=fixture.mob;
         return {frame:__golden.frame,sim:g.simTime,time:g.time,hp:[g.state.d.hp,m.hp],
           pos:g.camera.position.toArray(),yaw:g.cameraRig.yaw,weights:m.rig.materials.map(a=>a.flash.value.w)};
       });
       if(!original.weights.some(w=>w>.8))throw Error('Stock material flash missing');
       await page.screenshot({path:join(out,'stock.png')});
       const capped=await page.evaluate(()=>{
         const g=game,m=fixture.mob;
         for(const a of m.rig.materials)a.flash.value.w=Math.min(a.flash.value.w,.22);
         g.renderer.render(g.scene,g.camera,0);
         return {frame:__golden.frame,sim:g.simTime,time:g.time,hp:[g.state.d.hp,m.hp],
           pos:g.camera.position.toArray(),yaw:g.cameraRig.yaw,weights:m.rig.materials.map(a=>a.flash.value.w)};
       });
       for(const k of ['frame','sim','time','hp','pos','yaw'])
         if(JSON.stringify(original[k])!==JSON.stringify(capped[k]))throw Error('Comparison moved '+k);
       await page.screenshot({path:join(out,'capped.png')});
       writeFileSync(join(out,'wash.json'),JSON.stringify({original,capped},null,2)+'\n');
     }
   }
 }
 const proof=await page.evaluate(()=>({trace:fixture.trace,mode:fixture.mode}));
 writeFileSync(join(out,'trace.json'),JSON.stringify({setup,...proof},null,2)+'\n');
 console.log('Scratch output:',out);
 console.log('result',JSON.stringify({first:proof.trace.slice(0,1),locked:proof.trace.filter(r=>r.locked).slice(0,1),counter:proof.trace.find(r=>r.counterT>0),last:proof.trace.slice(-1),frames:proof.trace.length}));
} finally {await browser.close();}
