// VEIL v1.8 — Flexible Experiment Room / GB-001 correlation lab.
// All objects below are actual editable world-coordinate triangle meshes.
// Proposed concept only: no facility exists; telemetry is synthetic demonstration graphics.
const VEIL_FLEX_V18=[];
function v18Group(name,center,radius){
 const g=veilArchGroup(name,center,radius,'permanent');g.v18=true;
 VEIL_FLEX_V18.push(g);return g;
}
function v18Box(g,c,s,col,mat=2,bevel=.07){
 veilChamferedBox(g,c,s,Math.min(...s)*bevel,col,mat);
}
function v18Quad(g,a,b,c,d,col,mat=2){veilArchQuad(g,a,b,c,d,col,mat);}
function v18Tube(g,a,b,r,color,mat=2,steps=10){
 const d=[b[0]-a[0],b[1]-a[1],b[2]-a[2]],L=Math.hypot(...d);if(L<.0001)return;
 const w=d.map(v=>v/L),t=Math.abs(w[1])<.85?[0,1,0]:[1,0,0];
 let u=[w[1]*t[2]-w[2]*t[1],w[2]*t[0]-w[0]*t[2],w[0]*t[1]-w[1]*t[0]];
 const ul=Math.hypot(...u);u=u.map(v=>v/ul);
 const v=[w[1]*u[2]-w[2]*u[1],w[2]*u[0]-w[0]*u[2],w[0]*u[1]-w[1]*u[0]];
 const ring=(p,i)=>p.map((q,j)=>q+r*(u[j]*Math.cos(i*2*Math.PI/steps)+v[j]*Math.sin(i*2*Math.PI/steps)));
 for(let i=0;i<steps;i++){
  const a0=ring(a,i),a1=ring(a,i+1),b0=ring(b,i),b1=ring(b,i+1);
  veilArchTri(g,a0,b0,b1,color,mat);veilArchTri(g,a0,b1,a1,color,mat);
 }
}
function v18Path(g,points,r,col,mat=2){for(let i=0;i<points.length-1;i++)v18Tube(g,points[i],points[i+1],r,col,mat,9);}
function v18Acrylic(g,x0,x1,y0,y1,z){
 // Thin, actual glass panel. New translucent material 11 is drawn separately in GPU,
 // and in depth order by the Canvas fallback. Not a textured photograph.
 v18Quad(g,[x0,y0,z],[x1,y0,z],[x1,y1,z],[x0,y1,z],'#b9e6e7',11);
}
function v18AcrylicSide(g,x,y0,y1,z0,z1){
 v18Quad(g,[x,y0,z0],[x,y0,z1],[x,y1,z1],[x,y1,z0],'#b9e6e7',11);
}
// A real geometry-based isolated floor platform with staggered panel joints,
// isolation-foot plinths and a shallow inset protective perimeter.
{
 const g=v18Group('GB-001 resilient platform and machined floor edge',[-24,.11,18],3.3);
 v18Box(g,[-24,.075,18],[4.85,.13,3.38],'#2c3940',2,.025);
 v18Box(g,[-24,.155,18],[4.63,.034,3.18],'#566872',2,.03);
 for(let row=0;row<4;row++)for(let col=0;col<7;col++){
  const x=-26.12+col*.70+(row%2)*.07,z=16.68+row*.77;
  v18Box(g,[x,.179,z],[.645,.018,.705],(row+col)%3===0?'#566773':'#65747a',1,.05);
 }
 for(const x of [-26.27,-21.73])for(const z of [16.55,19.45]){
  veilCylinder(g,[x,.105,z],.105,.14,'y','#9eabb2',2,14);
  veilCylinder(g,[x,.19,z],.047,.04,'y','#b7c4c9',2,12);
 }
}
// The primary test object is a modeled clear sealed acrylic chamber with metal
// corner extrusions and an inert reference target on an isolated mounting plate.
// The front and side glazing is deliberately transparent, not a solid opaque cube.
{
 const g=v18Group('GB-001 sealed acrylic chamber and anti-vibration cradle',[-24,1.70,18],2.2);
 const x0=-25.36,x1=-22.64,z0=17.39,z1=18.61,y0=1.01,y1=2.36;
 v18Box(g,[-24,1.005,18],[2.89,.13,1.38],'#c4c9c8',2,.055);
 v18Box(g,[-24,1.105,18],[2.66,.055,1.16],'#273b43',2,.055);
 for(const x of [x0,x1])for(const z of [z0,z1]){
  v18Tube(g,[x,y0,z],[x,y1,z],.045,'#bdced4',2,12);
  veilCylinder(g,[x,1.02,z],.075,.11,'y','#536b77',2,12);
  veilCylinder(g,[x,2.36,z],.066,.08,'y','#7f9ba8',2,12);
 }
 for(const y of [y0,y1]){
  for(const z of [z0,z1])v18Tube(g,[x0,y,z],[x1,y,z],.039,'#aebfc8',2,12);
  for(const x of [x0,x1])v18Tube(g,[x,y,z0],[x,y,z1],.038,'#aebfc8',2,12);
 }
 // Glass is separate from the opaque frame so its translucency is correct.
 const glass=v18Group('GB-001 four optically clear acrylic panels',[-24,1.68,18],2.0);
 v18Acrylic(glass,x0+.05,x1-.05,y0+.04,y1-.05,z0+.009);
 v18Acrylic(glass,x0+.05,x1-.05,y0+.04,y1-.05,z1-.009);
 v18AcrylicSide(glass,x0+.009,y0+.04,y1-.05,z0+.05,z1-.05);
 v18AcrylicSide(glass,x1-.009,y0+.04,y1-.05,z0+.05,z1-.05);
 const target=v18Group('GB-001 inert calibration target and isolation stage',[-24,1.39,18],.95);
 v18Box(target,[-24,1.22,18],[.62,.15,.52],'#465c65',2,.15);
 for(const x of [-24.21,-23.79])for(const z of [17.84,18.16]){
  veilCylinder(target,[x,1.14,z],.05,.10,'y','#b5c4c9',2,14);
 }
 veilCylinder(target,[-24,1.45,18],.19,.27,'y','#e6cda5',2,24);
 veilTorus(target,[-24,1.62,18],.19,.033,'xz','#7bd5c9',3,30,8);
 veilCylinder(target,[-24,1.67,18],.065,.08,'y','#d5e5df',3,16);
 // Actual model latches and a gasket, not just a glass-looking texture.
 for(const x of [-24.75,-23.25]){
  v18Box(g,[x,2.378,17.38],[.24,.035,.10],'#82969f',2);
  v18Tube(g,[x,2.38,17.33],[x,2.50,17.33],.022,'#b6c4cb',2,10);
 }
}
// Four independently oriented, lens-equipped observation heads, with actual
// camera barrels, annular lenses, articulated mount and cable harness geometry.
for(let i=0;i<4;i++){
 const x=[-26.15,-21.85,-26.15,-21.85][i],z=[16.95,16.95,19.05,19.05][i];
 const g=v18Group('GB-001 optical-depth camera and vibration mount '+(i+1),[x,1.85,z],1.3);
 v18Box(g,[x,.52,z],[.32,.09,.32],'#5e7079',2);
 v18Tube(g,[x,.52,z],[x,2.11,z],.045,'#879da6',2,12);
 v18Tube(g,[x,2.10,z],[x+(x<-24?.24:-.24),2.25,z],.033,'#b6c4c8',2,12);
 const inward=z<18?.22:-.22;
 veilCylinder(g,[x,2.25,z+inward],.155,.31,'z','#354953',2,22);
 veilTorus(g,[x,2.25,z+inward+(inward>0?.17:-.17)],.118,.022,'xy','#b5d6d9',2,30,9);
 veilCylinder(g,[x,2.25,z+inward+(inward>0?.22:-.22)],.076,.018,'z','#173d51',4,20);
 veilTorus(g,[x,2.25,z+inward+(inward>0?.24:-.24)],.035,.012,'xy','#65d4d6',3,20,7);
 const p=[[x,2.09,z],[x,1.73,z+(z<18?-.15:.15)],[x,1.10,z+(z<18?-.15:.15)],[x,1.03,17.95]];
 v18Path(g,p,.021,'#253e49',2);
}
// Depth + thermal spatial-correlation arch: two physically separate sensor
// rails and modular sampled-temperature heads. Display data remains simulated.
{
 const g=v18Group('Spatial thermal correlation structural arch',[-24,2.72,20.04],5.6);
 for(const x of [-29.0,-19.0]){
  v18Tube(g,[x,.12,20.02],[x,3.72,20.02],.073,'#9cb3bc',2,14);
  v18Box(g,[x,.12,20.02],[.44,.15,.46],'#586d79',2);
  v18Box(g,[x,3.73,20.02],[.30,.18,.30],'#6e8893',2);
 }
 for(const y of [2.55,3.56])v18Tube(g,[-29.0,y,20.02],[-19.0,y,20.02],.051,'#92a9b3',2,12);
 for(let i=0;i<17;i++){
  const x=-28.75+i*.59;
  const h=v18Group('Spatial thermal array sampled sensor '+(i+1),[x,2.55,19.94],.25);
  v18Box(h,[x,2.55,19.95],[.20,.19,.19],'#435965',2,.18);
  veilCylinder(h,[x,2.55,19.80],.065,.08,'z','#8bc5d2',3,16);
  v18Box(h,[x,3.58,20.03],[.14,.12,.16],i%4===0?'#8dc6cb':'#728f9d',2);
 }
 // Visual calibration registration ticks on the frame, not fake detections.
 for(let j=0;j<11;j++){
  const x=-28.5+j*.9;
  v18Tube(g,[x,2.60,19.98],[x,2.72,19.98],.012,'#d4e4e3',3,8);
 }
}
// Two physical wall review boards: graticule, registration grid and simulated
// temperature/depth correlation curves are all thin actual 3D ribbons.
for(let i=0;i<2;i++){
 const cx=[-28,-22][i],z=23.06;
 const g=v18Group('Flexible room SIMULATED thermal-depth analysis panel '+(i+1),[cx,2.23,z],1.9);
 v18Box(g,[cx,2.23,z+.005],[3.0,1.58,.10],'#1c303d',2);
 v18Quad(g,[cx-1.37,1.64,z-.055],[cx+1.37,1.64,z-.055],[cx+1.37,2.87,z-.055],[cx-1.37,2.87,z-.055],'#163441',2);
 for(let j=0;j<9;j++){
  const x=cx-1.27+j*.31;
  v18Quad(g,[x,1.71,z-.070],[x+.008,1.71,z-.070],[x+.008,2.75,z-.070],[x,2.75,z-.070],'#284956',2);
 }
 for(let j=0;j<5;j++){
  const y=1.76+j*.225;
  v18Quad(g,[cx-1.27,y,z-.075],[cx+1.26,y,z-.075],[cx+1.26,y+.008,z-.075],[cx-1.27,y+.008,z-.075],'#2b4d5a',2);
 }
 for(let j=0;j<32;j++){
  const x0=cx-1.23+j*2.44/32,x1=cx-1.23+(j+1)*2.44/32;
  const y0=2.21+.24*Math.sin(j*.25+i*.9)+.07*Math.cos(j*.81+i);
  const y1=2.21+.24*Math.sin((j+1)*.25+i*.9)+.07*Math.cos((j+1)*.81+i);
  v18Tube(g,[x0,y0,z-.085],[x1,y1,z-.085],.012,i?'#d2b98d':'#78d4d1',3,6);
 }
 for(let j=0;j<7;j++){
  const x=cx-1.18+j*.35;
  const h=.06+.24*Math.abs(Math.sin(j*.71+i));
  v18Quad(g,[x,1.78,z-.09],[x+.12,1.78,z-.09],[x+.12,1.78+h,z-.09],[x,1.78+h,z-.09],j%2?'#54879b':'#8bc7c2',3);
 }
 for(let j=0;j<4;j++){
  const x=cx+.83+j*.11;
  v18Box(g,[x,2.77,z-.07],[.055,.045,.035],j===0?'#8ed8b8':'#a0bec9',3);
 }
}
// Ceiling baffles and soft diffused luminaires physically fit within the 4.4 m
// room, replacing an empty dark ceiling view with a plausible lighting study.
for(let i=0;i<3;i++)for(let j=0;j<2;j++){
 const x=-28.2+i*4.2,z=16.4+j*4.35;
 const g=v18Group('Flexible lab recessed softbox diffuser '+(i*2+j+1),[x,3.93,z],1.8);
 v18Box(g,[x,3.94,z],[2.66,.15,1.38],'#415864',2,.09);
 v18Box(g,[x,3.843,z],[2.40,.025,1.12],'#d4e6e5',3,.08);
 for(let k=0;k<7;k++){
  const px=x-1.04+k*.35;
  v18Box(g,[px,3.818,z],[.038,.034,1.11],'#91aeb9',2);
 }
 for(const px of [x-1.22,x+1.22]){
  v18Tube(g,[px,4.02,z],[px,4.24,z],.022,'#9eafb7',2,8);
 }
}
// More believable perimeter wall fit-out: removable absorptive panels with
// bevels and cable raceway, plus a 3D status/control pedestal.
for(let i=0;i<8;i++){
 const x=-30.6+i*1.72;
 const g=v18Group('Flexible lab back-wall acoustic diffuser '+(i+1),[x,3.50,23.72],.9);
 v18Box(g,[x,3.49,23.66],[1.55,.64,.17],i%2?'#596d78':'#6a7d83',8,.11);
 for(let k=0;k<5;k++){
  const px=x-.58+k*.29;
  v18Box(g,[px,3.49,23.545],[.046,.51,.045],'#8ba0aa',8,.07);
 }
}
{
 const g=v18Group('GB-001 instrument control and power isolation console',[-19.3,1.18,17.9],1.6);
 v18Box(g,[-19.3,.69,17.9],[.9,1.34,.68],'#4b6470',2);
 v18Box(g,[-19.3,1.37,17.84],[.98,.15,.76],'#9eafb4',2);
 v18Box(g,[-19.3,1.50,17.63],[.70,.30,.09],'#203746',2);
 for(let i=0;i<5;i++){
  const x=-19.58+i*.14;
  veilCylinder(g,[x,1.52,17.57],.038,.045,'z',i===0?'#70dfb8':'#78abc5',3,12);
 }
 for(let i=0;i<3;i++)veilCylinder(g,[-19.54+i*.23,1.30,17.55],.065,.08,'z','#c5d5d5',2,16);
 v18Path(g,[[-19.72,1.02,18.10],[-20.1,.35,18.10],[-22.4,.35,18.10]],.030,'#29444c',2);
}
window.VEIL_FLEX_V18={version:'1.8.0',room:'Flexible Experiment Room',
 meshGroups:VEIL_FLEX_V18.length,
 triangles:VEIL_FLEX_V18.reduce((n,g)=>n+g.triangles.length,0),
 acrylicGroups:VEIL_FLEX_V18.filter(g=>g.triangles.some(t=>t.m===11)).length,
 purpose:'Conceptual GB-001 isolation chamber and independently instrumented spatial/thermal correlation station',
 simulationDisclaimer:'Inert calibration object; screen waveforms and indicators are illustrative simulations. No live or paranormal data.'};