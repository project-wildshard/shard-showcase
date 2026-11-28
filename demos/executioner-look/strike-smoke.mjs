import {chromium} from 'playwright';
import assert from 'node:assert/strict';
import {mkdirSync} from 'node:fs';
const [url='http://127.0.0.1:5254/demos/executioner-look/',out='/tmp/executioner-strike']=process.argv.slice(2);
mkdirSync(out,{recursive:true});
const dest=new URL(url);
for(const [k,v] of [['mesh','./strike-study.glb'],['motion','strike'],['tone','localized'],['stage','forge']])dest.searchParams.set(k,v);
const b=await chromium.launch({executablePath:process.env.CHROMIUM_BINARY,
 args:['--enable-unsafe-swiftshader','--use-angle=swiftshader',...JSON.parse(process.env.CHROMIUM_EXTRA_ARGS??'[]')]});
const rows=[];
const diff=(a,b)=>Math.hypot(...a.map((v,i)=>v-b[i]));
const stage=e=>Object.assign({},e.dataset);
const pts=s=>s.motionMark.split(';').map(row=>row.split(',').map(Number));
try{
 for(const [label,w,h,touch] of [['desktop',1280,720,false],['portrait',402,874,true]]){
  const p=await b.newPage({viewport:{width:w,height:h},hasTouch:touch,isMobile:touch,deviceScaleFactor:1});
  const errors=[];p.on('pageerror',e=>errors.push(e.message));p.on('console',m=>{if(m.type()==='error')errors.push(m.text());});
  await p.goto(dest.href);
  await p.waitForFunction(()=>['ready','error'].includes(document.querySelector('#stage').dataset.state));
  const read=()=>p.locator('#stage').evaluate(stage);
  const first=await read();assert.equal(first.state,'ready',await p.locator('#status').textContent());
  assert.equal(first.motion,'planted-strike');assert.equal(first.camera,'forge-fixed');assert.equal(first.tone,'localized');assert.equal(first.dressing,'forge-yard');
  assert(+first.motionSeconds>=2&&+first.motionSeconds<=2.04);
  const play=p.getByRole('button',{name:'Play step and strike'});
  if(touch)await play.tap();else await play.click();
  await p.waitForFunction(()=>+document.querySelector('#stage').dataset.motionProgress===1);
  const end=await read();assert.deepEqual(end.cameraDistance,first.cameraDistance);
  assert(+end.clothTravel>.05);assert(+end.skinnedMeshes===7);
  const slider=p.getByRole('slider',{name:'Step and strike progression'});
  await slider.press('Home');assert.equal(+(await read()).motionProgress,0);
  const capture=async(name,value)=>{
   // Trusted Play and keyboard rewind are already verified. Use the scrub
   // interaction with fixed numeric values for reproducible frame captures.
   await slider.evaluate((e,v)=>{e.value=String(v);e.dispatchEvent(new Event('input',{bubbles:true}));},value);
   const s=await read();assert.equal(+s.motionProgress,value/100);
   assert.equal(s.cameraDistance,first.cameraDistance);
   await p.screenshot({path:`${out}/${label}-${name}.png`});
   return pts(s);
  };
  const rest=await capture('rest',0),lift=await capture('lift',28),plant=await capture('plant',41),
   wind=await capture('windup',57),strike=await capture('strike',67),recover=await capture('recover',100);
  assert(lift[1][1]-rest[1][1]>.09);
  assert(diff(plant[1],rest[1])>.33&&diff(plant[1],rest[1])<.39);
  assert(diff(strike[1],plant[1])<.003&&diff(recover[1],plant[1])<.003);
  const rear=Math.max(...[lift,plant,wind,strike,recover].map(q=>diff(q[0],rest[0])));
  assert(rear<.003);assert(diff(strike[2],wind[2])>.60);
  const clothSide=p.getByRole('button',{name:'Cloth side',exact:true});
  if(touch)await clothSide.tap();else await clothSide.click();
  assert.equal((await read()).view,'left');
  await slider.evaluate(e=>{e.value='67';e.dispatchEvent(new Event('input',{bubbles:true}));});
  await p.screenshot({path:`${out}/${label}-cloth-strike.png`});
  assert.deepEqual(errors,[]);
  rows.push({viewport:[w,h],trustedTouch:touch,forgeView:{fov:46,fixed:true,distanceM:+first.cameraDistance,
   standingSizePx:+first.heightPixels,reusedDressing:true},triangles:+end.triangles,duration:+end.motionSeconds,
   rearFootMaxDriftM:rear,frontFootStepM:diff(plant[1],rest[1]),wristWindupToStrikeM:diff(strike[2],wind[2]),sampled:true});
  await p.close();
 }
 console.log(JSON.stringify({actualSkin:true,cameraOnly:true,localAirStrike:true,hasTarget:false,rows},null,2));
}finally{await b.close();}
