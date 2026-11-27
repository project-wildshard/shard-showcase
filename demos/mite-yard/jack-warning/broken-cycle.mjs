// Scope: single live Pallet Jack in a disposable pinned-Fable fixture.
// Transform only the emitted Broken track, arc and exact one-frame head.
export function brokenCycle(g,fixture,h) {
  const fx=g.fx,rb=fx.ribbons,add=fx.add;
  const stockDraw=g.renderer.render.bind(g.renderer);
  const spot=fx.spot.bind(fx);
  let head=null, saved=null;
  fx.spot=(p,o)=>{
    const before=add.imN;
    const result=spot(p,o);
    if(fixture.mob.state==='broken'&&o.rot===.6&&o.glow===2.4&&o.color===0xffffff&&add.imN===before+1)
      head={frame:h.frame,p:[p.x,p.y,p.z],size:o.size};
    return result;
  };
  return function snap(compact) {
    const m=fixture.mob,cam=g.camera;
    if(m.state!=='broken'||g.mobs.list.filter(x=>x.alive).length!==1||!head||head.frame!==h.frame)
      throw Error('Expected one current Broken cue and its head');
    if(saved?.frame!==h.frame){
      const track=[],gold=[],P=rb.P.slice(),C=rb.C.slice();
      for(let j=0;j<rb.w*2;j++){
        if(rb.S[j*4]!==8||C[j*4+3]<=0)continue;
        (rb.S[j*4+3]>0?gold:track).push(j);
      }
      if(track.length!==58||gold.length<4||gold.length>58)throw Error('Unexpected ring geometry '+track.length+'/'+gold.length);
      const center=[0,1,2].map(k=>{
        const vals=track.map(j=>P[j*3+k]);
        return (Math.min(...vals)+Math.max(...vals))/2;
      });
      const ids=[];
      for(let i=0;i<add.mesh.geometry.instanceCount;i++){
        const o=i*4;
        if(head.p.every((v,k)=>Math.abs(v-add.aPos[o+k])<.00003)&&Math.abs(head.size-add.aPos[o+3])<.00003)
          ids.push(i);
      }
      if(ids.length!==1)throw Error('Could not isolate current timer head: '+ids);
      saved={frame:h.frame,track,gold,P,C,center,idx:ids[0],sprite:add.aPos.slice(ids[0]*4,ids[0]*4+4)};
    }
    const {track,gold,P,C,center,idx,sprite}=saved;
    const k=compact ? .58 : 1;
    rb.P.set(P);rb.C.set(C);
    for(const j of [...track,...gold])for(let a=0;a<3;a++)
      rb.P[j*3+a]=center[a]+k*(P[j*3+a]-center[a]);
    if(compact)for(const j of gold)rb.C[j*4+3]*=.65;
    for(let a=0;a<3;a++)add.aPos[idx*4+a]=center[a]+k*(sprite[a]-center[a]);
    add.aPos[idx*4+3]=sprite[3]*k;
    for(const s of ['position','aCol'])rb.mesh.geometry.getAttribute(s).needsUpdate=true;
    add.mesh.geometry.getAttribute('iPos').needsUpdate=true;
    const point=g.player.pos.clone();
    const proj=p=>{
      point.set(...p).project(cam);
      return [(point.x+1)*201,(1-point.y)*437];
    };
    const t=track.map(j=>proj(rb.P.subarray(j*3,j*3+3)));
    const trackBox=[Math.min(...t.map(p=>p[0])),Math.min(...t.map(p=>p[1])),
      Math.max(...t.map(p=>p[0])),Math.max(...t.map(p=>p[1]))];
    const headScreen=proj(add.aPos.subarray(idx*4,idx*4+3));
    const headWorld=Array.from(add.aPos.subarray(idx*4,idx*4+3));
    const radius=Math.hypot(...headWorld.map((v,a)=>v-center[a]));
    stockDraw(g.scene,cam,0);
    return {compact,frame:h.frame,sim:g.simTime,time:g.time,hp:[g.state.d.hp,m.hp],
      camera:cam.position.toArray(),q:cam.quaternion.toArray(),strobe:fx.strobe,
      remaining:1-m.stT/m.brokenDur,trackVertices:track.length,goldVertices:gold.length,
      center:proj(center),trackBox,headScreen,radius,headSize:add.aPos[idx*4+3]};
  };
}
