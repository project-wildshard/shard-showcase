// Cold-start benchmark plus a short-window deferred-load failure/retry test.
import {chromium} from 'playwright';
import assert from 'node:assert/strict';
const url=process.argv[2]??'http://127.0.0.1:5189/demos/forge-yard/';
const mode=process.argv[3]??'lazy';
assert(['lazy','eager'].includes(mode));
const downloadBps=450000,latencyMs=80;
const args=['--enable-unsafe-swiftshader','--use-angle=swiftshader',...JSON.parse(process.env.CHROMIUM_EXTRA_ARGS??'[]')];
const b=await chromium.launch({executablePath:process.env.CHROMIUM_BINARY,args});
const pageOptions={viewport:{width:402,height:874},hasTouch:true,isMobile:true,deviceScaleFactor:1};
const boot=async p=>{
 await p.goto(url,{waitUntil:'domcontentloaded'});
 await p.waitForFunction(()=>document.querySelector('#yard').dataset.state==='ready',null,{timeout:45000});
};
try{
 const runs=[];
 for(let i=0;i<3;i++){
  const p=await b.newPage(pageOptions),cdp=await p.context().newCDPSession(p);
  await cdp.send('Network.enable');
  await cdp.send('Network.setCacheDisabled',{cacheDisabled:true});
  await cdp.send('Network.emulateNetworkConditions',{offline:false,latency:latencyMs,downloadThroughput:downloadBps,uploadThroughput:175000});
  const t=performance.now();await boot(p);
  const readyMs=Math.round(performance.now()-t),r=await p.locator('#stick').boundingBox();
  await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:r.x+r.width/2,y:r.y+r.height/2-30}]});
  await p.waitForFunction(()=>+document.querySelector('#yard').dataset.playerZ<5.6);
  const moveMs=Math.round(performance.now()-t);
  await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
  const models=await p.evaluate(()=>performance.getEntriesByType('resource').filter(e=>/dock-(?:enemies|specialists|ordnance|foundry|terminal)\/.*\.glb$/.test(e.name)).map(e=>e.name.split('/').pop()).sort());
  if(mode==='lazy')assert.deepEqual(models,['sentry.glb']);
  runs.push({readyMs,moveMs,models});await p.close();
 }
 let retry=null;
 if(mode==='lazy'){
  const p=await b.newPage(pageOptions);let requests=0;
  await p.route('**/dock-enemies/skitter.glb',async route=>{
   requests++;
   if(requests===1)await route.fulfill({status:503,body:'Test-only temporary failure'});
   else await route.continue();
  });
  await boot(p);
  const next=p.locator('#next'),yard=p.locator('#yard');
  await next.tap();
  await p.waitForFunction(()=>document.querySelector('#notice').textContent.includes('tap Next to retry'));
  assert.equal(await yard.getAttribute('data-enemy'),'WSC-ENM-001');
  await next.tap();
  await p.waitForFunction(()=>document.querySelector('#yard').dataset.enemy==='WSC-ENM-002');
  assert.equal(requests,2);retry={firstResponse:503,thatRivalStayed:'WSC-ENM-001',recoveredRival:'WSC-ENM-002',requests};await p.close();
 }
 console.log(JSON.stringify({mode,downloadBps,latencyMs,viewport:[402,874],runs,retry},null,2));
}finally{await b.close();}
