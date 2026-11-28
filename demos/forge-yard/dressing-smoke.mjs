import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdirSync} from 'node:fs';
const current=process.argv[2]??'http://127.0.0.1:5187/demos/forge-yard/';
const out=process.argv[3]??'/tmp/dressing-proof';const baseline=process.argv[4];mkdirSync(out,{recursive:true});
const args=['--enable-unsafe-swiftshader','--use-angle=swiftshader',...JSON.parse(process.env.CHROMIUM_EXTRA_ARGS??'[]')];
const browser=await chromium.launch({executablePath:process.env.CHROMIUM_BINARY,args});
const wait=(page,cb,arg)=>page.waitForFunction(cb,arg,{timeout:18000});
async function inspect(url,name,width=402,height=874){
 const page=await browser.newPage({viewport:{width,height},hasTouch:true,isMobile:true,deviceScaleFactor:1});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(url);
 await wait(page,()=>document.querySelector('#yard').dataset.state==='ready');
 const y=page.locator('#yard'),stick=await page.locator('#stick').boundingBox();
 const cdp=await page.context().newCDPSession(page);
 const start=()=>cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:stick.x+stick.width/2,y:stick.y+stick.height/2-30}]});
 const stop=()=>cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
 const grab=()=>y.evaluate(el=>{
  const d=el.dataset;
  return {player:[+d.playerX,+d.playerZ],rival:[+d.enemyX,+d.enemyZ],framing:['playerViewX','playerViewY','enemyViewX','enemyViewY'].map(n=>+d[n]),kit:d.sceneKit??'blockout',
   batches:+d.sceneBatches||null,instances:+d.sceneInstances||null,covers:+d.sceneCover||null};
 });
 await start();
 await wait(page,()=>+document.querySelector('#yard').dataset.playerZ<=3.20);
 await stop();
 const sample=await grab();
 await page.screenshot({path:out+'/'+name+'-approach.png'});
 if(name!=='baseline'){
  assert.equal(sample.kit,'foundry-evening');assert.equal(sample.covers,4);
  assert(sample.batches<=42&&sample.instances>220);
 }
 let hit=false,relay=false;
 if(name==='foundry'){
  await start();
  await wait(page,()=>{
   const d=document.querySelector('#yard').dataset;
   return Math.hypot(+d.playerX-+d.enemyX,+d.playerZ-+d.enemyZ)<1.85;
  });
  await stop();
  const before=+(await page.locator('#enemy-hp').textContent());await page.locator('#attack').tap();
  await wait(page,h=>+document.querySelector('#enemy-hp').textContent<h,before);hit=true;
  await page.screenshot({path:out+'/foundry-hit.png'});
  await page.locator('#rival').selectOption('14');
  await wait(page,()=>document.querySelector('#yard').dataset.enemy==='WSC-ENM-015');
  await start();
  await wait(page,()=>+document.querySelector('#yard').dataset.playerZ<3.2);
  await stop();
  await wait(page,()=>document.querySelector('#notice').textContent.includes('LANTERNS'));
  relay=true;await page.screenshot({path:out+'/foundry-lantern-cue.png'});
 }
 assert.deepEqual(errors,[]);assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
 await page.close();return {viewport:[width,height],sample,hit,relay,errors};
}
try{
 const old=baseline?await inspect(baseline,'baseline'):null;
 const portrait=await inspect(current,'foundry');
 const wide=await inspect(current,'foundry-wide',960,680);
 if(old)assert(Math.abs(old.sample.player[1]-portrait.sample.player[1])<.55);
 console.log(JSON.stringify({trustedTouch:true,old,portrait,wide},null,2));
}finally{await browser.close();}
