"""VEIL v2.0.0: structural GB-001 lab enclosure + actual bounded softbox illumination.
Reproducible offline HTML source transformation. No publication or merge.
Usage: python veil_advance_v200.py input_v199.html output_v200.html
"""
from pathlib import Path
import sys

def replace_once(s,old,new):
    n=s.count(old)
    if n!=1:raise RuntimeError(f'Expected one occurrence, found {n}: {old[:90]}')
    return s.replace(old,new,1)

NEW_GEOMETRY=r'''
// VEIL v2.0.0: authored room-scale architectural enclosure, not a concept image.
// Coordinates match v1.8 GB-001 geometry; no changes to the 43 original v1.8 groups.
// All additions are explicit triangle meshes shared by Canvas and WebGL renderers.
const VEIL_ARCH_V200=[];
function v200Group(name,center,radius,classification='permanent'){
 const g=veilArchGroup(name,center,radius,classification);
 g.v200=true;VEIL_ARCH_V200.push(g);return g;
}
function v200Box(g,center,size,color,material=8){
 veilChamferedBox(g,center,size,Math.min(...size)*.025,color,material);
}
// Continuous wall backing; panel joints, corner returns and service trim are
// proud of the substrate rather than being drawn onto a 2D image.
{
 const g=v200Group('v2 GB-001 insulated rear wall and modular service cladding',[-24,2.2,23.79],7.8);
 v200Box(g,[-23.90,2.20,23.93],[14.10,4.35,.16],'#74858b',8);
 for(let i=0;i<12;i++){
  const x=-30.37+i*1.17;
  v200Box(g,[x,2.22,23.818],[1.128,3.94,.035],i%3===0?'#b8c4c2':'#aebdbd',8);
  v200Box(g,[x+.576,2.22,23.79],[.019,3.96,.049],'#516771',2);
 }
 // Continuous hard-wearing impact protection, with a recessed upper cap.
 v200Box(g,[-23.90,.47,23.745],[14.00,.87,.064],'#566f78',8);
 v200Box(g,[-23.90,.934,23.712],[14.0,.048,.082],'#a8b9bd',2);
 v200Box(g,[-23.90,.094,23.700],[14.02,.11,.115],'#33464f',2);
 v200Box(g,[-23.90,3.96,23.700],[14.04,.14,.105],'#758d95',2);
 // Conduit mounted behind the simulated instrument review boards.
 v200Box(g,[-23.90,1.24,23.695],[13.55,.095,.09],'#607e88',2);
 for(const x of [-30.1,-27.7,-25.3,-22.9,-20.5,-18.1]){
  v200Box(g,[x,1.24,23.63],[.10,.18,.08],'#9aadb2',2);
 }
}
// Existing side partitions are retained; these are shallow interior finish
// panels, skirting, and real trim, not opaque replacements of the base walls.
for(const west of [true,false]){
 const x=west?-30.818:-16.982;
 const g=v200Group('v2 GB-001 '+(west?'west':'east')+' wall liner and impact panels',[x,2.2,18.1],6.0);
 for(let i=0;i<6;i++){
  const z=13.6+i*1.78;
  v200Box(g,[x,2.36,z],[.036,3.62,1.72],i%2?'#b4c2c1':'#c0cac8',8);
  v200Box(g,[x+(west?.031:-.031),.64,z],[.047,1.04,1.71],'#647e88',8);
  v200Box(g,[x+(west?.055:-.055),1.195,z],[.055,.046,1.72],'#c0d0d1',2);
  v200Box(g,[x+(west?.038:-.038),.084,z],[.058,.12,1.73],'#354b55',2);
  if(i<5)v200Box(g,[x+(west?.05:-.05),2.40,z+.882],[.065,3.65,.024],'#728c94',2);
 }
}
// A single shallow epoxy wear layer replaces the bare slab appearance inside
// the flexible lab, with correctly modeled expansion joints and perimeter trim.
{
 const g=v200Group('v2 GB-001 grounded epoxy floor and expansion joints',[-24,.025,18.2],9.2);
 v200Box(g,[-23.93,.016,18.30],[13.66,.027,10.70],'#7a8a8a',1);
 for(let i=1;i<6;i++){
  const x=-30.76+i*2.28;
  v200Box(g,[x,.034,18.30],[.018,.007,10.58],'#405861',2);
 }
 for(let i=1;i<5;i++){
  const z=12.95+i*2.14;
  v200Box(g,[-23.93,.034,z],[13.58,.007,.018],'#405861',2);
 }
}
// Removable ceiling perimeter service rails; tagged as roof-class so the
// established roof-off cutaway continues to expose the full lab from above.
{
 const g=v200Group('v2 GB-001 ceiling perimeter and concealed service raceways',[-24,4.27,18.3],8.5,'roof');
 for(const z of [13.00,23.58])v200Box(g,[-23.93,4.23,z],[13.80,.18,.24],'#7d939b',2);
 for(const x of [-30.77,-17.07])v200Box(g,[x,4.23,18.30],[.24,.18,10.55],'#7d939b',2);
 for(const x of [-28.20,-24.0,-19.80]){
  v200Box(g,[x,4.27,18.53],[.14,.12,10.05],'#667e89',2);
 }
}
window.VEIL_ARCH_V200={version:'2.0.0',room:'GB-001',
 groups:VEIL_ARCH_V200.length,
 triangles:VEIL_ARCH_V200.reduce((n,g)=>n+g.triangles.length,0),
 classifications:VEIL_ARCH_V200.map(g=>({name:g.name,sectionClass:g.sectionClass,triangles:g.triangles.length})),
 meshGroups:VEIL_ARCH_V200,
 proposedOnly:true,diagnostics:'SIMULATED',photorealistic:false};
'''

def build(src,dst):
 s=Path(src).read_text(encoding='utf-8')
 s=replace_once(s,"version:'1.9.9-linear-pbr-indirect-light'","version:'2.0.0-architectural-enclosure-softbox-light'")
 s=replace_once(s,'window.VEIL_FLEX_V18={version:',NEW_GEOMETRY+'\nwindow.VEIL_FLEX_V18={version:')
 s=replace_once(s,'const NAV_OBSTACLES=BOXES.filter(b=>NAV_COLLISION_TAGS.test(b.tag)&&b.s[1]>.18);',
 '''const NAV_OBSTACLES=BOXES.filter(b=>NAV_COLLISION_TAGS.test(b.tag)&&b.s[1]>.18);
 // v2: the new solid back partition is a real collision surface as well.
 NAV_OBSTACLES.push({c:[-23.9,2.20,23.91],s:[14.10,4.35,.18],tag:'v2 GB-001 back partition'});''')
 # Shader lighting: match six actual diffuser positions, and make light direction
 # and inverse-square distance determine diffuse contribution.
 s=replace_once(s,'uniform vec3 uFootprints[12];','uniform vec3 uFootprints[12];\nuniform vec3 uLabSoftboxes[6];')
 s=replace_once(s,'lighting+=labWeight*(vec3(.065,.082,.086)+vec3(.12,.095,.075)*floorBounce);',
 '''lighting+=labWeight*(vec3(.048,.062,.068)+vec3(.09,.078,.065)*floorBounce);
 // Six physical ceiling softboxes: bounded point-area approximation. The
 // source positions match the actual modeled diffuser meshes, unlike the
 // prior purely decorative emissive panels. Not path-traced indirect light.
 for(int i=0;i<6;i++){
  vec3 delta=uLabSoftboxes[i]-vWorld;
  float d2=dot(delta,delta)+.4;
  float d=sqrt(d2);
  vec3 lightDir=delta/d;
  float normalResponse=max(dot(n,lightDir),0.0);
  float downCone=clamp(delta.y/d,0.0,1.0);
  float falloff=(3.6/(d2+3.6))*(1.0-smoothstep(8.0,12.0,d));
  lighting+=labWeight*vec3(.91,.98,.96)*normalResponse*downCone*falloff*.86;
 }''')
 s=replace_once(s,"uFootprints=gl.getUniformLocation(program,'uFootprints[0]');",
 "uFootprints=gl.getUniformLocation(program,'uFootprints[0]'),uLabSoftboxes=gl.getUniformLocation(program,'uLabSoftboxes[0]');")
 s=replace_once(s,'// Dedicated unindexed drawArrays VBO for curved meshes:',
 '''const VEIL_LAB_SOFTBOXES=new Float32Array([
 -28.2,3.83,16.4, -28.2,3.83,20.75,
 -24.0,3.83,16.4, -24.0,3.83,20.75,
 -19.8,3.83,16.4, -19.8,3.83,20.75]);
// Dedicated unindexed drawArrays VBO for curved meshes:''')
 s=replace_once(s,'gl.uniform3fv(uFootprints,VEIL_FOOTPRINTS);',
 'gl.uniform3fv(uFootprints,VEIL_FOOTPRINTS);gl.uniform3fv(uLabSoftboxes,VEIL_LAB_SOFTBOXES);')
 # PBR triplanar atlas mapping for new walls and floor, no change to original UV GLB.
 s=replace_once(s,"if(g.name.startsWith('GB-001')){",
 "if(g.name.startsWith('GB-001')||g.v200){")
 s=replace_once(s,"const texIndex=tri.m===1?1:tri.m===11?2:tri.m===3?3:tri.m===4?4:tri.m===8?5:tri.m===2?0:6;",
 "const texIndex=tri.m===1?1:tri.m===11?2:tri.m===3?3:tri.m===4?4:tri.m===8?(g.v200?6:5):tri.m===2?0:6;")
 s=replace_once(s,"window.VEIL_PBR_RENDERER={mode:'sRGB-to-linear atlas + GGX key + bounded indirect bounce sampled by WebGL'",
 "window.VEIL_PBR_RENDERER={mode:'sRGB-to-linear atlas + GGX key + six bounded GB-001 ceiling lights sampled by WebGL'")
 s=replace_once(s,'<title>VEIL Research Center — Architectural Acoustics & Filmic Materials v1.9.4 | A Vision Taking Shape</title>',
 '<title>VEIL Research Center — v2.0 Architectural GB-001 Laboratory | A Vision Taking Shape</title>')
 Path(dst).write_text(s,encoding='utf-8')
 return {'source_bytes':Path(src).stat().st_size,'result_bytes':Path(dst).stat().st_size}

if __name__=='__main__':print(build(sys.argv[1],sys.argv[2]))