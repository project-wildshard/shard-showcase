import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdirSync} from 'node:fs';
const url=process.argv[2]??'http://127.0.0.1:5187/demos/forge-yard/';
const out=process.argv[3]??'/tmp/impact-proof';mkdirSync(out,{recursive:true});
const args=['--enable-unsafe-swiftshader','--use-angle=swiftshader',...JSON.parse(process.env.CHROMIUM_EXTRA_ARGS??'[]')];
const b=await chromium.launch({executablePath:process.env.CHROMIUM_BINARY,args});
try{
 const p=await b.newPage({viewport:{width:402,height:874},hasTouch:true,isMobile:true,deviceScaleFactor:1});
 const errors=[];p.on('pageerror',e=>errors.push(e.message));
 const wait=(fn,arg)=>p.waitForFunction(fn,arg,{timeout:15000}),yard=p.locator('#yard');
 await p.goto(url);await wait(()=>document.querySelector('#yard').dataset.state==='ready');
 assert.equal(await yard.getAttribute('data-fx-sockets'),'grip_socket,tip_socket');
 const stick=await p.locator('#stick').boundingBox(),cdp=await p.context().newCDPSession(p),x=stick.x+stick.width/2,y=stick.y+stick.height/2;
 async function approach(distance){
  await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x,y:y-31}]});
  await wait(d=>{const o=document.querySelector('#yard').dataset;return Math.hypot(+o.playerX-+o.enemyX,+o.playerZ-+o.enemyZ)<d;},distance);
  await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
 }
 const serial=()=>yard.evaluate(e=>+e.dataset.fxImpact||0);
 const arm=()=>p.evaluate(()=>{
  window.fxObserver?.disconnect();const e=document.querySelector('#yard');
  window.fxSample={trail:0,particles:0};
  window.fxObserver=new MutationObserver(()=>{
   window.fxSample.trail=Math.max(window.fxSample.trail,+e.dataset.fxTrailSegments||0);
   window.fxSample.particles=Math.max(window.fxSample.particles,+e.dataset.fxParticles||0);
  });window.fxObserver.observe(e,{attributes:true});
 });
 const equip=async id=>{await p.locator('#weapon').selectOption(id);await wait(id=>document.querySelector('#yard').dataset.equipped===id,id);};
 const attack=p.locator('#attack');await arm();
 const missSerial=await serial();
 await attack.tap();await wait(()=>+document.querySelector('#yard').dataset.fxTrailSegments>0);
 await wait(()=>document.querySelector('#yard').dataset.heroClip==='Idle');
 assert.equal(await serial(),missSerial,'a miss cannot create a contact burst');
 assert.equal((await p.evaluate(()=>window.fxSample)).particles,0);
 const hits=[];
 for(const [weapon,kind] of [['014','sweep'],['017','chop'],['016','thrust'],['025','block']]){
  if(kind==='block'){
   await p.locator('#rival').selectOption('5');
   await wait(()=>document.querySelector('#yard').dataset.enemy==='WSC-ENM-006');
  }else await p.locator('#reset').tap();
  await equip(weapon);await approach(kind==='block'?3.00:1.82);
  const before=await serial(),hp=+await p.locator('#enemy-hp').textContent();
  await arm();await attack.tap();
  await wait(last=>(+document.querySelector('#yard').dataset.fxImpact||0)>last,before);
  await wait(()=>{const o=document.querySelector('#yard').dataset;return +o.fxParticles>0&&+o.fxAgeMs>=57;});
  await p.screenshot({path:out+'/impact-'+kind+'.png'});
  const e=await yard.evaluate(n=>{
   const o=n.dataset;
   return {anchor:o.fxAnchor.split(',').map(Number),enemy:[+o.enemyX,+o.enemyZ],kind:o.fxKind,phase:o.fxPhase,particles:+o.fxParticles};
  });
  assert.equal(e.kind,kind);assert(e.anchor[1]>.17&&e.anchor[1]<2.3);
  const gap=Math.hypot(e.anchor[0]-e.enemy[0],e.anchor[2]-e.enemy[1]);
  assert(gap>.30&&gap<.89);assert(+await p.locator('#enemy-hp').textContent()<hp);
  await wait(()=>+document.querySelector('#yard').dataset.fxParticles===0);
  const peak=await p.evaluate(()=>window.fxSample);
  assert(peak.trail>0&&peak.trail<=8);assert(peak.particles>0&&peak.particles<=11);
  hits.push({weapon,kind,localAnchorRadius:+gap.toFixed(3),height:e.anchor[1],maxTrailSegments:peak.trail,maxParticles:peak.particles,cleared:true});
 }
 assert.deepEqual(errors,[]);
 console.log(JSON.stringify({viewport:[402,874],trustedTouch:true,missTrailOnly:true,authoredSockets:['grip_socket','tip_socket'],hits,errors},null,2));
}finally{await b.close();}
