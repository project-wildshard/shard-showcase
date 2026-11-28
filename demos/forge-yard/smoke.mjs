// Run with a local static server from the repository root. Chromium must have WebGL.
import {chromium} from 'playwright';
import {mkdirSync} from 'node:fs';
import assert from 'node:assert/strict';
const base=process.argv[2]??'http://127.0.0.1:5187/demos/forge-yard/';
const out=process.argv[3]??'/tmp/forge-yard-proof';mkdirSync(out,{recursive:true});
const args=['--enable-unsafe-swiftshader','--use-angle=swiftshader'];
if(process.env.CHROMIUM_EXTRA_ARGS)args.push(...JSON.parse(process.env.CHROMIUM_EXTRA_ARGS));
const browser=await chromium.launch({executablePath:process.env.CHROMIUM_BINARY,args});
try{
 const page=await browser.newPage({viewport:{width:402,height:874},hasTouch:true,isMobile:true,deviceScaleFactor:1});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(base);
 const yard=page.locator('#yard');
 await page.waitForFunction(()=>document.querySelector('#yard').dataset.state==='ready',null,{timeout:45000});
 assert.equal(await yard.getAttribute('data-equipped'),'014');
 assert.equal(await page.locator('#weapon option').count(),12);
 const stick=await page.locator('#stick').boundingBox(),cdp=await page.context().newCDPSession(page);
 const x=stick.x+stick.width/2,y=stick.y+stick.height/2;
 const f=(type,...touchPoints)=>cdp.send('Input.dispatchTouchEvent',{type,touchPoints});
 await page.locator('#weapon').selectOption('017');
 await page.waitForFunction(()=>document.querySelector('#yard').dataset.equipped==='017');
 const victories=[];
 for(let n=0;n<12;n++){
  if(n)await page.locator('#win-next').tap();
  const label=await page.locator('#enemy-name').textContent();
  const track=()=>yard.evaluate(e=>{
   const d=e.dataset;
   return {x:+d.playerX,z:+d.playerZ,ex:+d.enemyX,ez:+d.enemyZ,outcome:d.outcome,pose:d.pose};
  });
  await f('touchStart',{x,y:y-32});
  await page.waitForFunction(()=>+document.querySelector('#yard').dataset.playerZ<3.2,null,{timeout:10000});
  await f('touchEnd');
  if(!n)await page.screenshot({path:out+'/forge-yard-sentry-approach.png'});
  let moves=1, taps=0;
  for(let trial=0;trial<25;trial++){
   const {x:px,z:pz,ex,ez,outcome}=await track();
   if(outcome==='win')break;
   assert.notEqual(outcome,'loss',label+' defeated the test player');
   const d=Math.hypot(ex-px,ez-pz);
   if(d>2.1){
    await f('touchStart',{x:x+(ex-px)/d*31,y:y+(ez-pz)/d*31});
    await page.waitForTimeout(Math.min(545,Math.max(190,(d-1.65)*210)));
    await f('touchEnd');moves++;
   }else{
    await page.locator('#attack').tap();taps++;
    if(taps===1){await page.waitForTimeout(490);await page.screenshot({path:out+'/forge-yard-match-'+n+'.png'});await page.waitForTimeout(720);}
    else await page.waitForTimeout(1160);
   }
  }
  assert.equal(await yard.getAttribute('data-outcome'),'win',label+' must reach defeat via the on-screen controls');
  assert.equal(await yard.getAttribute('data-pose'),'Defeat');
  assert.equal(await page.locator('#enemy-hp').textContent(),'0');
  victories.push({enemy:label,taps,moves,heroHp:+await page.locator('#hero-hp').textContent()});
 }
 await page.screenshot({path:out+'/forge-yard-last-win.png'});
 await page.locator('#win-next').tap();
 await page.locator('#dodge').tap();
 assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
 const weaponsHit=[];
 for(let i=14;i<=25;i++){
  const id=String(i).padStart(3,'0');
  await page.locator('#reset').tap();
  await page.locator('#weapon').selectOption(id);
  await page.waitForFunction(id=>document.querySelector('#yard').dataset.equipped===id,id);
  await f('touchStart',{x,y:y-32});
  await page.waitForFunction(()=>{
   const d=document.querySelector('#yard').dataset;
   return Math.hypot(+d.playerX-+d.enemyX,+d.playerZ-+d.enemyZ)<1.92;
  },null,{timeout:10000});
  await f('touchEnd');
  const before=Number(await page.locator('#enemy-hp').textContent());
  await page.locator('#attack').tap();
  await page.waitForFunction(h=>+document.querySelector('#enemy-hp').textContent<h,before,{timeout:5000});
  weaponsHit.push(id);
 }
 const inspectedVariants=[];
 const mode=['rusher','bulwark','feinter','echo','overload'];
 for(let n=0;n<12;n++){
  if(n)await page.locator('#next').tap();
  const type='WSC-ENM-'+String(n+1).padStart(3,'0');
  for(const id of mode){
   await page.locator('#variant').selectOption(id);
   const want=type+'-'+id;
   await page.waitForFunction(want=>{
    const d=document.querySelector('#yard').dataset;
    return d.enemy===want&&+d.variantParts>0;
   },want,{timeout:5000});
   inspectedVariants.push(want);
   if(n===0&&id==='rusher')await page.waitForFunction(()=>document.querySelector('#yard').dataset.variantCue==='rush',null,{timeout:5000});
   if(n===5&&id==='bulwark'){
    await f('touchStart',{x,y:y-30});
    await page.waitForFunction(()=>+document.querySelector('#yard').dataset.playerZ<3.75,null,{timeout:10000});
    await f('touchEnd');
    await page.screenshot({path:out+'/forge-yard-bulwark-kit.png'});
   }
  }
  await page.locator('#variant').selectOption('');
 }
 assert.equal(inspectedVariants.length,60);
 assert.deepEqual(errors,[]);
 console.log(JSON.stringify({trustedTouch:true,victories,weaponModelsLoaded:12,weaponsHit,inspectedVariants,viewport:[402,874],errors},null,2));
}finally{await browser.close();}
