import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdirSync,writeFileSync} from 'node:fs';

const [url='http://127.0.0.1:5239/demos/forge-yard/',out='/tmp/kiln-smoke']=process.argv.slice(2);
mkdirSync(out,{recursive:true});
const browser=await chromium.launch({executablePath:process.env.CHROMIUM_BINARY,
 args:['--enable-unsafe-swiftshader','--use-angle=swiftshader',...JSON.parse(process.env.CHROMIUM_EXTRA_ARGS??'[]')]});
const trials=[];
try{
 for(const [mode,threshold,want] of [['guarded',3.36,6],['exposed',1.88,15]]){
  const p=await browser.newPage({viewport:{width:402,height:874},hasTouch:true,isMobile:true,deviceScaleFactor:1});
  const errors=[];p.on('pageerror',e=>errors.push(e.message));
  const wait=(fn,arg)=>p.waitForFunction(fn,arg,{timeout:18000});
  await p.goto(url);
  await wait(()=>document.querySelector('#yard').dataset.state==='ready');
  await p.locator('#rival').selectOption({label:'Kiln Warden'});
  await wait(()=>document.querySelector('#yard').dataset.enemy==='WSC-ENM-006');
  await p.locator('#weapon').selectOption('016');
  await wait(()=>document.querySelector('#yard').dataset.equipped==='016');
  const stick=await p.locator('#stick').boundingBox(),cdp=await p.context().newCDPSession(p);
  await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:stick.x+stick.width/2,y:stick.y+stick.height/2-31}]});
  await wait(t=>{const d=document.querySelector('#yard').dataset;return Math.hypot(d.playerX-d.enemyX,d.playerZ-d.enemyZ)<t;},threshold);
  await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
  if(mode==='exposed')await wait(()=>{const x=document.querySelector('#yard').dataset;return x.kilnGuard==='open'&&+x.kilnGap>.58;});
  const prior=await p.locator('#yard').evaluate(y=>({state:y.dataset.kilnGuard,travel:+y.dataset.kilnGap,pose:y.dataset.pose,
    distance:+Math.hypot(y.dataset.playerX-y.dataset.enemyX,y.dataset.playerZ-y.dataset.enemyZ).toFixed(3)}));
  assert.equal(prior.state,mode==='guarded'?'closed':'open');
  assert.equal(prior.travel,mode==='guarded'?0:.60);
  await p.screenshot({path:out+'/'+mode+'.png'});
  const before=+await p.locator('#enemy-hp').textContent();
  await p.locator('#attack').tap();
  await wait(h=>+document.querySelector('#enemy-hp').textContent<h,before);
  const after=+await p.locator('#enemy-hp').textContent();
  assert.equal(before-after,want);
  if(mode==='guarded')assert.equal(await p.locator('#yard').getAttribute('data-variant-cue'),'shield');
  else{
   await p.locator('#reset').tap();
   await wait(()=>{const x=document.querySelector('#yard').dataset;return x.kilnGuard==='closed'&&+x.kilnGap===0;});
  }
  assert.deepEqual(errors,[]);
  trials.push({mode,...prior,damage:before-after,restartChecked:mode==='exposed',errors});
  await p.close();
 }
 console.log(JSON.stringify({viewport:[402,874],trustedTouch:true,weapon:'Line Pike',trials},null,2));
}finally{await browser.close();}
