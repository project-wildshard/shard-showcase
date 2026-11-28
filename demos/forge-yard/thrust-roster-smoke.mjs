import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdirSync,writeFileSync} from 'node:fs';
const [url='http://127.0.0.1:5187/demos/forge-yard/',out='/tmp/thrust-roster',prior,spacing='mid']=process.argv.slice(2);
mkdirSync(out,{recursive:true});
const args=['--enable-unsafe-swiftshader','--use-angle=swiftshader',...JSON.parse(process.env.CHROMIUM_EXTRA_ARGS??'[]')];
const browser=await chromium.launch({executablePath:process.env.CHROMIUM_BINARY,args});
const report=[];
try{
 for(const [id,name,want,target] of [['016','Line Pike',15,spacing==='close'?2.0:2.82],['025','Rail Needle',13,spacing==='close'?1.55:2.58]]){
  for(const mode of [...(prior?['before']:[]),'after']){
   const p=await browser.newPage({viewport:{width:402,height:874},hasTouch:true,isMobile:true,deviceScaleFactor:1});
   const errors=[];p.on('pageerror',e=>errors.push(e.message));
   if(mode==='before')await p.route('**/dist/yard.js',r=>r.fulfill({path:prior,contentType:'text/javascript'}));
   await p.addInitScript(()=>{
    const raf=requestAnimationFrame.bind(window);
    window.requestAnimationFrame=apply=>raf(t=>{
     apply(t);
     const y=document.querySelector('#yard'),d=y?.dataset;
     if(!window.hit&&!isNaN(+d?.fxImpact)&&+d.fxImpact>0&&d.fxKind==='thrust'){
      window.hit={image:y.querySelector('canvas').toDataURL(),axes:d.thrustAxes?.split(',').map(Number)??null,
       gap:d.thrustGap?.split(',').map(Number)??null,distance:Math.hypot(d.playerX-d.enemyX,d.playerZ-d.enemyZ),
       hp:+document.querySelector('#enemy-hp').textContent,clip:d.heroClip};
     }
    });
   });
   const wait=(fn,arg)=>p.waitForFunction(fn,arg,{timeout:16000});
   await p.goto(url);await wait(()=>document.querySelector('#yard').dataset.state==='ready');
   await p.locator('#weapon').selectOption(id);await wait(t=>document.querySelector('#yard').dataset.equipped===t,id);
   const s=await p.locator('#stick').boundingBox(),c=await p.context().newCDPSession(p);
   await c.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:s.x+s.width/2,y:s.y+s.height/2-31}]});
   await wait(t=>{const d=document.querySelector('#yard').dataset;return Math.hypot(d.playerX-d.enemyX,d.playerZ-d.enemyZ)<t;},target);
   await c.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
   const before=+await p.locator('#enemy-hp').textContent();await p.locator('#attack').tap();
   await wait(()=>window.hit);
   const {image,axes,gap,distance,hp,clip}=await p.evaluate(()=>window.hit);
   assert.equal(before-hp,want);assert(image.length>14000);
   if(mode==='after'){
    assert(axes?.[0]>25&&axes[1]<.5&&axes[2]<.001,'aim reduces angle without moving the grip');
    assert(gap?.[0]>gap[1]&&gap[1]>=0,'report residual tip distance independently from aim');
   }else{assert.equal(axes,null);}
   assert.deepEqual(errors,[]);
   writeFileSync(out+'/'+id+'-'+mode+'.png',Buffer.from(image.split(',')[1],'base64'));
   report.push({mode,id,name,clip,damage:before-hp,distance:+distance.toFixed(3),angleBeforeDegrees:axes?.[0]??null,
    angleAfterDegrees:axes?.[1]??null,gripSlipMeters:axes?.[2]??null,tipGapBeforeMeters:gap?.[0]??null,tipGapAfterMeters:gap?.[1]??null,tipAxialErrorMeters:gap?.[2]??null,errors});
   await p.close();
  }
 }
 console.log(JSON.stringify({trustedTouch:true,viewport:[402,874],spacing,report},null,2));
}finally{await browser.close();}
