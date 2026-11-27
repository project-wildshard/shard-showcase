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
if(!root||!dep||!['sidestep','counter','wash'].includes(mode))
  throw Error('Usage: node native-probe.mjs FABLE_CHECKOUT DEPENDENCY_PROJECT [sidestep|counter|wash]');
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
 const setup=await page.evaluate(onlySide=>{
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
    if(x.counterPressed&&m.hp<x.startEnemyHp){x.mode='counter-frozen';h.freeze();}
    if(h.frame>590){x.mode='ended';h.freeze();}
  };
  return {site,hp:g.state.d.hp,enabled:g.combat.enabled,god:g.state.god,touch:g.input.isTouch,view:g.cameraRig.view};
 },onlySide);
 console.log('setup',JSON.stringify(setup));
 if(onlySide){
   await page.waitForFunction(()=>window.fixture?.mode==='windup-frozen',null,{timeout:90000,polling:200});
   await page.screenshot({path:join(out,'windup.jpg'),type:'jpeg',quality:89});
   await page.keyboard.down('a');
   await page.evaluate(()=>{fixture.mode='run';__golden.thaw();});
   await page.waitForFunction(()=>window.fixture?.mode==='recover-frozen',null,{timeout:90000,polling:200});
   await page.keyboard.up('a');
   await page.screenshot({path:join(out,'recover.jpg'),type:'jpeg',quality:89});
 }else{
   await page.waitForFunction(()=>['counter-frozen','ended'].includes(window.fixture?.mode),null,{timeout:90000,polling:200});
   if(await page.evaluate(()=>fixture.mode==='counter-frozen')){
     await page.screenshot({path:join(out,'counter.jpg'),type:'jpeg',quality:90});
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
