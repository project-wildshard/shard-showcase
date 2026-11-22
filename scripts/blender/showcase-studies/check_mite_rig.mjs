import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { AnimationMixer, LoopOnce } from 'three'
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'
const file=process.argv[2]
assert(file,'Pass the exported rig GLB')
const bytes=await readFile(file)
const gltf=await new GLTFLoader().parseAsync(bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),'')
const clips=Object.fromEntries(gltf.animations.map(clip=>[clip.name,clip]))
assert.deepEqual(Object.keys(clips).sort(),['idle','walk','run','turn','telegraph','attack.bite','attack.overclock','hit','die','sleep','wake'].sort())
let tris=0,bones
gltf.scene.traverse(o=>{
    if(!o.isMesh)return
    assert(o.isSkinnedMesh,o.name)
    tris+=o.geometry.index.count/3
    bones=o.skeleton.bones
    const weights=o.geometry.attributes.skinWeight
    for(let i=0;i<weights.count;i++)assert.deepEqual([weights.getX(i),weights.getY(i),weights.getZ(i),weights.getW(i)],[1,0,0,0])
})
assert.equal(tris,386)
assert.deepEqual(bones.map(b=>b.name),['body','head','eye','front_l','front_r','rear_l','rear_r'])
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
play('die',1);assert(bones[0].position.y<rest-.15)
console.log('Verified rigid weights, 7 joints, 386 tris, and 11 playable GLB clips.',bytes.length,'bytes')
