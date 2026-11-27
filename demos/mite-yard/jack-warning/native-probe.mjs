// Read-only reference playtest. Run against a loopback build of the pinned
// source. The fresh browser context will have a disposable dev game save.
import {createRequire} from 'node:module';
import {readFileSync,writeFileSync,mkdtempSync} from 'node:fs';
import {execFileSync} from 'node:child_process';
import {join} from 'node:path';
import {tmpdir} from 'node:os';
import {pathToFileURL} from 'node:url';
const [root,dep,mode='counter'] = process.argv.slice(2);
const ref='3afcd880b397e9703e906a7e66b42e8447e59519';
if(!root||!dep||!['sidestep','counter','wash','gauge','framing'].includes(mode))
  throw Error('Usage: node native-probe.mjs FABLE_CHECKOUT DEPENDENCY_PROJECT [sidestep|counter|wash|gauge|framing]');
if(execFileSync('git',['-C',root,'rev-parse','HEAD'],{encoding:'utf8'}).trim()!==ref)
  throw Error('Wrong reference checkout');
const load=createRequire(join(dep,'package.json'));
const pw=await import(pathToFileURL(load.resolve('playwright')).href);
const chromium=pw.chromium??pw.default?.chromium;
const {default:shell}=await import(pathToFileURL(load.resolve('@sparticuz/chromium')).href);
const out=mkdtempSync(join(tmpdir(),'jack-native-'));
const onlySide=mode==='sidestep';
const browser=await chromium.launch({executablePath:await shell.executablePath(),headless:true,args:shell.args});
try {
 const ctx=await browser.newContext({viewport:{width:402,height:874},deviceScaleFactor:1,hasTouch:true,isMobile:true,serviceWorkers:'block'});
 await ctx.addInitScript({content:readFileSync(join(root,'tools/golden/init.js'),'utf8')});
 const page=await ctx.newPage();
 page.on('pageerror',e=>console.log('pageerror',String(e).slice(0,400)));
 await page.goto('http://127.0.0.1:5174/?golden&dev&q=medium',{waitUntil:'domcontentloaded'});
 await page.waitForFunction(()=>window.game?.started&&game?.mobs?.list&&game.renderer.gl.info.render.frame>0,null,{timeout:90000,polling:250});
 const setup=await page.evaluate(({onlySide,mode})=>{
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
  if(mode==='framing'){
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
      const actors=bases.map(([name,rig,labels])=>({name,pts:rigPoints(rig),sockets:Object.fromEntries(labels.map(k=>[k,rig.sockets[k].getWorldPosition(v).clone()]))}));
      // A measurement control, not a controller: stage a bounded taper on
      // these exact contact-relative samples. No input, collision or HUD changes.
      const taper={0:{plus:8,yaw:12},6:{plus:8,yaw:8},12:{yaw:4},18:{yaw:2},30:{}};
      const original=(name)=>({plus:0,yaw:0,...({taper:taper[h.frame-fixture.hitFrame],wide6:{plus:6},wide12:{plus:12},
        left4:{yaw:4},right4:{yaw:-4},left8:{yaw:8},right8:{yaw:-8},left12:{yaw:12},right12:{yaw:-12}}[name]??{})});
      const measure=(name)=>{
        const {plus,yaw}=original(name);
        probe.quaternion.copy(cam.quaternion);
        probe.rotateY(yaw*Math.PI/180);
        probe.fov=cam.fov+plus;probe.updateProjectionMatrix();probe.updateMatrixWorld(true);
        const proj=(w)=>{
          v.copy(w).applyMatrix4(probe.matrixWorldInverse);
          if(v.z>=-probe.near)return null;
          v.copy(w).project(probe);return [(1+v.x)*201,(1-v.y)*437];
        };
        return {name,fov:probe.fov,yaw,actors:Object.fromEntries(actors.map(({name,pts,sockets})=>{
          const bounds=[Infinity,Infinity,-Infinity,-Infinity];
          let outside=0,behind=0;
          for(const w of pts){
            const xy=proj(w);
            if(!xy){behind++;continue}
            const [x,y]=xy;
            if(x<0||x>402||y<0||y>874)outside++;
            bounds[0]=Math.min(bounds[0],x);bounds[1]=Math.min(bounds[1],y);
            bounds[2]=Math.max(bounds[2],x);bounds[3]=Math.max(bounds[3],y);
          }
          return [name,{bounds,vertices:pts.length,outside,behind,sockets:Object.fromEntries(Object.entries(sockets).map(([k,w])=>[k,proj(w)]))}];
        }))};
      };
      const results=['stock','wide6','wide12','left4','right4','left8','right8','left12','right12','taper'].map(measure);
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
   if((x.mode==='ramp'&&m.state==='windup'&&m.atk?.id==='charge'&&m.stT>.45)||
      (x.mode==='run'&&m.state==='recover')||(x.counterPressed&&m.hp<x.startEnemyHp))draw(...args);
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
      x.counterPressed=true;x.counterFrame=h.frame;g.input.press('attack');
    } else if(x.counterPressed&&h.frame===x.counterFrame+1)g.input.release('attack');
    if(x.counterPressed&&m.hp<x.startEnemyHp){
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
 },{onlySide,mode});
 console.log('setup',JSON.stringify(setup));
 if(onlySide){
   await page.waitForFunction(()=>window.fixture?.mode==='windup-frozen',null,{timeout:90000,polling:200});
   await page.screenshot({path:join(out,'windup.jpg'),type:'jpeg',quality:89});
   await page.keyboard.down('a');
   await page.evaluate(()=>{fixture.mode='run';__golden.thaw();});
   await page.waitForFunction(()=>window.fixture?.mode==='recover-frozen',null,{timeout:90000,polling:200});
   await page.keyboard.up('a');
   await page.screenshot({path:join(out,'recover.jpg'),type:'jpeg',quality:89});
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
