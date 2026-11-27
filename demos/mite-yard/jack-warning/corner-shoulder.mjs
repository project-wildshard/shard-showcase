// Reversible render-only shoulder camera, not an override of Fable's
// camera controller or touch basis. Compare weapon-on/off at each lens.
export function installShoulder(g,p,mob,f,h,draw,began){
 const cam=g.camera;
 const v=p.pos.clone();
 const loc=node=>node.getWorldPosition(v.clone());
 const project=node=>{
  const q=loc(node).project(cam);
  return [(q.x+1)*201,(1-q.y)*437,q.z];
 };
 const checkSweep=(from,to)=>{
  const d=to.clone().sub(from),len=d.length();
  if(len<.001)return {physics:null,drawn:null};
  d.multiplyScalar(1/len);
  return {physics:g.physics.spherecast(from,d,len,.24,0xffff0003),
   drawn:g.cameraRig.occ?.sweep(from,d,len,.24)??null};
 };
 f.drawShoulder=(offset,lift,visible)=>{
  const eye=cam.position.clone(),rotation=cam.quaternion.clone();
  const weapon=p.weaponModel, flag=weapon.object.visible;
  if(!flag||!p.action?.startsWith('sword'))throw Error('Expected the active third-person sword');
  const aim=loc(mob.rig.sockets.core);
  const right=v.clone().set(1,0,0).applyQuaternion(rotation);right.y=0;right.normalize();
  const at=eye.clone().addScaledVector(right,offset);at.y+=lift;
  const d0=aim.clone().sub(eye).normalize(),d1=aim.clone().sub(at).normalize();
  const shift=rotation.clone().setFromUnitVectors(d0,d1);
  const sweep=checkSweep(eye,at);
  const before=g.cameraRig.forward(v.clone()).toArray();
  let receipt;
  try{
   cam.position.copy(at);cam.quaternion.copy(rotation).premultiply(shift);cam.updateMatrixWorld(true);
   weapon.object.visible=visible;
   draw(g.scene,cam,0);
   receipt={frame:h.frame-began,offset,lift,visible,pose:p.action,actionTime:p.actionT,hp:[g.state.d.hp,mob.hp],
    fov:cam.fov,sim:g.simTime,hero:p.pos.toArray(),jack:mob.pos.toArray(),camera:cam.position.toArray(),
    inputBasis:g.cameraRig.forward(v.clone()).toArray(),sweep,
    base:project(weapon.base),tip:project(weapon.tip),head:project(p.rig.sockets.head),
    enemyEye:project(mob.rig.sockets.weak),enemyCore:project(mob.rig.sockets.core)};
  }finally{
   weapon.object.visible=flag;cam.position.copy(eye);cam.quaternion.copy(rotation);cam.updateMatrixWorld(true);
  }
  if(JSON.stringify(receipt.inputBasis)!==JSON.stringify(before))throw Error('Input basis moved');
  return receipt;
 };
}

export async function captureShoulder(page,out){
 const offsets=[['stock',0,0],['left',-.6,0],['right',.6,0],['raised',0,.45],['raised-right',.35,.45]];
 const rows=[];
 for(const [name,offset,lift] of offsets)for(const visible of [true,false,true]){
  const row=await page.evaluate(({offset,lift,visible})=>coverFixture.drawShoulder(offset,lift,visible),{offset,lift,visible});
  const slot=rows.filter(x=>x.name===name).length, png=`shoulder-${row.frame}-${name}-${slot}.png`;
  await page.screenshot({path:out+'/'+png});
  rows.push({...row,name,slot,png});
 }
 for(const row of rows.slice(1))for(const k of ['frame','sim','pose','actionTime','hp','fov','hero','jack','inputBasis'])
  if(JSON.stringify(row[k])!==JSON.stringify(rows[0][k]))throw Error('Unmatched shoulder frame: '+k);
 await page.evaluate(rows=>{(coverFixture.shoulder??=[]).push(rows);},rows);
}
