// Read-only lifecycle receipt around a staged low-health native enemy.
// All gameplay rewards, attacks, particles and removal remain native.
export function installFinish(g,p,m,f,h,began){
 const st=g.state, weapon=()=>p.action??null;
 const frame=()=>h.frame-began;
 f.finish={events:[],samples:[],start:{hp:m.hp,xp:st.d.xp,kills:st.d.kills.pallet??0,level:st.d.level,scrip:st.d.scrip}};
 const record=(kind,data={})=>f.finish.events.push({kind,frame:frame(),...data});
 st.events.on('xp',e=>{if(e.src==='kill')record('kill-xp',{amount:e.amount});});
 st.events.on('scrip',e=>record('scrip-credit',{amount:e.amount}));
 st.events.on('kill',e=>{if(e.kind==='pallet')record('kill',{level:e.level,variant:e.variant});});
 function watch(obj,fn,before){
  const orig=obj[fn].bind(obj);
  obj[fn]=(...args)=>{before(...args);return orig(...args);};
 }
 watch(g.loot,'scrip',(_,amount)=>record('scrip-drop',{amount}));
 watch(g.fx,'robotDeath',()=>record('breakup'));
 watch(g.mobs,'remove',mob=>{if(mob===m)record('remove');});
 const loc=node=>node.getWorldPosition(p.pos.clone()).toArray();
 const sample=()=>{
  const inScene=m.rig.root.parent===g.scene;
  const target=g.combat.target===m;
  const r={frame:frame(),hp:m.hp,heroHp:st.d.hp,xp:st.d.xp,kills:st.d.kills.pallet??0,level:st.d.level,
   alive:m.alive,targetable:m.targetable,target,inList:g.mobs.list.includes(m),inScene,
   attack:m.atk?.id??null,state:m.state,action:m.pose.action,poseT:m.pose.t,
   scrip:st.d.scrip,scripOrbs:g.loot.orbs.filter(o=>o.kind==='scrip').map(o=>o.n),
   sword:weapon(),hero:p.pos.toArray(),eye:inScene?loc(m.rig.sockets.weak):null};
  f.finish.samples.push(r);
  return r;
 };
 return {sample};
}

export async function captureFinish(page,out){
 const row=await page.evaluate(()=>{
  const f=coverFixture, sample=f.finish.samples.at(-1);
  return {phase:f.finish.capture,frame:sample.frame};
 });
 await page.screenshot({path:out+'/finish-'+row.phase+'.png'});
}

// Reopen against the same isolated Chromium context without ?golden, so
// the initial fixture and storage reset cannot be applied to the new page.
export async function verifyPayoutSave(ctx,url){
 const page=await ctx.newPage();
 await page.goto(url,{waitUntil:'domcontentloaded'});
 const button=page.locator('[data-t="go"]').filter({hasText:'Continue'});
 await button.waitFor({timeout:90000,state:'visible'});
 const snapshot=()=>page.evaluate(()=>{
  const d=game.state.d;
  return {scrip:d.scrip,xp:d.xp,palletKills:d.kills.pallet??0,level:d.level,golden:!!window.__golden};
 });
 const before=await snapshot();
 await button.tap({timeout:15000});
 await page.waitForFunction(()=>game.started,null,{timeout:90000});
 const after=await snapshot();
 await page.close();
 return {before,after};
}
