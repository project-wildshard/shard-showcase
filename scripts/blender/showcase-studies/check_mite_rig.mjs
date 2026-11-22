import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { AnimationMixer, LoopOnce, Vector3 } from 'three'
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'
const file=process.argv[2]
assert(file,'Pass the exported rig GLB')
assert(process.argv.length===3||process.argv.length===4&&process.argv[3]==='--far')
const expectedTriangles=process.argv[3]==='--far'?138:386
const bytes=await readFile(file)
const gltf=await new GLTFLoader().parseAsync(bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),'')
const clips=Object.fromEntries(gltf.animations.map(clip=>[clip.name,clip]))
assert.deepEqual(Object.keys(clips).sort(),['idle','walk','run','turn','telegraph','attack.bite','attack.overclock','hit','die','sleep','wake'].sort())
let tris=0,bones
const boundJoints=new Set()
gltf.scene.traverse(o=>{
    if(!o.isMesh)return
    assert(o.isSkinnedMesh,o.name)
    tris+=o.geometry.index.count/3
    bones=o.skeleton.bones
    const weights=o.geometry.attributes.skinWeight
    for(let i=0;i<weights.count;i++){
        assert.deepEqual([weights.getX(i),weights.getY(i),weights.getZ(i),weights.getW(i)],[1,0,0,0])
        boundJoints.add(bones[o.geometry.attributes.skinIndex.getX(i)].name)
    }
})
assert.equal(tris,expectedTriangles)
assert.deepEqual(bones.map(b=>b.name),['body','head','eye','front_l','front_r','rear_l','rear_r'])
assert.deepEqual([...boundJoints].sort(),bones.map(b=>b.name).sort())
const mix=new AnimationMixer(gltf.scene)
const play=(name,t)=>{
    mix.stopAllAction()
    const clip=mix.clipAction(clips[name]).reset()
    clip.setLoop(LoopOnce,1);clip.clampWhenFinished=true;clip.play()
    mix.update(t)
}
play('idle',0);const rest=bones[0].position.y
play('attack.bite',.6);assert(bones[0].position.y<rest-.07)
play('attack.bite',22/30);assert(bones[0].position.y>rest+.1)
play('turn',.2);assert(Math.abs(bones[0].quaternion.w)<.999)
play('sleep',.5);assert(bones.find(b=>b.name==='eye').scale.x<.04)
const die=clips.die
assert(die.duration>=1.29&&die.duration<=1.31)
function posedBounds(){
    gltf.scene.updateMatrixWorld(true)
    let minX=Infinity,maxX=-Infinity
    const minY={}
    gltf.scene.traverse(o=>{
        if(!o.isSkinnedMesh)return
        o.skeleton.update()
        const p=o.geometry.attributes.position,ix=o.geometry.attributes.skinIndex
        for(let i=0;i<p.count;i++){
            const v=new Vector3().fromBufferAttribute(p,i)
            const n=o.skeleton.bones[ix.getX(i)].name
            o.applyBoneTransform(i,v).applyMatrix4(o.matrixWorld)
            minX=Math.min(minX,v.x);maxX=Math.max(maxX,v.x)
            minY[n]=Math.min(minY[n]??Infinity,v.y)
        }
    })
    return {width:maxX-minX,minY}
}
play('die',0);const initial=posedBounds()
play('die',.467);const airborne=posedBounds()
play('die',die.duration);const settled=posedBounds()
assert(bones[0].position.y<rest-.15)
assert(airborne.minY.head>.65&&settled.width>initial.width*2.2,'Detached lid and outward scatter')
for(const n of ['body','head','front_l','front_r','rear_l','rear_r'])
    assert(settled.minY[n]>.003&&settled.minY[n]<.02,'Each visible piece settles above the floor')
assert(bones.find(b=>b.name==='eye').scale.x<.04,'Eye collapses on death')
console.log(`Verified rigid weights, 7 joints, ${tris} tris, and 11 playable GLB clips.`,bytes.length,'bytes')
