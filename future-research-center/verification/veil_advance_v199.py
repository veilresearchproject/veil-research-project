"""VEIL v1.9.9: reproducible physically motivated WebGL material and grounding update.
Run: python veil_advance_v199.py v198.html v199.html
No external dependencies or network calls. Does not change live website.
"""
from pathlib import Path
import sys

def one(s, old, new):
    n=s.count(old)
    if n!=1: raise RuntimeError(f'Expected one replacement, found {n}: {old[:90]}')
    return s.replace(old,new,1)

def build(src, dst):
    s=Path(src).read_text(encoding='utf-8')
    s=one(s,"version:'1.9.8-mobile-nav-acrylic-depth'","version:'1.9.9-linear-pbr-indirect-light'")
    # Source hex RGB and PNG atlases are sRGB, not linear light. Convert BEFORE lighting.
    s=one(s,'vec3 n=normalize(vNormal); vec3 toEye=normalize(uEye-vWorld); vec3 c=vCol;',
          'vec3 n=normalize(vNormal); vec3 toEye=normalize(uEye-vWorld); vec3 c=pow(max(vCol,vec3(0.0)),vec3(2.2));')
    s=one(s,'vec3 texBase=texture2D(uPBRBaseAtlas,atlasUV).rgb;',
          'vec3 texBase=pow(texture2D(uPBRBaseAtlas,atlasUV).rgb,vec3(2.2));')
    # Reduce ambient fill and distance haze; keep directional key and fixture lighting.
    s=one(s,'vec3 lighting=mix(vec3(.50,.58,.64),vec3(.26,.36,.51),uSceneMode);',
          'vec3 lighting=mix(vec3(.34,.40,.46),vec3(.20,.28,.39),uSceneMode);')
    s=one(s,'vFog=clamp((p.w-18.0)/145.0,0.0,0.58);',
          'vFog=clamp((p.w-32.0)/190.0,0.0,0.36);')
    # Extend actual floor contact shadows to the GB-001 chamber and nearby camera tripods.
    s=one(s,'uniform vec3 uFootprints[8];','uniform vec3 uFootprints[12];')
    s=one(s,'for(int i=0;i<8;i++){\n   vec3 f=uFootprints[i];',
          'for(int i=0;i<12;i++){\n   vec3 f=uFootprints[i];')
    s=one(s,'43.0, 13, 6.8]);',
          '43.0, 13, 6.8, -24.0, 18.0, 3.2, -26.3, 17.1, .85, -21.7, 17.1, .85, -24.0, 20.2, 1.1]);')
    # Bounded indirect wall/floor bounce for the GB-001 room. No claim of path tracing.
    s=one(s,'// Soft grounded contact shadows tied to instrument/fixture footprints, only on the floor.',
'''// v1.9.9 approximate first-bounce indirect illumination in the GB-001 lab.
 // Floor bounce is warmer under downward-facing surfaces; walls return cool fill.
 // This is bounded analytical lighting, not ray-traced global illumination.
 float labX=smoothstep(-32.0,-29.8,vWorld.x)*(1.0-smoothstep(-18.8,-16.8,vWorld.x));
 float labZ=smoothstep(12.0,14.0,vWorld.z)*(1.0-smoothstep(22.0,24.3,vWorld.z));
 float labWeight=labX*labZ;
 float floorBounce=clamp(-n.y,0.0,1.0);
 lighting+=labWeight*(vec3(.065,.082,.086)+vec3(.12,.095,.075)*floorBounce);
 // Soft grounded contact shadows tied to instrument/fixture footprints, only on the floor.''')
    # Replace stylized highlight with a bounded, energy-aware GGX microfacet key-light term.
    s=one(s,''' vec3 keyDir=normalize(vec3(-.43,.75,-.51));
 vec3 halfway=normalize(keyDir+toEye);
 float ndv=clamp(dot(n,toEye),0.0,1.0);
 float ndh=max(dot(n,halfway),0.0);
 float fresnel=f0+(1.0-f0)*pow(1.0-ndv,5.0);
 float glossPower=mix(108.0,7.0,roughness);
 float highlight=pow(ndh,glossPower)*(1.0-roughness*.65)*sunDiffuse;
 gleam+=vec3(1.0,.96,.88)*highlight*fresnel*1.8;''',
'''  vec3 keyDir=normalize(vec3(-.43,.75,-.51));
 vec3 halfway=normalize(keyDir+toEye);
 float ndv=max(dot(n,toEye),.001);
  float ndl=max(dot(n,keyDir),0.0);
 float ndh=max(dot(n,halfway),.001);
  float vdh=max(dot(toEye,halfway),.001);
  float a=max(.045,roughness*roughness);
  float a2=a*a;
  float ggxD=a2/(3.14159265*pow(ndh*ndh*(a2-1.0)+1.0,2.0)+.0001);
  float k=pow(roughness+1.0,2.0)/8.0;
  float ggxG=(ndl/(ndl*(1.0-k)+k+.0001))*(ndv/(ndv*(1.0-k)+k+.0001));
  float ggxF=f0+(1.0-f0)*pow(1.0-vdh,5.0);
  float microfacet=clamp(ggxD*ggxG*ggxF/(4.0*ndl*ndv+.0001),0.0,1.5);
  gleam+=vec3(1.0,.96,.90)*microfacet*ndl*.75;''')
    s=one(s,'vec3 shaded=c*max(lighting,vec3(0.0))+gleam;',
          'vec3 shaded=c*max(lighting,vec3(0.0))*(1.0-.35*clamp(pbrMR.b,0.0,1.0))+gleam;')
    s=one(s,"window.VEIL_PBR_RENDERER={mode:'real atlas textures sampled by WebGL'",
          "window.VEIL_PBR_RENDERER={mode:'sRGB-to-linear atlas + GGX key + bounded indirect bounce sampled by WebGL'")
    Path(dst).write_text(s,encoding='utf-8')
    return {'source_bytes':len(Path(src).read_bytes()),'result_bytes':len(Path(dst).read_bytes())}

if __name__=='__main__':
    print(build(sys.argv[1],sys.argv[2]))