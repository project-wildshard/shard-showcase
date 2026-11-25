import { BufferAttribute, BufferGeometry, Color, DynamicDrawUsage, Mesh, MeshBasicMaterial, Sphere, Vector3 } from 'three'

export const DURATION = .6
export const MAX_SEGMENTS = 80
const shell = new Color('#1cb5de')
const core = new Color('#b9ffff')
const rim = new Color('#51e3ef')
const start = -.39, end = .39
const clamp = t => Math.min(1,Math.max(0,t))
const smooth = t => {t=clamp(t);return t*t*(3-2*t)}
const jitter = (i,k,t) => .62*Math.sin(23.36*i+1.83*k+t*7.5)+.38*Math.sin(73.17*i+3.2*k+t*13.7)
const point = (x,y=0,z=0) => [x,y,z]
const lift = p => [p[0],p[1],p[2]+.026]
const mix = (a,b,t) => a.map((v,i)=>v+(b[i]-v)*t)

// Local +X follows the indicator's tip, not world up; caller owns attachment.
// Pure absolute-age evaluation keeps looping, stale charge and hit logic out.
export function chargePieces(age) {
  if (!Number.isFinite(age) || age < 0 || age >= DURATION) return []
  const t=age/DURATION, q=smooth((t-.04)/.79), charge=smooth(t/.14)
  if (!charge) return []
  const segments=[]
  const emit=(a,b,width,color)=>segments.push({a,b,width,color:color.toArray()})
  const zig=(a,b,n,amp,lane,width,color)=>{
    let last=a
    for(let j=1;j<=n;j++){
      const u=j/n, next=mix(a,b,u), fade=Math.sin(Math.PI*u)
      next[1]+=fade*amp*jitter(j,lane,t)
      next[2]+=fade*amp*jitter(j,lane+13,t)*.66
      emit(last,next,width,color);last=next
    }
  }
  // Edge-travel indicators make early charge read without a whole-screen flash.
  for (let i=0;i<4;i++){
    const x=-.285+i*.19, intensity=.18+.72*charge, active=smooth((t-.065*i)/.27)
    if(active>0) emit(point(x-.038*active,.055,.092),point(x+.038*active,.055,.092),
      .021+.015*active,rim.clone().multiplyScalar(intensity))
  }
  // Converging pilot arcs grow inward before connecting into one defined spine.
  const left=mix(point(start),point(-.035,.047,.020),.24+.76*q)
  const right=mix(point(end),point(.035,-.038,.019),.24+.76*q)
  for(const [i,a,b] of [[0,point(start),left],[1,right,point(end)]]){
    zig(a,b,8,.027+.040*q,i,.025+.026*q,shell)
    zig(lift(a),lift(b),8,.027+.040*q,i,.013+.010*q,core)
  }
  const join=smooth((t-.49)/.22)
  if(join>0){
    const mid=mix(left,right,join)
    zig(left,mid,4,.009,5,.022+.022*join,shell)
    zig(lift(left),lift(mid),4,.009,5,.013+.010*join,core)
  }
  for(let i=0;i<6;i++){
    const f=smooth((t-.30-i*.051)/.32)
    if(f<=0)continue
    const x=-.29+i*.116, dir=i%2?1:-1
    zig(point(x,jitter(i,11,t)*.031,.014),
      point(x+(.08+.062*q)*dir*f,dir*(.080+.082*q)*f,-.076*f),
      3,.022*f,20+i,.013+.009*f,rim.clone().multiplyScalar(.55+.43*f))
  }
  return segments
}

// One reusable mesh. Each segment is a narrow four-sided tube, so it does
// not vanish edge-on or require any camera-facing update or light source.
export function makeChargeCue() {
  const perSegment=24, pos=new Float32Array(MAX_SEGMENTS*perSegment*3)
  const rgb=new Float32Array(pos.length)
  const geo=new BufferGeometry()
  for(const [name,array] of [['position',pos],['color',rgb]])
    geo.setAttribute(name,new BufferAttribute(array,3).setUsage(DynamicDrawUsage))
  const mat=new MeshBasicMaterial({vertexColors:true,toneMapped:false})
  const mesh=new Mesh(geo,mat)
  // Explicit bound ignores unused slots and follows the caller's mount.
  geo.boundingSphere=new Sphere(new Vector3(),.76)
  const p=new Vector3(),q=new Vector3(),d=new Vector3(),u=new Vector3(),v=new Vector3()
  const up=new Vector3(0,1,0),side=new Vector3(0,0,1)
  const offsets=[u,v,new Vector3(),new Vector3()]
  const al=new Vector3(),ar=new Vector3(),bl=new Vector3(),br=new Vector3()
  const vertices=[al,ar,bl,bl,ar,br]
  function sample(age){
    const segments=chargePieces(age)
    if(segments.length>MAX_SEGMENTS)throw new Error('Charge mesh budget exceeded')
    let k=0
    for(const {a,b,width,color} of segments){
      p.fromArray(a);q.fromArray(b);d.subVectors(q,p).normalize()
      if(!d.lengthSq())throw new Error('Degenerate charge segment')
      u.crossVectors(d,Math.abs(d.y)<.88?up:side).normalize().multiplyScalar(width*.5)
      v.crossVectors(d,u)
      offsets[2].copy(u).negate();offsets[3].copy(v).negate()
      for(let n=0;n<4;n++){
        const x=offsets[n],y=offsets[(n+1)%4]
        al.addVectors(p,x);ar.addVectors(p,y);bl.addVectors(q,x);br.addVectors(q,y)
        for (const vec of vertices){
          vec.toArray(pos,k);rgb.set(color,k);k+=3
        }
      }
    }
    geo.setDrawRange(0,k/3)
    if(k)for(const attr of [geo.attributes.position,geo.attributes.color]){
      attr.clearUpdateRanges()
      attr.addUpdateRange(0,k)
      attr.needsUpdate=true
    }
    mesh.visible=k!==0
    return segments.length
  }
  sample(-1)
  return {mesh,sample,dispose(){geo.dispose();mat.dispose()}}
}
