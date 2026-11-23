import assert from 'node:assert/strict'
import test from 'node:test'
import {CLOUDS,CLOUD_SIZE,cloudDirection,cloudPixels,skyChannels} from './yard-sky.mjs'

test('the directional sky is deterministic and the cloud masks feather at all edges',()=>{
 const [w,h]=CLOUD_SIZE,ids=[]
 for(let variant=0;variant<3;variant++){
  const bytes=cloudPixels(variant)
  assert.deepEqual(cloudPixels(variant),bytes)
  assert.equal(bytes.length,w*h*4)
  let dense=0
  for(let y=0;y<h;y++)for(let x=0;x<w;x++){
   const a=bytes[(y*w+x)*4+3]
   if(!x||!y||x===w-1||y===h-1)assert.equal(a,0)
   if(a>180)dense++
  }
  assert(dense>w*h*.14&&dense<w*h*.75)
  ids.push(dense)
 }
 assert.equal(new Set(ids).size,3)
 for(const [b,e,s,o] of CLOUDS){
  assert(Math.abs(Math.hypot(...cloudDirection(b,e))-1)<1e-12)
  assert(e>0&&s>0&&o<=1)
 }
 assert(skyChannels(1)[0]<skyChannels(0)[0])
})
