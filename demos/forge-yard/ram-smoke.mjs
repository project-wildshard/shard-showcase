import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdirSync} from 'node:fs';
import {COVER as stock} from './arena.mjs';
const url=process.argv[2]??'http://127.0.0.1:5187/demos/forge-yard/';
const out=process.argv[3]??'/tmp/ram-proof';mkdirSync(out,{recursive:true});
const b=await chromium.launch({executablePath:process.env.CHROMIUM_BINARY,args:['--enable-unsafe-swiftshader','--use-angle=swiftshader',...JSON.parse(process.env.CHROMIUM_EXTRA_ARGS??'[]')]});
try{
 const p=await b.newPage({viewport:{width:402,height:874},hasTouch:true,isMobile:true,deviceScaleFactor:1});
 const errors=[];p.on('pageerror',e=>errors.push(e.message));
 const o=p.locator('#yard'),w=(fn,arg,t=16000)=>p.waitForFunction(fn,arg,{timeout:t});
 await p.goto(url);
 await w(()=>document.querySelector('#yard').dataset.state==='ready');
 await p.locator('#rival').selectOption('3');
 await w(()=>document.querySelector('#yard').dataset.enemy==='WSC-ENM-004');
 await p.locator('#weapon').selectOption('021');
 await w(()=>document.querySelector('#yard').dataset.equipped==='021');
 const c=await p.context().newCDPSession(p),s=await p.locator('#stick').boundingBox(),x=s.x+s.width/2,y=s.y+s.height/2;
 const start=(u,v)=>c.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:x+u*31,y:y+v*31}]});
 const stop=()=>c.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
 const get=()=>o.evaluate(el=>{const d=el.dataset;return {x:+d.playerX,z:+d.playerZ,ex:+d.enemyX,ez:+d.enemyZ,out:d.outcome,pose:d.pose,
  h:d.heroClip,hp:+document.querySelector('#enemy-hp').textContent,hero:+document.querySelector('#hero-hp').textContent,impact:+d.fxImpact||0};});
 let hits=0,taps=0,steps=0,totalHit=0,stalled=0; const rows=[];
 for(let i=0;i<65;i++){
  const a=await get();
  if(a.out==='win')break;
  assert.notEqual(a.out,'loss');
  const dx=a.ex-a.x,dz=a.ez-a.z,d=Math.hypot(dx,dz);
  if(i%4===0)rows.push({i,dist:+d.toFixed(2),...a});
  const [u,v]=d?[dx/d,dz/d]:[0,1];
  const obstruction=stock.find(([cx,cz,r])=>{
   const t=Math.max(0,Math.min(d,(cx-a.x)*u+(cz-a.z)*v));
   return Math.hypot(cx-(a.x+u*t),cz-(a.z+v*t))<r+.31;
  });
  if(d<=3.20&&!obstruction){
   await p.locator('#attack').tap();taps++;
   await w(()=>document.querySelector('#yard').dataset.heroClip==='Thrust',null,5000).catch(()=>{});
   await w(()=>document.querySelector('#yard').dataset.heroClip!=='Thrust',null,7000);
   const m=await get();if(m.hp<a.hp){hits++;totalHit+=a.hp-m.hp;}
   if(hits===1&&m.hp<a.hp)await p.screenshot({path:out+'/ram-first-confirmed-hit.png'});
  }else{
   let f=u,g=v;
   if(obstruction){
    const [cx,cz,r]=obstruction;
    const sign=((cx-a.x)*(-v)+(cz-a.z)*u)>0?-1:1;
    const ox=a.x-cx,oz=a.z-cz,length=Math.hypot(ox,oz);
    if(length<r+.51){
     f=(ox/length)*.17-v*sign;g=(oz/length)*.17+u*sign;
    }else{f=u*.51-v*.88*sign;g=v*.51+u*.88*sign;}
   }else if(stalled%3===2){f=u*.66-v*.76;g=v*.66+u*.76;}
   const m=Math.hypot(f,g);await start(f/m,g/m);
   await w(a=>{const o=document.querySelector('#yard').dataset;return Math.hypot(+o.playerX-a.x,+o.playerZ-a.z)>.63;},a,2300).catch(()=>{});
   await stop();steps++;
   const t=await get();stalled=Math.hypot(t.x-a.x,t.z-a.z)<.21?stalled+1:0;
  }
 }
 const final=await get();console.log(JSON.stringify({trustedTouch:true,viewport:[402,874],opponent:'WSC-ENM-004',weapon:'021',hits,taps,steps,totalHit,final,rows,errors},null,2));
 assert.equal(final.out,'win');assert.equal(final.hp,0);assert.deepEqual(errors,[]);
}finally{await b.close();}
