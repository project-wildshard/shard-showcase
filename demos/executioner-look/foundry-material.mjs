// A texture-free surface experiment for the look viewer, not a production shader.
function property(name) {
 if(name.includes('steel')||name.includes('hammered')||name.includes('copper'))return 1;
 if(name.includes('leather')||name.includes('cured'))return 2;
 if(name.includes('ceramic'))return 3;
 return 0;
}
const substance=`
varying vec3 vFoundryPosition;
uniform float uFoundryClass;
uniform float uFoundryLocalized;
float fHash(vec3 p){
 p=fract(p*vec3(.1031,.1030,.0973));p+=dot(p,p.yxz+33.33);
 return fract((p.x+p.y)*p.z);
}
float fNoise(vec3 p){
 vec3 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);
 return mix(mix(mix(fHash(i),fHash(i+vec3(1,0,0)),f.x),mix(fHash(i+vec3(0,1,0)),fHash(i+vec3(1,1,0)),f.x),f.y),
            mix(mix(fHash(i+vec3(0,0,1)),fHash(i+vec3(1,0,1)),f.x),mix(fHash(i+vec3(0,1,1)),fHash(i+vec3(1,1,1)),f.x),f.y),f.z);
}
float fWeave(vec3 p){
 // Band-limit stripes at projected gameplay sizes to avoid shimmer.
 vec3 w=sin(p*vec3(181.,141.,174.)*6.2831853);
 float visible=1.-smoothstep(.25,1.,length(fwidth(p))*120.);
 return (.58*w.x*w.z+.42*w.y*w.z)*visible;
}
float fScale(vec3 p){
 float coarse=fNoise(p*13.1),grain=fNoise(p*123.);
 return .53*coarse+.28*fNoise(p*35.2)+.19*grain;
}
`;
export function applyFoundryMaterial(material, localized=false) {
 if(material.userData.foundry)return;
 material.userData.foundry=true;
 const family=property(material.name.toLowerCase());
 material.onBeforeCompile=shader=>{
  shader.uniforms.uFoundryClass={value:family};
  shader.uniforms.uFoundryLocalized={value:Number(localized)};
  shader.vertexShader='varying vec3 vFoundryPosition;\n'+shader.vertexShader;
  shader.vertexShader=shader.vertexShader.replace('#include <begin_vertex>','#include <begin_vertex>\n vFoundryPosition=position;');
  shader.fragmentShader=substance+shader.fragmentShader;
  shader.fragmentShader=shader.fragmentShader.replace('#include <color_fragment>',`
  #include <color_fragment>
  vec3 foundryPoint=vFoundryPosition;
  float foundryBody=fScale(foundryPoint),foundryMacro=fNoise(foundryPoint*5.7);
  float foundryHeight=fNoise(foundryPoint*223.);
  if(uFoundryClass<.5){
   float woven=fWeave(foundryPoint);
   diffuseColor.rgb *= .67+foundryBody*.48+woven*.11;
   foundryHeight*=.35;foundryHeight+=woven*.12;
  }else if(uFoundryClass<1.5){
   float oxide=smoothstep(.43,.69,foundryBody)*smoothstep(.25,.75,foundryMacro);
   float highImpact=1.-smoothstep(.045,.20,abs(abs(foundryPoint.x)-.29)+abs(foundryPoint.y-1.50)*.62);
   float strapEdge=1.-smoothstep(.009,.036,abs(foundryPoint.y-1.15)+.026*abs(foundryPoint.x));
   float shinWear=(1.-smoothstep(.022,.115,abs(foundryPoint.y-.39)))*.45;
   float distributed=max(highImpact*.57,max(strapEdge,shinWear));
   float localizedOxide=oxide*distributed;
   diffuseColor.rgb=mix(diffuseColor.rgb*mix(.68+.68*foundryBody,.90+.22*foundryBody,uFoundryLocalized),
                       vec3(.132,.058,.027),mix(oxide*.65,localizedOxide*.54,uFoundryLocalized));
   foundryHeight*=mix(.70,.16+.34*distributed,uFoundryLocalized);
  }else if(uFoundryClass<2.5){
   float pore=fNoise(foundryPoint*165.);
   diffuseColor.rgb *= .59+.87*foundryBody+.17*pore;
   diffuseColor.rgb *= mix(vec3(.82,.73,.65),vec3(1.08,1.02,.94),foundryMacro);
   foundryHeight=pore*.51;
  }else{
   diffuseColor.rgb *= mix(vec3(.68,.54,.43),vec3(.98,.94,.82),smoothstep(.16,.76,foundryBody));
   foundryHeight*=.23;
  }`);
  shader.fragmentShader=shader.fragmentShader.replace('#include <roughnessmap_fragment>',`
   #include <roughnessmap_fragment>
   roughnessFactor=clamp(roughnessFactor+(foundryBody-.48)*(uFoundryClass<1.5?.54:.32),.23,.96);`);
  shader.fragmentShader=shader.fragmentShader.replace('#include <normal_fragment_maps>',`
   #include <normal_fragment_maps>
   vec3 fQx=dFdx(-vViewPosition),fQy=dFdy(-vViewPosition);
   vec3 fRx=cross(fQy,normal),fRy=cross(normal,fQx);
   float fDet=dot(fQx,fRx);
   float fVisible=1.-smoothstep(.006,.022,length(fwidth(foundryPoint)));
   vec3 fGrad=(dFdx(foundryHeight)*fRx+dFdy(foundryHeight)*fRy)*(.0016*fVisible);
   if(abs(fDet)>1e-12)normal=normalize(abs(fDet)*normal-sign(fDet)*fGrad);`);
 };
 material.customProgramCacheKey=()=>'wsc-foundry-review-v1';
 material.needsUpdate=true;
}
