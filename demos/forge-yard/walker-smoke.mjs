// Browser proof that the authored actor moves the live right-hand weapon socket.
import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdirSync} from 'node:fs';
const url=process.argv[2]??'http://127.0.0.1:5187/demos/forge-yard/';
const out=process.argv[3]??'/tmp/walker-proof';mkdirSync(out,{recursive:true});
const args=['--enable-unsafe-swiftshader','--use-angle=swiftshader',...JSON.parse(process.env.CHROMIUM_EXTRA_ARGS??'[]')];
const b=await chromium.launch({executablePath:process.env.CHROMIUM_BINARY,args});
try{
 const p=await b.newPage({viewport:{width:402,height:874},hasTouch:true,isMobile:true,deviceScaleFactor:1});
 const errors=[];p.on('pageerror',e=>errors.push(e.message));
 await p.goto(url);const yard=p.locator('#yard');
 await p.waitForFunction(()=>document.querySelector('#yard').dataset.state==='ready');
 assert.equal(await yard.getAttribute('data-hero-rig'),'Walker');
 assert.equal(await yard.getAttribute('data-weapon-socket'),'grip_R');
 const observed=new Set();
 const pose=async name=>{await p.waitForFunction(n=>document.querySelector('#yard').dataset.heroClip===n,name,{timeout:25000});observed.add(name);};
 const stick=await p.locator('#stick').boundingBox(),cdp=await p.context().newCDPSession(p),
   x=stick.x+stick.width/2,y=stick.y+stick.height/2;
 const dir=(dx,dy)=>cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:x+dx,y:y+dy}]});
 const release=()=>cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
 await pose('Idle');
 await dir(32,0);await pose('Turn');await pose('Stride');await release();
 await p.locator('#dodge').tap();await pose('Dodge');await pose('Idle');
 const attackProof=[];
 for(const [weapon,clip] of [['014','Sweep'],['017','Chop'],['016','Thrust']]){
  await p.locator('#weapon').selectOption(weapon);
  await p.waitForFunction(id=>document.querySelector('#yard').dataset.equipped===id,weapon);
  const before=(await yard.getAttribute('data-grip-local')).split(',').map(Number);
  await p.locator('#attack').tap();await pose(clip);
  const furthest=await p.evaluate(async ({before,clip})=>{
   const o=document.querySelector('#yard');
   let max=0;
   for(let n=0;n<14;n++){
    await new Promise(requestAnimationFrame);
    if(o.dataset.heroClip!==clip)break;
    const a=o.dataset.gripLocal.split(',').map(Number);
    max=Math.max(max,Math.hypot(...a.map((c,i)=>c-before[i])));
   }
   return max;
  },{before,clip});
  assert(furthest>.045,clip+' must move the attached hand socket');
  attackProof.push({weapon,clip,maxObservedSocketTravelM:+furthest.toFixed(3)});
  await pose('Idle');
 }
 await p.locator('#reset').tap();await pose('Idle');
 await dir(0,-32);
 await p.waitForFunction(()=>{
  const d=document.querySelector('#yard').dataset;
  return Math.hypot(+d.playerX-+d.enemyX,+d.playerZ-+d.enemyZ)<1.42;
 },null,{timeout:10000});
 await release();
 await pose('Hit');
 await pose('Defeat');
 assert.equal(await yard.getAttribute('data-outcome'),'loss');
 await p.screenshot({path:out+'/walker-defeat.png'});
 assert.deepEqual(errors,[]);
 assert.equal(observed.size,9);
 console.log(JSON.stringify({portrait:[402,874],trustedTouch:true,observed:[...observed],weaponSocket:'grip_R',attackProof,defeat:true,errors},null,2));
}finally{await b.close();}
