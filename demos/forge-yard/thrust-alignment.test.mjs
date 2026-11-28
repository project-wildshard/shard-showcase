import {test} from 'node:test';
import assert from 'node:assert/strict';
import {Group,Vector3} from 'three';
import {beaconThrustWeight,createThrustAlignment} from './thrust-alignment.mjs';
test('Beacon Lance pivots about an offset grip and eases before and after the strike',()=>{
 const hand=new Group(),mount=new Group(),g=new Group(),tip=new Group();
 hand.position.set(4,1,-3);hand.rotation.set(.2,-1.1,.3);hand.add(mount);mount.add(g,tip);
 mount.rotation.set(.3,1.2,-.15);g.position.set(.17,.02,.06);tip.position.set(.17,1.98,.06);
 const target=hand.localToWorld(new Vector3(-2,0,0)),base=mount.quaternion.clone(),f=createThrustAlignment();
 const a=f(mount,base,hand,g,tip,target,beaconThrustWeight(.34,.34,.69));
 assert(a.before>30&&a.after<.0001&&a.gripSlip<1e-10);
 assert(a.tipGapBefore>a.tipGapAfter&&a.tipGapAfter>0.01,'alignment improves the gap without telescoping the weapon');
 assert.equal(beaconThrustWeight(0,.34,.69),0);assert.equal(beaconThrustWeight(.69,.34,.69),0);
 assert.equal(f(mount,base,hand,g,tip,null,0),null);
 assert.equal(mount.position.length(),0);assert(Math.abs(mount.quaternion.dot(base)-1)<1e-10);
});
