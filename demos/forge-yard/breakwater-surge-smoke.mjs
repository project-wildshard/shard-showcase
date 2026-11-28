import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdirSync,writeFileSync} from 'node:fs';
import {SURGE} from './breakwater-surge.mjs';
const [url='http://127.0.0.1:5187/demos/forge-yard/?arena=breakwater',out='/tmp/breakwater-surge']=process.argv.slice(2);
mkdirSync(out,{recursive:true});
const args=['--enable-unsafe-swiftshader','--use-angle=swiftshader',...JSON.parse(process.env.CHROMIUM_EXTRA_ARGS??'[]')];
const browser=await chromium.launch({executablePath:process.env.CHROMIUM_BINARY,args});
const report=[];
try{
 for(const scenario of ['stay','step-out']){
  const page=await browser.newPage({viewport:{width:402,height:874},hasTouch:true,isMobile:true,deviceScaleFactor:1});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.addInitScript(()=>{
   const raf=requestAnimationFrame.bind(window);window.tideFrames={};window.washed=false;
   window.requestAnimationFrame=apply=>raf(t=>{
    apply(t);
    const y=document.querySelector('#yard'),d=y?.dataset;
    if(!d?.surgePhase)return;
    const save=key=>{
     if(window.tideFrames[key])return;
     const canvas=y.querySelector('canvas');
     window.tideFrames[key]={
      image:canvas.toDataURL(),x:+d.playerX,z:+d.playerZ,hp:+document.querySelector('#hero-hp').textContent,
      notice:document.querySelector('#tide').textContent,front:d.surgeFront?+d.surgeFront:null
     };
    };
    if(d.surgePhase==='warn')save('warning');
    if(d.surgePhase==='wash'){
     window.washed=true;
     if(Math.abs(Number(d.surgeFront)-Number(d.playerZ)-.32)<.22)save('pass');
    }
    if(d.surgeHits==='1')save('contact');
   });
  });
  const wait=(fn,arg)=>page.waitForFunction(fn,arg,{timeout:20000});
  await page.goto(url);
  await wait(()=>document.querySelector('#yard')?.dataset.state==='ready');
  const yard=page.locator('#yard');
  assert.equal(await yard.getAttribute('data-scene-kit'),'signal-breakwater');
  const stick=await page.locator('#stick').boundingBox(),cdp=await page.context().newCDPSession(page);
  const start=(dx,dy)=>cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:stick.x+stick.width/2+dx*31,y:stick.y+stick.height/2+dy*31}]});
  const stop=()=>cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
  await start(-1,0);await wait(()=>+document.querySelector('#yard').dataset.playerX<=-5.24);await stop();
  await wait(()=>document.querySelector('#yard').dataset.surgePhase==='warn');
  assert.match(await page.locator('#tide').textContent(),/TIDE INCOMING/);
  const xAtWarning=Number(await yard.getAttribute('data-player-x'));
  assert(Math.abs(xAtWarning-SURGE.x)<SURGE.halfWidth);
  if(scenario==='step-out'){
   await start(1,0);await wait(()=>+document.querySelector('#yard').dataset.playerX>=-4.2);await stop();
  }
  await wait(()=>window.washed&&document.querySelector('#yard').dataset.surgePhase==='idle');
  const hits=Number(await yard.getAttribute('data-surge-hits'));
  assert.equal(hits,scenario==='stay'?1:0,scenario);
  const frames=await page.evaluate(()=>window.tideFrames);
  assert(frames.warning?.image.length>14000&&frames.pass?.image.length>14000);
  assert.equal(Boolean(frames.contact),scenario==='stay');
  for(const [key,f] of Object.entries(frames)){
   writeFileSync(out+'/'+scenario+'-'+key+'.png',Buffer.from(f.image.split(',')[1],'base64'));
   delete f.image;
  }
  assert.deepEqual(errors,[]);
  report.push({scenario,xAtWarning,hits,hpAfter:Number(await page.locator('#hero-hp').textContent()),frames,errors});
  await page.close();
 }
 console.log(JSON.stringify({viewport:[402,874],trustedTouch:true,damagePerWash:SURGE.damage,report},null,2));
}finally{await browser.close();}
