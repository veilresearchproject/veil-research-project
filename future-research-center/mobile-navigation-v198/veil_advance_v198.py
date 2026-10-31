"""VEIL v1.9.8: repair real blocked mobile navigation, sort transmissive acrylic, and test offline.
Input is actual v1.9.7 Library ZIP. This script never modifies the source ZIP.
"""
from pathlib import Path
import re,zipfile,subprocess,json,hashlib
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parent/'live-pbr-v197/index.html'
s=SOURCE.read_text()
assert len(s)>3_000_000 and '1.9.7-pbr-live-texture-atlas' in s
# Verified collision tests found that both MTC and command-room tour spawn points
# intersected furniture. Move the *camera*, not the furniture, into clear walkways.
assert s.count('"pos":[-23,1.72,-4.8]')==1
assert s.count('"pos":[0,5.92,-12.4]')==1
s=s.replace('"pos":[-23,1.72,-4.8]','"pos":[-22.3,1.72,-4.8]')
s=s.replace('"pos":[0,5.92,-12.4]','"pos":[0,5.92,-14.8]')
# Exterior was trapped outside the collision boundary; exterior level is a safe
# elevated overview (not ground-level physical navigation).
s=s.replace('if(x<-59||x>59||z<-39||z>34)return false;', '''if(lvl===0)return x>=-95&&x<=95&&z>=-95&&z<=95;
    if(x<-59||x>59||z<-39||z>34)return false;''',1)
# Pointer-capture control is shared by both renderers, with a deterministic tap step
# for short touch events that otherwise finish between two animation frames.
marker="window.VEIL_DEVELOPMENT.renderer=gl?'webgl':'software';window.VEIL_DEVELOPMENT.renderScale=1;"
assert s.count(marker)==1
shared='''
// v1.9.8: press-and-hold AND short tap work on mobile. A tap advances a minimum
// 0.55 model units, rather than depending on the timing of requestAnimationFrame.
window.VEIL_MOBILE_NAV={pointerDown:0,tapSteps:0,heldReleases:0,lastAction:null};
function veilBindMobileControls(keys,onTap){
 for(const b of document.querySelectorAll('#mobile [data-key]')){
  const k=b.dataset.key;let started=0,pressed=false,startPosition=null;
  b.setAttribute('aria-label',k==='KeyW'?'Move forward':k==='KeyS'?'Move backward':k==='KeyA'?'Strafe left':'Strafe right');
  b.addEventListener('pointerdown',e=>{
   e.preventDefault();if(pressed)return;pressed=true;started=performance.now();startPosition=[...(window.VEIL_DEVELOPMENT.camera?.position||[0,0,0])];keys.add(k);
   window.VEIL_MOBILE_NAV.pointerDown++;window.VEIL_MOBILE_NAV.lastAction=k;
   if(window.VEIL_CINEMATIC)window.VEIL_CINEMATIC.enabled=false;
   window.dispatchEvent(new Event('veil:manual-control'));
   try{b.setPointerCapture(e.pointerId)}catch(_){/* capture unavailable */}
  });
  b.addEventListener('pointerup',e=>{
   if(!pressed)return;e.preventDefault();pressed=false;keys.delete(k);
   const elapsed=performance.now()-started;
   const now=window.VEIL_DEVELOPMENT.camera?.position||startPosition;
   const already=Math.hypot(now[0]-startPosition[0],now[2]-startPosition[2]);
   const desired=elapsed<190?.55:Math.min(3.5,elapsed*.0032);
   const correction=Math.max(0,desired-already);
   if(correction>.001)onTap(k,correction);
   if(elapsed<190)window.VEIL_MOBILE_NAV.tapSteps++;
   else window.VEIL_MOBILE_NAV.heldReleases++;
   window.VEIL_MOBILE_NAV.lastDistance=desired;
  });
  const cancel=()=>{pressed=false;keys.delete(k)};
  b.addEventListener('pointercancel',cancel);
  b.addEventListener('lostpointercapture',cancel);
  // Do not cancel on pointerleave: mobile browsers may emit it mid-press.
 }
}
'''
s=s.replace(marker,marker+shared,1)
# Remove the two duplicated legacy pointer handlers; both currently release keys
# on pointerleave and have no guaranteed movement on a short tap.
old_a="for(const b of document.querySelectorAll('[data-key]')){const k=b.dataset.key;b.addEventListener('pointerdown',e=>{e.preventDefault();keys.add(k);if(window.VEIL_CINEMATIC)window.VEIL_CINEMATIC.enabled=false;window.dispatchEvent(new Event('veil:manual-control'));b.setPointerCapture(e.pointerId)});for(const ev of ['pointerup','pointercancel','pointerleave'])b.addEventListener(ev,()=>keys.delete(k));}"
old_b="for(let b of document.querySelectorAll('[data-key]')){const k=b.dataset.key;b.addEventListener('pointerdown',e=>{e.preventDefault();keys.add(k);if(window.VEIL_CINEMATIC)window.VEIL_CINEMATIC.enabled=false;window.dispatchEvent(new Event('veil:manual-control'));b.setPointerCapture(e.pointerId)});for(let t of ['pointerup','pointercancel','pointerleave'])b.addEventListener(t,()=>keys.delete(k));}"
assert s.count(old_a)==1 and s.count(old_b)==1
# Callback modifies the same camera position used by the renderer, then runs
# the existing circle-vs-rectangle collision function.
tap='''function veilTapStep(k,distance=.55){
 const f=[Math.sin(yaw),Math.cos(yaw)],r=[Math.cos(yaw),-Math.sin(yaw)];
 let dx=0,dz=0;
 if(k==='KeyW'){dx=f[0]*distance;dz=f[1]*distance;}
 if(k==='KeyS'){dx=-f[0]*distance;dz=-f[1]*distance;}
 if(k==='KeyA'){dx=-r[0]*distance;dz=-r[1]*distance;}
 if(k==='KeyD'){dx=r[0]*distance;dz=r[1]*distance;}
 const pieces=Math.max(1,Math.ceil(Math.hypot(dx,dz)/.20));
 for(let i=0;i<pieces;i++)level=resolveMove(position,dx/pieces,dz/pieces,level);
 window.VEIL_DEVELOPMENT.camera={position:[...position],yaw,pitch,level,stop:active};
}
veilBindMobileControls(keys,veilTapStep);'''
s=s.replace(old_a,tap,1).replace(old_b,tap,1)
# Physical minimum finger targets, instead of 38px buttons on phone.
s=s.replace('bottom:150px;grid-template-columns:repeat(3,38px)','bottom:155px;grid-template-columns:repeat(3,50px)',1)
s=s.replace('#mobile button{width:38px;height:38px;font-size:16px}', '#mobile button{width:50px;height:50px;font-size:20px}',1)
# Critical WebGL state leak: the previous frame ends with acrylic VBO bound.
# Indexed BOXES must rebind their own VBO at the START of every frame.
# Otherwise stale acrylic vertex pointers cause incorrect geometry and GL errors.
s=s.replace('gl.drawElements(gl.TRIANGLES,roofStart,gl.UNSIGNED_SHORT,0);', 'veilBindAttributes(vb);gl.drawElements(gl.TRIANGLES,roofStart,gl.UNSIGNED_SHORT,0);',1)
# Capture actual camera coordinates for reproducible functional browser QA.
# Two render paths have their own requestAnimationFrame loops.
s=s.replace('function frame(t){veilSamplePerformance(t,t-last);resize();', '''function frame(t){window.VEIL_DEVELOPMENT.camera={position:[...position],yaw,pitch,level,stop:active};veilSamplePerformance(t,t-last);resize();''',1)
# Canvas fallback uses a different animation-loop declaration.
idx=s.index('if(!gl){');end=s.index('}else{',idx) if '}else{' in s[idx:] else len(s)
part=s[idx:end]
# Use specific fallback frame marker found by inspection.
if 'function frame(t)' in part:
 part=part.replace('function frame(t){', 'function frame(t){window.VEIL_DEVELOPMENT.camera={position:[...position],yaw,pitch,level,stop:active};',1)
 s=s[:idx]+part+s[end:]
# The fallback loop is named render(), not frame().
s=s.replace('function render(t){if(t-lastT<', 'function render(t){window.VEIL_DEVELOPMENT.camera={position:[...position],yaw,pitch,level,stop:active};if(t-lastT<',1)
# WebGL: front-on acrylic is ~96% transmissive; grazing Fresnel remains visible.
# It is still an approximation: no refraction, no spectral dispersion.
old="float acrylicAlpha=(baseMat>10.5&&baseMat<11.5)?mix(.15,.36,pow(1.0-clamp(abs(dot(n,toEye)),0.0,1.0),5.0)):1.0;"
new="float acrylicAlpha=(baseMat>10.5&&baseMat<11.5)?mix(.035,.19,pow(1.0-clamp(abs(dot(n,toEye)),0.0,1.0),3.0)):1.0;"
assert s.count(old)==1;s=s.replace(old,new)
needle='if(baseMat>10.5 && baseMat<11.5){\n   float rim=pow(1.0-ndv,3.0);'
assert s.count(needle)==1
s=s.replace(needle,"if(baseMat>10.5 && baseMat<11.5){\n    c=mix(c,vec3(.88,.94,.96),.84);\n   float rim=pow(1.0-ndv,3.0);",1)
# Fallback uses the same low-opacity clear material with restrained edge cues.
assert s.count("ctx.globalAlpha=night?.19:.23;ctx.fillStyle='#91d1d8';") ==1
s=s.replace("ctx.globalAlpha=night?.19:.23;ctx.fillStyle='#91d1d8';", "ctx.globalAlpha=night?.045:.055;ctx.fillStyle='#d9edf0';",1)
s=s.replace("ctx.globalAlpha=.27;ctx.strokeStyle='#d5f1f0';ctx.lineWidth=.75;ctx.stroke();", "ctx.globalAlpha=.14;ctx.strokeStyle='#d5f1f0';ctx.lineWidth=.6;ctx.stroke();",1)
# Transparent faces must be blended back-to-front, not authored mesh order.
# Only eight real panel triangles, so dynamic 240-float upload is inexpensive.
anchor='const curvedGPU={permanent:veilCreateVertexBucket(curvedBuckets.permanent),roof:veilCreateVertexBucket(curvedBuckets.roof),envelope:veilCreateVertexBucket(curvedBuckets.envelope),acrylic:veilCreateVertexBucket(curvedBuckets.acrylic)};'
assert s.count(anchor)==1
sorter='''
// Eight thin acrylic triangles; sort their centroids back-to-front per camera.
// Depth writes remain disabled for the translucent pass. This removes the
// previous incorrect mesh-authoring-order dependence when orbiting the chamber.
const veilAcrylicTris=[];
for(let i=0;i<curvedBuckets.acrylic.length;i+=30){
 const tri=curvedBuckets.acrylic.slice(i,i+30);
 veilAcrylicTris.push({tri,c:[(tri[0]+tri[10]+tri[20])/3,(tri[1]+tri[11]+tri[21])/3,(tri[2]+tri[12]+tri[22])/3]});
}
window.VEIL_ACRYLIC_QA={triangles:veilAcrylicTris.length,sortedFrames:0,alphaFaceOn:.035,alphaGrazing:.19};
function veilSortAcrylic(eye){
 const ordered=veilAcrylicTris.map(t=>({t,d:(t.c[0]-eye[0])**2+(t.c[1]-eye[1])**2+(t.c[2]-eye[2])**2})).sort((a,b)=>b.d-a.d);
 const data=new Float32Array(curvedBuckets.acrylic.length);let off=0;
 for(const item of ordered){data.set(item.t.tri,off);off+=30;}
 gl.bindBuffer(gl.ARRAY_BUFFER,curvedGPU.acrylic.buffer);
 gl.bufferSubData(gl.ARRAY_BUFFER,0,data);
 window.VEIL_ACRYLIC_QA.sortedFrames++;
}
'''
s=s.replace(anchor,anchor+sorter,1)
assert s.count('veilBindAttributes(curvedGPU.acrylic.buffer);gl.drawArrays')==1
s=s.replace('veilBindAttributes(curvedGPU.acrylic.buffer);gl.drawArrays','veilSortAcrylic(position);veilBindAttributes(curvedGPU.acrylic.buffer);gl.drawArrays',1)
s=s.replace("version:'1.9.7-pbr-live-texture-atlas'", "version:'1.9.8-mobile-nav-acrylic-depth'",1)
s=s.replace('v1.9.7','v1.9.8')
# Validate embedded JS, preserving standalone structure.
scripts=re.findall(r'<script(?:\s[^>]*)?>(.*?)</script>',s,re.S|re.I)
assert len(scripts)==8,len(scripts)
for i,js in enumerate(scripts):
 f=ROOT/f'check_{i}.js';f.write_text(js)
 r=subprocess.run(['node','--check',str(f)],capture_output=True,text=True)
 assert r.returncode==0,(i,r.stderr[:1000])
 f.unlink()
assert s.count('data:image/webp;base64')==9
out=ROOT/'VEIL_Research_Center_v198_OPEN_IN_BROWSER.html';out.write_text(s)
print(json.dumps({'html':str(out),'bytes':out.stat().st_size,'scripts':len(scripts),'sha256':hashlib.sha256(out.read_bytes()).hexdigest()},indent=2))