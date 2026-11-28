import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdirSync} from 'node:fs';
const [url='http://127.0.0.1:5250/demos/executioner-look/',out='/tmp/executioner-ab']=process.argv.slice(2);
mkdirSync(out,{recursive:true});
const browser=await chromium.launch({executablePath:process.env.CHROMIUM_BINARY,
 args:['--enable-unsafe-swiftshader','--use-angle=swiftshader',...JSON.parse(process.env.CHROMIUM_EXTRA_ARGS??'[]')]});
const tests=[];
try{
 const page=await browser.newPage({viewport:{width:1280,height:720},deviceScaleFactor:1});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 for(const mesh of ['authored','reconstructed']){
  const caseURL=new URL(url);caseURL.searchParams.set('mesh','./'+mesh+'.glb');caseURL.searchParams.set('tone','clay');
  await page.goto(caseURL.href);
  await page.waitForFunction(()=>['ready','error'].includes(document.querySelector('#stage').dataset.state));
  const state=()=>page.locator('#stage').evaluate(el=>Object.assign({},el.dataset));
  const before=await state();assert.equal(before.state,'ready',await page.locator('#status').textContent());
  assert.equal(before.tone,'clay');assert.equal(before.view,'desktop');
  await page.screenshot({path:`${out}/${mesh}-distance.png`});
  for(const name of ['Close','Profile','Rear']){
   await page.getByRole('button',{name,exact:true}).click();
   const s=await state();assert.equal(s.view,name.toLowerCase());
   await page.screenshot({path:`${out}/${mesh}-${s.view}.png`});
  }
  tests.push({mesh,triangles:+before.triangles,projectedHeightPx:+before.heightPixels,heightM:+before.modelHeight});
 }
 assert(Math.abs(tests[0].projectedHeightPx-tests[1].projectedHeightPx)<3);
 assert.deepEqual(errors,[]);
 console.log(JSON.stringify({sameCamera:true,sameLighting:true,sameMaterial:true,identicalPose:false,viewport:[1280,720],tests,errors},null,2));
}finally{await browser.close();}
