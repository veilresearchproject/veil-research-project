"""VEIL v1.9.7: bring archived v1.8 PBR texture maps into the actual WebGL renderer,
repair the standalone viewer's missing images, and correct command-room glass.
No external network/services. Source inputs remain unchanged.
"""
from pathlib import Path
import base64,zipfile,io,json,re,subprocess,hashlib,os
from PIL import Image
ROOT=Path('/mnt/data')
SRC=ROOT/'VEIL_Research_Center_v196_OPEN_IN_BROWSER.html'
Z18=zipfile.ZipFile(ROOT/'VEIL_Research_Center_GB001_v18_COMPLETE.zip')
Z196=zipfile.ZipFile(ROOT/'VEIL_Research_Center_v196_ARCHITECTURE_CHECKPOINT.zip')
assert Z18.testzip() is None and Z196.testzip() is None
s=SRC.read_text()
assert len(s)>380000 and 'VEIL_V196_ARCH' in s
# Restore genuinely self-contained concept assets: previous checkpoints lost embedded images.
assets={}
for n in Z18.namelist():
 if n.startswith('future-research-center/assets/') and n.endswith('.webp'):
  assets['assets/'+n.split('/')[-1]]='data:image/webp;base64,'+base64.b64encode(Z18.read(n)).decode()
for path,uri in assets.items():
 assert path in s,path
 s=s.replace(path,uri)
assert 'assets/vision' not in s and 'assets/hero' not in s
# 7 deterministic PBR material texture pairs from the verified v1.8 export.
material_names=['brushed_alloy','anti_static_floor','clear_acrylic','diffused_led','optical_lens','acoustic_weave','matte_paint']
# One atlas row; each tile has 4px wrap-safe border. WebGL1 NPOT CLAMP_TO_EDGE + LINEAR.
TILE=136; PAD=4; TW=TILE*7
atlases={}
for suffix in ['base','metalrough']:
 atlas=Image.new('RGB',(TW,TILE))
 for i,name in enumerate(material_names):
  raw=Z18.read(f'future-research-center/pbr-textures-v18/{name}_{suffix}.png')
  im=Image.open(io.BytesIO(raw)).convert('RGB')
  assert im.size==(128,128)
  atlas.paste(im,(i*TILE+PAD,PAD))
  # Edge-extended border avoids bleeding between tiles at grazing angles.
  for p in range(PAD):
   atlas.paste(im.crop((0,0,1,128)).resize((1,128)),(i*TILE+p,PAD))
   atlas.paste(im.crop((127,0,128,128)).resize((1,128)),(i*TILE+PAD+128+p,PAD))
   atlas.paste(im.crop((0,0,128,1)).resize((128,1)),(i*TILE+PAD,p))
   atlas.paste(im.crop((0,127,128,128)).resize((128,1)),(i*TILE+PAD,PAD+128+p))
 buf=io.BytesIO();atlas.save(buf,format='PNG',optimize=True)
 atlases[suffix]=buf.getvalue()
 (ROOT/f'VEIL_v197_PBR_{suffix}_atlas.png').write_bytes(buf.getvalue())
# Targeted command-room glazing fix. Previously opaque due six-sided box faces at 85% alpha.
s=s.replace("if(/monitor|situation display|screen|console display/.test(t))return 6;", "if(/command room tinted observation glass/.test(t))return 12;\n if(/monitor|situation display|screen|console display/.test(t))return 6;",1)
# Software renderer: glass pane is intentionally thin, and all other glazing retains prior behavior.
s=s.replace("if(mat===4){\n  ctx.globalAlpha=night?.82:.88;", "if(mat===12){ctx.globalAlpha=night?.075:.10;ctx.fillStyle='#92b5c2';ctx.fill();ctx.globalAlpha=1;continue;}\n if(mat===4){\n  ctx.globalAlpha=night?.82:.88;",1)
# GPU material-coded command room glass belongs in the blended glass bucket.
s=s.replace("mat===4?(VEIL_IS_ENVELOPE(b.tag)?envelopeGlassIndices:glassIndices)","(mat===4||mat===12)?(VEIL_IS_ENVELOPE(b.tag)?envelopeGlassIndices:glassIndices)",1)
# Texture atlas uniforms + packed per-triangle material encoding in the curved geometry.
s=s.replace("uniform vec3 uFootprints[8];\nfloat sNoise", "uniform vec3 uFootprints[8];\nuniform sampler2D uPBRBaseAtlas;\nuniform sampler2D uPBRMetalAtlas;\nfloat sNoise",1)
start=s.index('const fs=`');end=s.index('`;\nfunction shader(',start)
fs=s[start:end]
pre,main=fs.split('void main(){',1)
# Decode 16-bit exact float material codes. Original 0-12 remain intact.
main=main.replace('vMat','baseMat')
intro='''
 float baseMat=mod(vMat,16.0);
 float texIndex=floor(vMat/16.0)-1.0;
 vec3 pbrMR=vec3(0.0,0.75,0.0);
'''
main=intro+main
# Add triplanar material lookup, with repeatable world-space coordinates for actual 3D triangles.
anchor='vec3 n=normalize(vNormal); vec3 toEye=normalize(uEye-vWorld); vec3 c=vCol;'
assert anchor in main
main=main.replace(anchor,anchor+'''
 if(texIndex>=0.0){
  vec3 axis=abs(n);
  vec2 coord=axis.y>axis.x&&axis.y>axis.z?vWorld.xz:(axis.x>axis.z?vWorld.zy:vWorld.xy);
  vec2 tiled=fract(coord*1.32);
  vec2 atlasUV=vec2((texIndex*136.0+4.5+tiled.x*127.0)/952.0,(4.5+tiled.y*127.0)/136.0);
  vec3 texBase=texture2D(uPBRBaseAtlas,atlasUV).rgb;
  pbrMR=texture2D(uPBRMetalAtlas,atlasUV).rgb;
  c=mix(c,texBase,0.53);
 }
''',1)
anchor='if(baseMat>10.5 && baseMat<11.5){roughness=.12;f0=.045;} // clear acrylic'
assert anchor in main
main=main.replace(anchor,anchor+'''
 if(texIndex>=0.0){
  roughness=mix(roughness,clamp(pbrMR.g,0.08,0.98),0.85);
  f0=mix(0.045,0.68,clamp(pbrMR.b,0.0,1.0));
 }
''',1)
# New material 12 is command-room clear glass, not a solid wall.
main=main.replace('float surfaceAlpha=(baseMat>3.5&&baseMat<4.5)?0.85:acrylicAlpha;', '''float surfaceAlpha=(baseMat>11.5&&baseMat<12.5)?0.09:((baseMat>3.5&&baseMat<4.5)?0.85:acrylicAlpha);''',1)
# Bounded dielectric tint/reflection for command glazing, preserving visual clarity.
main=main.replace('// Softbox illumination falloff restricted', '''if(baseMat>11.5 && baseMat<12.5){
   float rim=pow(1.0-clamp(abs(dot(n,toEye)),0.0,1.0),5.0);
   c=mix(vec3(.44,.65,.72),vec3(.77,.89,.94),rim*.65);
   gleam+=vec3(.15,.22,.24)*rim;
 }
 // Softbox illumination falloff restricted''',1)
s=s[:start]+pre+'void main(){'+main+s[end:]
# At drawArrays VBO construction time, texture-enable only GB-001 real triangles.
old='''for(const tri of g.triangles){const data=curvedBuckets[tri.m===11?'acrylic':(g.sectionClass||'permanent')];const col=rgb(tri.c);
  for(const pos of tri.p)data.push(...pos,...col,...tri.n,tri.m);'''
new='''for(const tri of g.triangles){const data=curvedBuckets[tri.m===11?'acrylic':(g.sectionClass||'permanent')];const col=rgb(tri.c);
  // Material index is packed in 16-unit bands, preserving original material semantics.
  let materialCode=tri.m;
  if(g.name.startsWith('GB-001')){
   const texIndex=tri.m===1?1:tri.m===11?2:tri.m===3?3:tri.m===4?4:tri.m===8?5:tri.m===2?0:6;
   materialCode=16*(texIndex+1)+tri.m;
  }
  for(const pos of tri.p)data.push(...pos,...col,...tri.n,materialCode);'''
assert old in s
s=s.replace(old,new,1)
# Load embedded texture atlases asynchronously with safe 1x1 initial texture; verify readiness in QA.
atlas_js='''
// v1.9.7: REAL v1.8 PBR texture images now sampled by the interactive WebGL shader.
// The separate GLB retains its original authored UVs; the live custom renderer
// uses triplanar world coordinates to avoid replacing its geometry pipeline.
const VEIL_PBR_ATLAS={base:'__BASE__',metalrough:'__MR__'};
window.VEIL_PBR_RENDERER={mode:'real atlas textures sampled by WebGL',materialNames:__NAMES__,loaded:0,expected:2,atlasSize:[952,136],uvMode:'world-space triplanar; separate GLB has authored UVs'};
function veilUploadAtlas(url,unit){
 const tex=gl.createTexture();gl.activeTexture(gl.TEXTURE0+unit);gl.bindTexture(gl.TEXTURE_2D,tex);
 gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);
 gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);
 gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR);
 gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.LINEAR);
 gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,1,1,0,gl.RGBA,gl.UNSIGNED_BYTE,new Uint8Array([180,185,190,255]));
 const image=new Image();image.onload=()=>{
  gl.activeTexture(gl.TEXTURE0+unit);gl.bindTexture(gl.TEXTURE_2D,tex);
  gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL,true);
  gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,gl.RGBA,gl.UNSIGNED_BYTE,image);
  gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL,false);
  window.VEIL_PBR_RENDERER.loaded++;
 };image.onerror=()=>{window.VEIL_PBR_RENDERER.error='embedded atlas failed to decode'};image.src=url;
 return tex;
}
const veilAtlasBase=veilUploadAtlas(VEIL_PBR_ATLAS.base,0);
const veilAtlasMR=veilUploadAtlas(VEIL_PBR_ATLAS.metalrough,1);
gl.uniform1i(gl.getUniformLocation(program,'uPBRBaseAtlas'),0);
gl.uniform1i(gl.getUniformLocation(program,'uPBRMetalAtlas'),1);
'''.replace('__BASE__','data:image/png;base64,'+base64.b64encode(atlases['base']).decode()).replace('__MR__','data:image/png;base64,'+base64.b64encode(atlases['metalrough']).decode()).replace('__NAMES__',json.dumps(material_names))
anchor="gl.useProgram(program);"
assert s.count(anchor)==1
s=s.replace(anchor,anchor+atlas_js,1)
# Restore atlas texture bindings if future draw code changes active texture state.
s=s.replace('gl.uniform3fv(uFootprints,VEIL_FOOTPRINTS);gl.drawElements', 'gl.uniform3fv(uFootprints,VEIL_FOOTPRINTS);gl.activeTexture(gl.TEXTURE0);gl.bindTexture(gl.TEXTURE_2D,veilAtlasBase);gl.activeTexture(gl.TEXTURE1);gl.bindTexture(gl.TEXTURE_2D,veilAtlasMR);gl.drawElements',1)
# Clear and accurate user-visible version/diagnostics.
s=s.replace("version:'1.8.0-flex-correlation-model'", "version:'1.9.7-pbr-live-texture-atlas'",1)
s=s.replace("webglMaterialMode:'world-coordinate procedural roughness'", "webglMaterialMode:'live v1.8 base-color + metal/rough atlas via triplanar coordinates'",1)
s=s.replace('v1.9.6','v1.9.7').replace('v196','v197')
# preserve existing actual 3D geometry and controls.
assert 'const STOPS=' in s and 'VEIL_CURVED_MESHES' in s and 'SIMULATED' in s
assert s.count('<script')==8
OUT=ROOT/'VEIL_Research_Center_v197_OPEN_IN_BROWSER.html'
OUT.write_text(s)
# Node syntax checks of all 8 inline scripts.
script_results=[]
for i,script in enumerate(re.findall(r'<script(?:\s[^>]*)?>(.*?)</script>',s,re.S|re.I)):
 p=ROOT/f'veil_v197_js_{i}.js';p.write_text(script)
 r=subprocess.run(['node','--check',str(p)],capture_output=True,text=True)
 script_results.append({'script':i,'pass':r.returncode==0,'error':r.stderr[:400]})
 p.unlink()
assert len(script_results)==8 and all(v['pass'] for v in script_results),script_results
assert s.count('data:image/webp;base64')==9
# Save only new or changed files alongside all prior editable assets.
notes='''# VEIL v1.9.7 — Real PBR material textures in the interactive renderer

- Inspected the actual v1.8 Library baseline, full ZIP, and draft GitHub PR #45 (still open/draft/unmerged), plus v1.9.6 checkpoint.
- Fixed the v1.9.x standalone HTML regression: six concept art assets are again embedded as data URLs, with nine references. No external image paths required.
- Integrated all **seven** deterministic v1.8 base-color and metallic/roughness texture pairs into two packed atlases. The interactive WebGL renderer now **samples the real texture data** for GB-001 curved geometry, using triplanar world coordinates. The separate UV-mapped GLB is preserved but still not loaded by the browser; its authored UVs are NOT yet used in the live renderer.
- Added targeted low-opacity command-room observation glazing material (material 12). This corrects the previous six-faced opaque-window effect without globally changing the building facade.
- Preserved all 13 stops, older scene assets, controls, simulated data warnings and roof/section options.
- This is a **concept** future center, not a physical facility. All readings are **SIMULATED**. Neither the existing scene nor this material upgrade is photorealistic.

## Tests and limits
Node syntax (8 scripts), GLB structural verification, ZIP CRC, and actual WebGL browser QA must be documented in QA_v197.json. WebGL testing under virtual X display + SwiftShader is software GPU emulation, NOT physical Samsung Galaxy S25 performance.
'''
( ROOT/'RELEASE_NOTES_v197.md').write_text(notes)
with zipfile.ZipFile(ROOT/'VEIL_Research_Center_v197_PBR_LIVE_CHECKPOINT.zip','w',zipfile.ZIP_DEFLATED) as out:
 for info in Z196.infolist():
  # Preserve previous files. Existing archive root index is stale; replace it with v1.9.7.
  if info.filename=='future-research-center/index.html':continue
  out.writestr(info,Z196.read(info.filename))
 out.writestr('future-research-center/index.html',s)
 out.writestr('future-research-center/VEIL_Research_Center_v197_OPEN_IN_BROWSER.html',s)
 out.writestr('future-research-center/RELEASE_NOTES_v197.md',notes)
 out.writestr('future-research-center/pbr-atlas-v197/base.png',atlases['base'])
 out.writestr('future-research-center/pbr-atlas-v197/metalrough.png',atlases['metalrough'])
 out.writestr('future-research-center/pbr-atlas-v197/manifest.json',json.dumps({'version':'1.9.7','materials':material_names,'tile':136,'padding':4,'atlasSize':[952,136],'liveRenderer':'WebGL triplanar','GLB_UV_unchanged':True},indent=2))
with zipfile.ZipFile(ROOT/'VEIL_Research_Center_v197_PBR_LIVE_CHECKPOINT.zip') as z:assert z.testzip() is None
print(json.dumps({'output':str(OUT),'bytes':OUT.stat().st_size,'atlas_bytes':{k:len(v) for k,v in atlases.items()},'js':script_results,'zip_crc':True},indent=2))