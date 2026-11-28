import assert from 'node:assert/strict';
import test from 'node:test';
import {PerspectiveCamera,Vector3} from 'three';
import {DUEL_CAMERA_AXIS,DUEL_CAMERA_FOV,duelDistance} from './duel-camera.mjs';

test('fixed-angle fit covers both body bounds without changing the shoulder azimuth',()=>{
 const dir=new Vector3(...DUEL_CAMERA_AXIS);
 const poses=[
  [{x:0,z:0,radius:.59,height:2.14},{x:0,z:-2,radius:.55,height:2.21}],
  [{x:-9,z:6,radius:.59,height:2.14},{x:9,z:-6,radius:.70,height:1.16}],
  [{x:7,z:-4,radius:.59,height:2.14},{x:-2,z:8,radius:1.0,height:3.17}],
 ];
 for(const aspect of [360/800,402/874,960/680,1212/680])for(const [a,b] of poses){
  const look=new Vector3(a.x+(b.x-a.x)*.46,.91,a.z+(b.z-a.z)*.46);
  const cam=new PerspectiveCamera(DUEL_CAMERA_FOV,aspect,.09,85);
  cam.position.copy(look).addScaledVector(dir,duelDistance(look,aspect,[a,b]));
  cam.lookAt(look);cam.updateMatrixWorld();
  for(const o of [a,b])for(const x of [o.x-o.radius,o.x+o.radius])for(const z of [o.z-o.radius,o.z+o.radius])for(const y of [.02,o.height+.20]){
   const p=new Vector3(x,y,z).project(cam);
   assert(Math.abs(p.x)<.861&&Math.abs(p.y)<.701&&Math.abs(p.z)<1);
  }
 }
});
