import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdirSync} from 'node:fs';
const url=process.argv[2]??'http://127.0.0.1:5187/demos/forge-yard/';
const out=process.argv[3]??'/tmp/walker-armor';mkdirSync(out,{recursive:true});
const prior=process.argv[4];
const args=['--enable-unsafe-swiftshader','--use-angle=swiftshader',...JSON.parse(process.env.CHROMIUM_EXTRA_ARGS??'[]')];
const browser=await chromium.launch({executablePath:process.env.CHROMIUM_BINARY,args});
const report=[];
try{
 for(const variant of [...(prior?['before']:[]),'after']){
  const p=await browser.newPage({viewport:{width:402,height:874},hasTouch:true,isMobile:true,deviceScaleFactor:1});
  const errors=[];p.on('pageerror',e=>errors.push(e.message));
  if(variant==='before')await p.route('**/walker.glb',r=>r.fulfill({path:prior,contentType:'model/gltf-binary'}));
  const wait=(fn,arg)=>p.waitForFunction(fn,arg,{timeout:16000});
  await p.goto(url);await wait(()=>document.querySelector('#yard').dataset.state==='ready');
  const stick=await p.locator('#stick').boundingBox(),cdp=await p.context().newCDPSession(p);
  await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:stick.x+stick.width/2,y:stick.y+stick.height/2-31}]});
  await wait(()=>{const o=document.querySelector('#yard').dataset;return Math.hypot(+o.playerX-+o.enemyX,+o.playerZ-+o.enemyZ)<1.84;});
  await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
  await p.screenshot({path:out+'/'+variant+'-armor.png'});
  const hp=+await p.locator('#enemy-hp').textContent();
  await p.locator('#attack').tap();
  await wait(n=>+document.querySelector('#enemy-hp').textContent<n,hp);
  const after=+await p.locator('#enemy-hp').textContent(),socket=await p.locator('#yard').getAttribute('data-weapon-socket');
  assert.equal(socket,'grip_R');assert.deepEqual(errors,[]);
  report.push({variant,damage:hp-after,socket,errors});
  await p.close();
 }
 if(prior)assert.equal(report[0].damage,report[1].damage);
 console.log(JSON.stringify({portrait:[402,874],trustedTouch:true,report},null,2));
}finally{await browser.close();}
