// Reusable third-person sword contact cue. One world-space batch; no actor,
// camera, damage, hit-stop, HUD or post-process ownership.
export const CONTACT_END = .155;
const coreEnd = .052;
const seeds = [
  [-.72,.20,3.05,.115],[-.45,.44,4.65,.132],[-.15,.29,5.15,.153],
  [.10,.70,4.40,.138],[.29,.35,4.90,.147],[.55,.51,3.65,.130],[.77,.26,3.20,.119],
];
const add=(a,b)=>a.map((x,i)=>x+b[i]), scale=(a,k)=>a.map(x=>x*k);
const dot=(a,b)=>a.reduce((n,x,i)=>n+x*b[i],0);
function direction(a){
  const n=Math.hypot(...a);
  if (!(n>1e-8)) throw new RangeError('Contact basis must not be degenerate');
  return scale(a, 1/n);
}
const cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
const rgba=x=>x.map(c=>Math.round(c*1e6)/1e6);

export function sampleContact(age,{point,normal,tangent}){
  if (![point,normal,tangent].every(a=>Array.isArray(a)&&a.length===3&&a.every(Number.isFinite)) ||
      !Number.isFinite(age)) throw new TypeError('Use finite world-space contact arrays and seconds');
  const n=direction(normal);
  const t=direction(add(tangent,scale(n,-dot(tangent,n))));
  const b=direction(cross(n,t));
  if (age<0||age>=CONTACT_END) return [];
  const onset = add(point,scale(n,.031));
  const items=[];
  if(age<coreEnd){
    const k=1-age/coreEnd;
    items.push({kind:'core',center:rgba(onset),axis:rgba(t),reach:.058+.043*k,radius:.024+.014*k,
      color:[1,.48,.12],gain:.36+.81*k*k});
  }
  for(let i=0;i<seeds.length;i++){
    const [spread,out,speed,life]=seeds[i];
    if(age>=life)continue;
    const a=direction(add(add(scale(t,.72),scale(b,spread)),scale(n,out)));
    const u=age/life, speedDown=speed*(age-age*age*.9);
    const p=add(add(onset,scale(a,.043+speedDown)),[0,-.48*age*age,0]);
    items.push({kind:'spark',center:rgba(p),axis:rgba(a),reach:.026+.072*(1-u),
      radius:.007+.008*(1-u), color:i%3?[1,.29,.038]:[1,.57,.16],gain:.88*(1-u)**1.5});
  }
  return items;
}

// The caller advances age from an existing confirmed contact event.
// Linear RGB, opaque tapered geometry with luminance fade, depth-tested and
// tone-mapped. The one InstancedMesh can be reused for each selected duel hit.
export function makeContactBatch(THREE){
  const geo=new THREE.OctahedronGeometry(1,0);
  const material=new THREE.MeshBasicMaterial({color:0xffffff,toneMapped:true,depthTest:true,depthWrite:true});
  const batch=new THREE.InstancedMesh(geo,material,8);
  const dummy=new THREE.Object3D(), axis=new THREE.Vector3(), up=new THREE.Vector3(0,1,0), color=new THREE.Color();
  batch.name='Portrait sword contact cue';
  batch.frustumCulled=false;
  batch.count=0;
  batch.visible=false;
  return {
    object:batch,
    draw(age,contact){
      const items=sampleContact(age,contact);
      items.forEach((item,i)=>{
        dummy.position.fromArray(item.center);
        dummy.quaternion.setFromUnitVectors(up,axis.fromArray(item.axis).normalize());
        dummy.scale.set(item.radius,item.reach,item.radius);
        dummy.updateMatrix();
        batch.setMatrixAt(i,dummy.matrix);
        batch.setColorAt(i,color.setRGB(...item.color).multiplyScalar(item.gain));
      });
      batch.count=items.length; batch.visible=items.length>0;
      batch.instanceMatrix.needsUpdate=true;
      if(batch.instanceColor)batch.instanceColor.needsUpdate=true;
    },
    dispose(){geo.dispose();material.dispose()},
  };
}
