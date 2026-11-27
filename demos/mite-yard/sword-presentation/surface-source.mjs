// Private-input adapter. Do not publish its vertex/triangle output; feed it
// to the local measurement script. The renderer does not see this mesh.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {createRequire} from 'node:module';
import {dirname,join} from 'node:path';
import {realpathSync,readFileSync} from 'node:fs';
import {pathToFileURL} from 'node:url';
import {readDecodedScenes} from './rig-reader.mjs';
const file=realpathSync(process.argv[2]), deps=createRequire(join(realpathSync(process.argv[3]),'package.json'));
const b=readFileSync(file);
const sourceBlob='9603f6c37b94a49904f017c7ee1cd917cab36cf3';
assert.equal(createHash('sha1').update('blob '+b.length+'\0').update(b).digest('hex'),sourceBlob);
const threeDir=dirname(dirname(deps.resolve('three')));
const THREE=await import(pathToFileURL(join(threeDir,'build/three.module.js')).href);
const load=name=>import(pathToFileURL(deps.resolve(name)).href);
const {pallet:root}=await readDecodedScenes({pallet:file},load,threeDir);
const truck=root.getObjectByName('truck');
assert.ok(truck?.isBone);
truck.scale.setScalar(1.18);
root.updateMatrixWorld(true);
let mesh;
root.traverse(o=>{if(o.isSkinnedMesh)mesh=o;});
assert.ok(mesh);
mesh.skeleton.update();
const pos=mesh.geometry.getAttribute('position'),ix=mesh.geometry.index;
const vertices=Array.from({length:pos.count},(_,i)=>{
  const v=new THREE.Vector3().fromBufferAttribute(pos,i);
  return mesh.applyBoneTransform(i,v).applyMatrix4(mesh.matrixWorld).toArray();
});
const triangles=Array.from({length:ix.count/3},(_,i)=>[ix.getX(3*i),ix.getX(3*i+1),ix.getX(3*i+2)]);
console.log(JSON.stringify({sourceBlob,truckScale:truck.scale.x,vertices,triangles}));
