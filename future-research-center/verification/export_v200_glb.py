"""Offline glTF 2.0 PBR export of new VEIL v2.0.0 room geometry.
Deterministic texture creation, authored planar UVs, per-group meshes.
"""
import json,math,hashlib,struct
from collections import defaultdict
from pathlib import Path
import numpy as np
from PIL import Image
import trimesh
from trimesh.visual.material import PBRMaterial
from trimesh.visual.texture import TextureVisuals
ROOT=Path('/mnt/data/veil_v200_work')
source=json.loads((ROOT/'VEIL_GB001_Architecture_v200_geometry.json').read_text())
scene=trimesh.Scene()
texture_cache={}

def tex(color,mat):
 key=(color,mat)
 if key in texture_cache:return texture_cache[key]
 rgb=tuple(int(color[i:i+2],16) for i in (1,3,5))
 yy,xx=np.indices((64,64))
 # Small repeatable roughness and pigment variations, not a photographic overlay.
 grain=((xx*13+yy*17+((xx*yy)%11)*7)%23)-11
 variation=grain*(.40 if mat==8 else .28 if mat==1 else .16)
 arr=np.empty((64,64,4),dtype=np.uint8)
 for i in range(3):arr[:,:,i]=np.clip(rgb[i]+variation,0,255)
 arr[:,:,3]=255
 rough={1:220,2:105,8:228}[mat]
 metallic={1:3,2:177,8:0}[mat]
 mr=np.zeros((64,64,4),dtype=np.uint8)
 mr[:,:,0]=255
 mr[:,:,1]=np.clip(rough+grain*.18,0,255)
 mr[:,:,2]=metallic
 mr[:,:,3]=255
 base=Image.fromarray(arr,'RGBA');metal=Image.fromarray(mr,'RGBA')
 texture_cache[key]=(base,metal)
 return base,metal

def uv_point(p,n):
 ax=np.argmax(np.abs(n))
 if ax==1:return [p[0]*.36,p[2]*.36]
 if ax==0:return [p[2]*.36,p[1]*.36]
 return [p[0]*.36,p[1]*.36]

primitive_count=0
for gi,g in enumerate(source['groups']):
 batches=defaultdict(list)
 for tri in g['triangles']:batches[(tri['c'],tri['m'])].append(tri)
 for bi,((color,mat),tris) in enumerate(sorted(batches.items())):
  vertices=[];uv=[]
  for t in tris:
   for p in t['p']:
    vertices.append(p);uv.append(uv_point(p,t['n']))
  vertices=np.array(vertices,dtype=np.float32)
  mesh=trimesh.Trimesh(vertices=vertices,faces=np.arange(len(vertices)).reshape(-1,3),process=False)
  base,mr=tex(color,mat)
  material=PBRMaterial(name=f'{g["name"]} | {color} | {mat}',baseColorFactor=[255,255,255,255],baseColorTexture=base,metallicRoughnessTexture=mr,metallicFactor=1.0,roughnessFactor=1.0,doubleSided=True)
  mesh.visual=TextureVisuals(uv=np.array(uv,dtype=np.float32),material=material)
  scene.add_geometry(mesh,geom_name=f'v200_g{gi:02d}_m{mat}_{bi:02d}')
  primitive_count+=1
out=ROOT/'VEIL_GB001_Architecture_v200_PBR.glb'
out.write_bytes(trimesh.exchange.gltf.export_glb(scene))
check=trimesh.load(out,force='scene',process=False)
assert sum(len(x.faces) for x in check.geometry.values())==source['metadata']['triangles']
assert len(check.geometry)==primitive_count
blob=out.read_bytes()
assert blob[:4]==b'glTF' and struct.unpack_from('<I',blob,4)[0]==2
jlen,jtype=struct.unpack_from('<I4s',blob,12)
assert jtype==b'JSON'
gltf=json.loads(blob[20:20+jlen].decode('utf-8').rstrip(' \x00'))
assert gltf['asset']['version']=='2.0'
assert len(gltf['images'])>=3 and len(gltf['textures'])>=3
assert all('TEXCOORD_0' in prim['attributes'] for m in gltf['meshes'] for prim in m['primitives'])
report={'version':'2.0.0','triangles':source['metadata']['triangles'],'sourceGroups':source['metadata']['groups'],'gltfMeshes':len(gltf['meshes']),'gltfPrimitives':sum(len(m['primitives']) for m in gltf['meshes']),'images':len(gltf['images']),'textures':len(gltf['textures']),'materials':len(gltf['materials']),'uvMapped':True,'glbBytes':len(blob),'sha256':hashlib.sha256(blob).hexdigest(),'roundtrip':'PASS'}
(ROOT/'VEIL_v200_GLB_QA.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))