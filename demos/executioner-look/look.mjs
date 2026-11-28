import * as T from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {RoomEnvironment} from 'three/addons/environments/RoomEnvironment.js';

const stage=document.querySelector('#stage'), status=document.querySelector('#status');
try {
 const r=new T.WebGLRenderer({antialias:true,powerPreference:'low-power'});
 r.setPixelRatio(Math.min(devicePixelRatio,1.5));r.toneMapping=T.ACESFilmicToneMapping;r.toneMappingExposure=1.05;
 r.shadowMap.enabled=true;r.shadowMap.type=T.PCFSoftShadowMap;stage.prepend(r.domElement);
 const scene=new T.Scene();scene.background=new T.Color(0x39464a);scene.fog=new T.FogExp2(0x39464a,.045);
 const env=new RoomEnvironment(),pmrem=new T.PMREMGenerator(r);
 scene.environment=pmrem.fromScene(env,.08).texture;scene.environmentIntensity=.62;env.dispose();pmrem.dispose();
 scene.add(new T.HemisphereLight(0xb6cfe7,0x514336,1.22));
 const key=new T.DirectionalLight(0xffe5cb,2.45);key.position.set(-3.2,7.6,4.4);key.castShadow=true;
 key.shadow.mapSize.set(1024,1024);key.shadow.camera.left=-4;key.shadow.camera.right=4;
 key.shadow.camera.top=4;key.shadow.camera.bottom=-4;key.shadow.normalBias=.021;scene.add(key);
 const rim=new T.DirectionalLight(0xb2d0ee,1.15);rim.position.set(3,4,-5);scene.add(rim);
 const ground=new T.Mesh(new T.PlaneGeometry(300,300),new T.MeshStandardMaterial({color:0x444a48,roughness:.91,metalness:.08}));
 ground.rotation.x=-Math.PI/2;ground.position.y=.007;ground.receiveShadow=true;scene.add(ground);
 const params=new URL(location.href).searchParams,source=params.get('mesh')??'./look.glb';
 if(!/^\.\/[a-z0-9-]+\.glb$/i.test(source))throw Error('Use a local GLB filename.');
 const gltf=await new GLTFLoader().loadAsync(source);scene.add(gltf.scene);
 let tris=0;gltf.scene.traverse(o=>{if(o.isMesh){o.castShadow=true;o.receiveShadow=true;tris+=(o.geometry.index?.count??o.geometry.attributes.position.count)/3;}});
 const bounds=new T.Box3().setFromObject(gltf.scene), span=bounds.getSize(new T.Vector3());
 if(span.y<1.75||span.y>2.15||!Number.isFinite(tris))throw Error('Unexpected model scale.');
 const camera=new T.PerspectiveCamera(39,1,.1,100);
 const views={desktop:[[0.96,3.62,7.3],[0,1.02,0]],close:[[1.78,1.52,3.1],[0,1.02,0]],
   profile:[[3.2,1.39,0.12],[0,1.01,0]],rear:[[1.14,1.55,-3.38],[0,1.04,0]]};
 let view='desktop';
 function draw(){
  const w=stage.clientWidth,h=stage.clientHeight;camera.aspect=w/h;camera.updateProjectionMatrix();r.setSize(w,h,false);
  r.render(scene,camera);
  const bot=new T.Vector3(0,bounds.min.y,0).project(camera),top=new T.Vector3(0,bounds.max.y,0).project(camera);
  stage.dataset.heightPixels=(Math.abs(top.y-bot.y)*h/2).toFixed(1);stage.dataset.viewport=w+'x'+h;
 }
 function choose(name){
  if(!(name in views))return;
  view=name;const [p,target]=views[view];camera.position.set(...p);
  // The short dimension must fit the full model in narrow phone views.
  if(window.innerWidth<560&&view!=='desktop')camera.position.lerp(new T.Vector3(...target),-.11);
  camera.lookAt(...target);
  for(const el of document.querySelectorAll('button'))el.setAttribute('aria-pressed',String(el.value===view));
  stage.dataset.view=view;draw();
 }
 document.querySelector('nav').addEventListener('click',e=>{if(e.target.tagName==='BUTTON')choose(e.target.value);});
 window.addEventListener('resize',()=>choose(view));choose('desktop');
 status.textContent='Static pose from the editable Blender model. No gameplay.';
 stage.dataset.triangles=String(tris);stage.dataset.modelHeight=span.y.toFixed(3);stage.dataset.state='ready';
} catch(error){stage.dataset.state='error';status.textContent=error.message;console.error(error);}
