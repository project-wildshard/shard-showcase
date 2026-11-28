import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdirSync} from 'node:fs';
const [url='http://127.0.0.1:5250/demos/executioner-look/',output='/tmp/executioner-look']=process.argv.slice(2);
mkdirSync(output,{recursive:true});
const browser=await chromium.launch({executablePath:process.env.CHROMIUM_BINARY,
 args:['--enable-unsafe-swiftshader','--use-angle=swiftshader',...JSON.parse(process.env.CHROMIUM_EXTRA_ARGS??'[]')]});
const evidence=[];
try{
 for(const [label,w,h,touch] of [['desktop',1280,720,false],['phone',402,874,true]]){
  const page=await browser.newPage({viewport:{width:w,height:h},hasTouch:touch,isMobile:touch,deviceScaleFactor:1});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(url);
  const state=()=>page.locator('#stage').evaluate(el=>Object.assign({},el.dataset));
  await page.waitForFunction(()=>['ready','error'].includes(document.querySelector('#stage').dataset.state),null,{timeout:35000});
  const ds=await state();assert.equal(ds.state,'ready',await page.locator('#status').textContent());
  assert.equal(ds.viewport,w+'x'+h);assert(+ds.modelHeight>1.75&&+ds.modelHeight<2.15);
  assert(+ds.triangles>5000&&+ds.triangles<=46000);
  assert(+ds.heightPixels>150&&+ds.heightPixels<h*.64);
  await page.screenshot({path:`${output}/${label}-distance.png`});
  const base=+ds.heightPixels;const views=[];
  for(const name of ['Close','Profile','Rear']){
   const el=page.getByRole('button',{name,exact:true});
   if(touch)await el.tap();else await el.click();
   const s=await state();assert.equal(s.view,name.toLowerCase());assert(+s.heightPixels>base*1.55&&+s.heightPixels<h*.97);
   await page.screenshot({path:`${output}/${label}-${s.view}.png`});
   views.push({name:s.view,heightPixels:+s.heightPixels});
  }
  assert.deepEqual(errors,[]);
  evidence.push({viewport:[w,h],trustedTouch:touch,meshHeightM:+ds.modelHeight,triangles:+ds.triangles,distanceHeightPixels:base,views,errors});
  await page.close();
 }
 console.log(JSON.stringify({visualReviewOnly:true,staticPose:true,cases:evidence},null,2));
}finally{await browser.close();}
