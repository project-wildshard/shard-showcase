import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdirSync} from 'node:fs';

const [url='http://127.0.0.1:5187/demos/forge-yard/',out='/tmp/double-shift']=process.argv.slice(2);
mkdirSync(out,{recursive:true});
const browser=await chromium.launch({executablePath:process.env.CHROMIUM_BINARY,
 args:['--enable-unsafe-swiftshader','--use-angle=swiftshader',...JSON.parse(process.env.CHROMIUM_EXTRA_ARGS??'[]')]});
try{
 const page=await browser.newPage({viewport:{width:402,height:874},hasTouch:true,isMobile:true,deviceScaleFactor:1});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 const yard=page.locator('#yard'), wait=(fn,arg)=>page.waitForFunction(fn,arg,{timeout:15000});
 const testAttr=(key,value)=>wait(([k,v])=>document.querySelector('#yard').dataset[k]===v,[key,value]);
 const hp=async()=>Number(await page.locator('#hero-hp').textContent());
 await page.goto(url);
 await testAttr('state','ready');
 assert.equal(await yard.getAttribute('data-trial'),null);
 assert(await page.locator('#rival').isVisible());
 await page.locator('#trial-link').tap();
 await testAttr('state','ready');
 await testAttr('round','1');
 assert.equal(await hp(),120);
 assert(!(await page.locator('#rival').isVisible()));
 assert(!(await page.locator('#next').isVisible()));
 const models=await page.evaluate(()=>performance.getEntriesByType('resource').filter(e=>/dock-enemies\/.*\.glb$/.test(e.name)).map(e=>e.name.split('/').pop()));
 assert.deepEqual(models,['sentry.glb']);
 const stick=await page.locator('#stick').boundingBox(),x=stick.x+stick.width/2,y=stick.y+stick.height/2;
 const cdp=await page.context().newCDPSession(page);
 const f=(type,...touchPoints)=>cdp.send('Input.dispatchTouchEvent',{type,touchPoints});
 const position=()=>yard.evaluate(e=>{
  const {playerX,playerZ,enemyX,enemyZ,outcome}=e.dataset;
  return {dx:+enemyX-playerX,dz:+enemyZ-playerZ,outcome};
 });
 const close=async()=>{
  const {dx,dz}=await position(),d=Math.hypot(dx,dz);
  if(d<1.88)return;
  await f('touchStart',{x:x+dx/d*32,y:y+dz/d*32});
  try{await wait(()=>{const e=document.querySelector('#yard').dataset;return e.outcome||Math.hypot(e.enemyX-e.playerX,e.enemyZ-e.playerZ)<1.86;});}
  finally{await f('touchEnd');}
 };
 const fight=async(path,outcome)=>{
  for(let j=0;j<12;j++){
   if((await position()).outcome)break;
   await close();
   if((await position()).outcome)break;
   if(j===0)await page.screenshot({path:out+'/'+path+'.png'});
   await page.locator('#attack').tap();
   await page.waitForTimeout(895);
  }
  assert.equal((await position()).outcome,outcome);
 };
 await page.locator('#weapon').selectOption('017');
 await testAttr('equipped','017');
 await close();
 // Let one real hit land so the health carry cannot pass trivially.
 const hitFrom=await hp();
 await wait(prior=>+document.querySelector('#hero-hp').textContent<prior,hitFrom);
 await fight('gate-sentry','clear');
 const afterFirst=await hp();assert(afterFirst>0&&afterFirst<120);
 await page.screenshot({path:out+'/first-gate.png'});
 await page.waitForTimeout(650);
 assert.equal(await hp(),afterFirst);
 await page.locator('#win-next').tap();
 await testAttr('round','2');
 assert.equal(await hp(),afterFirst);
 assert.equal(await yard.getAttribute('data-equipped'),'017');
 await fight('rivet-skitter','win');
 const afterSecond=await hp();assert(afterSecond>0&&afterSecond<=afterFirst);
 const result=await page.locator('#win-body').textContent();
 assert.match(result,new RegExp(afterSecond+' HP left · [0-9.]+s in the arena'));
 await page.screenshot({path:out+'/double-shift-clear.png'});
 await page.locator('#win-next').tap();
 await testAttr('round','1');await testAttr('outcome','');
 assert.equal(await hp(),120);
 assert.equal(await page.locator('#enemy-hp').textContent(),'92');
 await close();
 // Failure may not unlock the next gate; verify a real defeat and replay.
 await page.waitForFunction(()=>document.querySelector('#yard').dataset.outcome==='loss',null,{timeout:70000});
 assert.equal(await page.locator('#win-next').textContent(),'Retry trial');
 await page.locator('#win-next').tap();
 await testAttr('outcome','');await testAttr('round','1');assert.equal(await hp(),120);
 assert.deepEqual(errors,[]);
 console.log(JSON.stringify({viewport:[402,874],trustedTouch:true,rivals:['Gate Sentry','Rivet Skitter'],afterFirst,carriedHp:afterFirst,afterSecond,result,resetChecked:true,lossChecked:true,lazyLoad:true,freeSparring:true,errors},null,2));
}finally{await browser.close();}
