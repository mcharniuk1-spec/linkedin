import { useEffect, useRef } from 'react';
import type { MotionValue } from 'motion/react';
import * as THREE from 'three';
import './experience.css';
import {GLTFLoader} from 'three/examples/jsm/loaders/GLTFLoader.js';
import {mergeGeometries} from 'three/examples/jsm/utils/BufferGeometryUtils.js';
import {createCorticalBrain} from './corticalGeometry';

export type NeuronFieldProps={imageSrc:string;progress?:MotionValue<number>;staticOnly?:boolean;modelSrc?:string;compact?:boolean};
const anchors=[
  {id:'experience',label:'Experience',point:[-1.0,.9,.8],side:'left',y:.27},
  {id:'methods-tools',label:'Methods & tools',point:[-1.35,-.1,.7],side:'left',y:.52},
  {id:'product-judgment',label:'Product judgment',point:[-.8,-1.1,.4],side:'left',y:.77},
  {id:'evidence-cases',label:'Evidence & cases',point:[.85,.85,.75],side:'right',y:.35},
  {id:'customer-insight',label:'Customer insight',point:[1.2,-.55,.6],side:'right',y:.68},
] as const;
const vertex=`attribute float aSeed;attribute float aSize;attribute vec3 aColor;varying vec3 vColor;varying float vSpark;uniform float uTime;uniform float uDpr;uniform float uStill;void main(){vColor=aColor;vSpark=mix(.68+.32*pow(max(0.,sin(uTime*.55+aSeed*23.)),12.),1.,uStill);vec4 mv=modelViewMatrix*vec4(position,1.);gl_Position=projectionMatrix*mv;gl_PointSize=clamp(aSize*uDpr*(7.5/-mv.z),1.,5.*uDpr);}`;
const fragment=`varying vec3 vColor;varying float vSpark;uniform float uOpacity;void main(){vec2 p=gl_PointCoord-.5;float d=length(p);float core=exp(-d*d*32.);float rays=(exp(-abs(p.x)*38.)+exp(-abs(p.y)*38.))*.11;float alpha=(core+rays)*vSpark*uOpacity;if(alpha<.02)discard;gl_FragColor=vec4(vColor,alpha);}`;
/** The licensed HRA reference geometry carries true volume, surface and interior stars.
 * Labels describe the founder-content process. This is an artistic metaphor, not a brain/medical model. */
export function NeuronField({imageSrc,progress,staticOnly=false,modelSrc='/assets/revisions/v3/neural/human-reference-brain-web.glb',compact=false}:NeuronFieldProps){
  const host=useRef<HTMLDivElement>(null),canvas=useRef<HTMLCanvasElement>(null),art=useRef<HTMLImageElement>(null),svg=useRef<SVGSVGElement>(null);
  useEffect(()=>{
    if(!host.current||!canvas.current||!art.current||!svg.current)return;const root=host.current!,view=canvas.current!,image=art.current!,overlay=svg.current!;
    const preference=matchMedia('(prefers-reduced-motion: reduce)');let still=staticOnly||preference.matches,visible=false,disposed=false,ready=false;
    let width=1,height=1,baseScale=1,raf=0,time=0,last=0,p=progress?.get()??.3;
    let pointerX=0,pointerY=0,yaw=still?0:(1-THREE.MathUtils.smoothstep(p,0,compact?.34:.2))*(compact?.62:1.22173),pitch=.10,lastInput=performance.now(),loading=false;
    const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(35,1,.1,100),cloud=new THREE.Group();scene.add(cloud);camera.position.set(0,0,8);
    let renderer:THREE.WebGLRenderer|undefined,geometry:THREE.BufferGeometry|undefined,material:THREE.ShaderMaterial|undefined;
    const cortical=createCorticalBrain();let realGeometry:THREE.BufferGeometry|undefined;let surfaces:THREE.BufferAttribute[]=[];cloud.add(cortical.group);
    const key=new THREE.DirectionalLight('#dce8ff',4.2);key.position.set(-3,5,5);scene.add(key);const rim=new THREE.DirectionalLight('#6a9cff',3);rim.position.set(4,1,-3);scene.add(rim);scene.add(new THREE.HemisphereLight('#b4d1ff','#071024',1.4));
    let anchorPoints=anchors.map(a=>new THREE.Vector3(...a.point));
    const paths=anchors.map(a=>overlay.querySelector<SVGPathElement>(`[data-leader="${a.id}"]`)!);
    const dots=anchors.map(a=>overlay.querySelector<SVGCircleElement>(`[data-dot="${a.id}"]`)!);
    const labels=anchors.map(a=>root.querySelector<HTMLSpanElement>(`[data-label="${a.id}"]`)!);
    function request(){if(!raf&&!disposed&&visible)raf=requestAnimationFrame(draw);}
    function project(){
      const narrow=width<700,rootRect=root.getBoundingClientRect();
      overlay.setAttribute('viewBox',`0 0 ${width} ${height}`);
      const converge=still?0:compact?THREE.MathUtils.smootherstep(p,.64,.84):THREE.MathUtils.smoothstep(p,.50,.70),rank=[0,2,4,1,3];
      const compactRails=compact?(()=>{const board=root.closest('.m-expertise__scene')?.querySelector('.m-expertise__board'),heading=board?.querySelector('h3')?.getBoundingClientRect(),outcome=board?.querySelector('.m-expertise__outcome')?.getBoundingClientRect();return {top:heading?heading.bottom-rootRect.top+14:height*.30,bottom:outcome?outcome.top-rootRect.top-14:height*.83};})():undefined;
      anchors.forEach((anchor,i)=>{
        const world=anchorPoints[i].clone().applyMatrix4(cloud.matrixWorld),point=world.clone().project(camera);
        const x=(point.x*.5+.5)*width,y=(-point.y*.5+.5)*height,label=labels[i];
        const desiredWidth=compact?THREE.MathUtils.lerp(Math.min(180,(width-24)/2),Math.min(288,width-48),converge):narrow?Math.min(180,width*.44):228;
        label.style.width=`${desiredWidth}px`;label.style.setProperty('top','0px','important');label.style.setProperty('left','0px','important');label.style.setProperty('right','auto','important');
        const cardWidth=label.offsetWidth,h=label.offsetHeight,side=compact?8:narrow?16:Math.max(30,width*.035),startX=anchor.side==='left'?side:width-side-cardWidth,startY=height*(compact?[.16,.47,.84,.22,.76][i]:anchor.y)-h/2;
        // Preserve five separate readable titles while their layered cards gather.
        // Original vertical ordering avoids crossed trajectories between the rails.
        const row=rank[i],step=compact?Math.min(52,(compactRails!.bottom-compactRails!.top-h)/4):narrow?44:46,targetX=width*.5-cardWidth/2+(compact?[-3,3,-2,4,-3][row]:[-18,14,-8,20,-12][row]),targetY=compact?compactRails!.top+Math.max(0,(compactRails!.bottom-compactRails!.top-h-4*step)/2)+row*step:height*.5+29+(row-2)*step-h/2;
        const cardX=THREE.MathUtils.lerp(startX,targetX,converge),cardY=THREE.MathUtils.lerp(startY,targetY,converge),roll=(compact?[-.8,.6,-.4,.7,-.6]:[-2,1,-1,1.5,-1.5])[row]*converge;
        label.style.transform=`translate3d(${cardX.toFixed(2)}px,${cardY.toFixed(2)}px,${(row*(compact?2:3)*converge).toFixed(2)}px) rotateX(${((compact?2.5:5)*converge).toFixed(2)}deg) rotateZ(${roll.toFixed(2)}deg)`;
        label.style.zIndex=String(8+row);label.dataset.pose=[cardX,cardY,roll,converge].map(n=>n.toFixed(4)).join(',');label.dataset.cluster=converge===1?'formed':converge>0?'converging':'anchor';
        if(compact){
          const horizontal=x<cardX||x>cardX+cardWidth,sx=horizontal?(x<cardX?cardX-7:cardX+cardWidth+7):THREE.MathUtils.clamp(x,cardX+12,cardX+cardWidth-12),sy=horizontal?THREE.MathUtils.clamp(y,cardY+10,cardY+h-10):y<cardY?cardY-7:cardY+h+7,dx=x-sx,dy=y-sy;
          paths[i].setAttribute('d',`M${sx.toFixed(2)},${sy.toFixed(2)} C${(sx+(horizontal?dx*.5:0)).toFixed(2)},${(sy+(horizontal?0:dy*.5)).toFixed(2)} ${(x-(horizontal?0:dx*.5)).toFixed(2)},${(y-(horizontal?dy*.5:0)).toFixed(2)} ${x.toFixed(2)},${y.toFixed(2)}`);dots[i].setAttribute('r','4');
        }else{
          const sx=anchor.side==='left'?cardX+cardWidth+10:cardX-10,sy=cardY+h/2;
          const elbow=anchor.side==='left'?Math.min(sx+Math.max(18,width*.035),x-16):Math.max(sx-Math.max(18,width*.035),x+16);
          paths[i].setAttribute('d',`M${sx.toFixed(2)},${sy.toFixed(2)} H${elbow.toFixed(2)} L${x.toFixed(2)},${y.toFixed(2)}`);
        }
        dots[i].setAttribute('cx',x.toFixed(2));dots[i].setAttribute('cy',y.toFixed(2));
        label.dataset.anchorWorld=world.toArray().map(n=>n.toFixed(5)).join(',');label.dataset.projected=`${x.toFixed(3)},${y.toFixed(3)}`;label.dataset.mobile=String(narrow);
      });
      root.dataset.cluster=still?'static':p>=.82?'handoff':converge===1?'formed':converge>0?'converging':'anchors';root.dataset.convergence=converge.toFixed(5);
      root.dataset.viewProjection=new THREE.Matrix4().multiplyMatrices(camera.projectionMatrix,camera.matrixWorldInverse).toArray().map(n=>n.toFixed(7)).join(',');
      root.dataset.camera=camera.position.toArray().map(n=>n.toFixed(5)).join(',');root.dataset.cloudMatrix=cloud.matrixWorld.toArray().map(n=>n.toFixed(7)).join(',');
      if(compact&&realGeometry?.boundingBox){
        const box=realGeometry.boundingBox,points:THREE.Vector3[]=[];
        for(const x of [box.min.x,box.max.x])for(const y of [box.min.y,box.max.y])for(const z of [box.min.z,box.max.z])points.push(new THREE.Vector3(x,y,z).applyMatrix4(cloud.matrixWorld).project(camera));
        const xs=points.map(v=>(v.x*.5+.5)*width),ys=points.map(v=>(-.5*v.y+.5)*height);
        root.dataset.brainBounds=[Math.min(...xs),Math.min(...ys),Math.max(...xs)-Math.min(...xs),Math.max(...ys)-Math.min(...ys)].map(v=>v.toFixed(4)).join(',');
        root.dataset.brainGeometryBounds=[...box.min.toArray(),...box.max.toArray()].map(v=>v.toFixed(7)).join(',');
      }
    }
    function draw(now:number){
      raf=0;if(disposed||!visible)return;
      const dt=last?Math.min((now-last)/1000,.04):1/60;last=now;time+=dt;
      const ending=still?0:compact?THREE.MathUtils.smootherstep(p,.66,.86):THREE.MathUtils.smoothstep(p,.50,.78),targetYaw=still?0:(1-THREE.MathUtils.smoothstep(p,0,compact?.34:.2))*(compact?.62:1.22173)+pointerX*.0698,targetPitch=still?.10:.10+pointerY*.045;
      yaw=still?0:THREE.MathUtils.damp(yaw,targetYaw,compact?10:5,dt);pitch=still?0:THREE.MathUtils.damp(pitch,targetPitch,compact?10:5,dt);
      camera.position.set(Math.sin(yaw)*8,Math.sin(pitch)*8,Math.cos(yaw)*8);camera.lookAt(0,0,0);camera.updateMatrixWorld();
      const distance=1-ending*(compact?.08:.2);cloud.scale.setScalar(baseScale*distance);cloud.position.z=-ending*(compact?.7:2.2);cloud.rotation.z=still||compact?0:Math.sin(p*15)*.055*(1-THREE.MathUtils.smoothstep(p,.08,.22));cloud.updateMatrixWorld(true);
      const opacity=1-ending;cortical.material.transparent=opacity<.999;cortical.material.opacity=opacity;cortical.material.depthWrite=opacity>.99;
      if(material){material.uniforms.uTime.value=time;material.uniforms.uStill.value=still?1:0;material.uniforms.uOpacity.value=opacity*(compact?.24:width<700?.30:.66);}
      image.style.opacity=String(renderer?0:opacity);image.style.transform=`translate(-50%,-50%) scale(${distance})`;
      const reveal=still?1:compact?THREE.MathUtils.smootherstep(p,.30,.39):THREE.MathUtils.smoothstep(p,.14,.24);overlay.style.opacity=String(still?1:reveal*(1-(compact?THREE.MathUtils.smootherstep(p,.64,.78):THREE.MathUtils.smoothstep(p,.50,.70))));labels.forEach(label=>label.style.opacity=String(reveal));
      root.dataset.progress=p.toFixed(5);root.dataset.static=String(still);root.dataset.brainOpacity=opacity.toFixed(5);
      renderer?.render(scene,camera);project();
      if(!still&&ready&&(Math.abs(yaw-targetYaw)+Math.abs(pitch-targetPitch)>.0001||now-lastInput<1200))request();
    }
    function resize(){
      width=root.clientWidth;height=root.clientHeight;
      camera.aspect=width/height;camera.updateProjectionMatrix();
      // Fit the full geometry and its front depth to the layout box. Ancestor CSS transforms must not change the scene scale.
      const worldHeight=2*Math.tan(THREE.MathUtils.degToRad(camera.fov/2))*8;
      const artWidth=Math.min(width*(width<700?.96:.70),1060),artHeight=artWidth/1.5;
      const targetHeight=Math.min(height*(compact?.84:.68),compact?640:500),targetWidth=compact?Math.min(width*1.26,650):width*(width<700?.74:.62);
      const desiredExtent=Math.min(worldHeight*targetHeight/height,worldHeight*targetWidth/height);
      const scale=8*desiredExtent/(8*4.1+2.05*desiredExtent);baseScale=scale;cloud.scale.setScalar(scale);root.style.setProperty('--os3-neuron-art-width',`${artWidth}px`);
      root.dataset.baseScale=scale.toFixed(7);
      if(geometry){const total=geometry.getAttribute('position').count,active=compact?Math.min(total,4800):width<700?Math.min(total,7600):total;geometry.setDrawRange(0,active);root.dataset.activePoints=String(active);}
      if(renderer){renderer.setPixelRatio(Math.min(devicePixelRatio||1,compact?1.25:1.5));renderer.setSize(width,height,false);if(material)material.uniforms.uDpr.value=Math.min(devicePixelRatio||1,compact?1.25:1.5);}
      request();
    }
    async function build(){
      if(disposed||ready||loading||!visible||!image.naturalWidth)return;loading=true;
      try{
        try{
          const gltf=await new GLTFLoader().loadAsync(modelSrc);
          if(disposed){gltf.scene.traverse(node=>{if(node instanceof THREE.Mesh){node.geometry.dispose();const materials=Array.isArray(node.material)?node.material:[node.material];materials.forEach(m=>m.dispose());}});return;}
          gltf.scene.updateMatrixWorld(true);const parts:THREE.BufferGeometry[]=[];let meshes=0;
          gltf.scene.traverse(node=>{if(!(node instanceof THREE.Mesh))return;meshes++;let input=node.geometry.clone();if(input.index){const indexed=input;input=input.toNonIndexed();indexed.dispose();}const part=new THREE.BufferGeometry();part.setAttribute('position',input.getAttribute('position').clone());if(input.hasAttribute('normal'))part.setAttribute('normal',input.getAttribute('normal').clone());else part.computeVertexNormals();part.applyMatrix4(node.matrixWorld);parts.push(part);input.dispose();node.geometry.dispose();const materials=Array.isArray(node.material)?node.material:[node.material];materials.forEach(m=>m.dispose());});
          realGeometry=mergeGeometries(parts,false)??undefined;parts.forEach(g=>g.dispose());
          if(!realGeometry)throw new Error('Brain geometry could not merge');
          realGeometry.computeBoundingBox();const box=realGeometry.boundingBox!,center=box.getCenter(new THREE.Vector3()),size=box.getSize(new THREE.Vector3()),scale=4.1/Math.max(size.x,size.y,size.z);realGeometry.translate(-center.x,-center.y,-center.z);realGeometry.scale(scale,scale,scale);
          cloud.remove(cortical.group);const mesh=new THREE.Mesh(realGeometry,cortical.material);mesh.name='HRA_Allen_actual_reference_brain';cloud.add(mesh);surfaces=[realGeometry.getAttribute('position') as THREE.BufferAttribute];
          const vertices=surfaces[0];anchorPoints=anchors.map(a=>{let best=Infinity,result=new THREE.Vector3(...a.point);for(let i=0;i<vertices.count;i+=3){const x=vertices.getX(i),y=vertices.getY(i),z=vertices.getZ(i),score=(x-a.point[0])**2+(y-a.point[1])**2+(z-2.05)**2*.20;if(score<best){best=score;result.set(x,y,z);}}return result;});root.dataset.meshes=String(meshes);root.dataset.geometry='HRA-Allen-real-reference-brain-merged';root.dataset.modelSource=modelSrc;root.dataset.drawMeshes='1';
        }catch(error){surfaces=cortical.geometries.slice(0,3).map(g=>g.getAttribute('position') as THREE.BufferAttribute);root.dataset.meshes='4';root.dataset.geometry='original-artistic-cortical-fallback';root.dataset.modelLoad='fallback';}

        const sample=document.createElement('canvas');sample.width=768;sample.height=512;
        const context=sample.getContext('2d',{willReadFrequently:true});if(!context)return;
        context.drawImage(image,0,0,768,512);const rgba=context.getImageData(0,0,768,512).data;
        const limit=compact?4800:matchMedia('(max-width:700px)').matches?7600:14000,candidates:number[]=[];
        for(let y=0;y<512;y+=2)for(let x=0;x<768;x+=2){const k=(y*768+x)*4,brightness=(rgba[k]+rgba[k+1]+rgba[k+2])/765;if(rgba[k+3]>90&&brightness>.2)candidates.push(k);}
        const count=limit,positions=new Float32Array(count*3),colors=new Float32Array(count*3),seeds=new Float32Array(count),sizes=new Float32Array(count);

        for(let i=0;i<count;i++){
          const surface=surfaces[i%surfaces.length],j=Math.floor((i*.61803398875%1)*surface.count);
          const volume=i%7===0?.45+.5*((i*.41421356237)%1):1;
          positions.set([surface.getX(j)*volume,surface.getY(j)*volume,surface.getZ(j)*volume],i*3);
          const k=candidates[Math.floor((i*.754877666%1)*candidates.length)]??0;
          const b=(rgba[k]+rgba[k+1]+rgba[k+2])/765;
          colors.set([Math.max(.35,rgba[k]/255),Math.max(.54,rgba[k+1]/255),Math.max(.8,rgba[k+2]/255)],i*3);seeds[i]=(i*.61803398875)%1;sizes[i]=1.3+b*2.9;
        }
        geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.BufferAttribute(positions,3));geometry.setAttribute('aColor',new THREE.BufferAttribute(colors,3));geometry.setAttribute('aSeed',new THREE.BufferAttribute(seeds,1));geometry.setAttribute('aSize',new THREE.BufferAttribute(sizes,1));
        material=new THREE.ShaderMaterial({vertexShader:vertex,fragmentShader:fragment,transparent:true,depthWrite:false,depthTest:false,blending:THREE.AdditiveBlending,uniforms:{uTime:{value:0},uDpr:{value:1},uOpacity:{value:.76},uStill:{value:still?1:0}}});
        cloud.add(new THREE.Points(geometry,material));renderer=new THREE.WebGLRenderer({canvas:view,alpha:true,antialias:false,powerPreference:'low-power'});renderer.setClearColor(0,0);renderer.outputColorSpace=THREE.SRGBColorSpace;
        ready=true;root.dataset.points=String(count);root.dataset.renderer='three-cortical-volume';root.dataset.modelLoad=root.dataset.modelLoad??'real-reference-ready';resize();request();
      }catch{root.dataset.renderer='artwork-fallback';ready=true;resize();request();}
    }
    // Record the exact art source, not a synthetic anatomical reconstruction.
    root.dataset.artSource=imageSrc;
    const observer=new IntersectionObserver(records=>{visible=records[0].isIntersecting;root.dataset.visible=String(visible);if(visible){last=0;lastInput=performance.now();build();request();}else{cancelAnimationFrame(raf);raf=0;}},{rootMargin:'80px'});observer.observe(root);
    const resizeObserver=new ResizeObserver(resize);resizeObserver.observe(root);
    const pointer=(event:PointerEvent)=>{if(event.pointerType!=='mouse'||still)return;const rect=root.getBoundingClientRect();pointerX=THREE.MathUtils.clamp(((event.clientX-rect.left)/rect.width-.5)*2,-1,1);pointerY=THREE.MathUtils.clamp(((event.clientY-rect.top)/rect.height-.5)*2,-1,1);lastInput=performance.now();request();};
    const leave=()=>{pointerX=0;pointerY=0;lastInput=performance.now();request();};root.addEventListener('pointermove',pointer);root.addEventListener('pointerleave',leave);
    const preferenceChange=()=>{still=staticOnly||preference.matches;request();};preference.addEventListener('change',preferenceChange);
    const unsubscribe=progress?.on('change',value=>{p=THREE.MathUtils.clamp(value,0,1);lastInput=performance.now();request();});
    image.addEventListener('load',build);resize();if(image.complete)build();
    return()=>{disposed=true;cancelAnimationFrame(raf);observer.disconnect();resizeObserver.disconnect();unsubscribe?.();preference.removeEventListener('change',preferenceChange);root.removeEventListener('pointermove',pointer);root.removeEventListener('pointerleave',leave);image.removeEventListener('load',build);geometry?.dispose();realGeometry?.dispose();material?.dispose();cortical.geometries.forEach(g=>g.dispose());cortical.material.dispose();renderer?.dispose();renderer?.forceContextLoss();};
  },[imageSrc,progress,staticOnly,modelSrc,compact]);
  return <div className="os3-neuron" ref={host} aria-label="Founder knowledge, illustrated as a constellation" role="group">
    <img ref={art} src={imageSrc} alt="" className="os3-neuron__art" decoding="async" loading="lazy"/>
    <canvas ref={canvas} className="os3-neuron__canvas" aria-hidden="true"/>
    <svg ref={svg} className="os3-neuron__leaders" aria-hidden="true">{anchors.map(a=><g key={a.id}><path data-leader={a.id}/><circle data-dot={a.id} r="3"/></g>)}</svg>
    {anchors.map(a=><span key={a.id} data-label={a.id} className={`os3-neuron__label os3-neuron__label--${a.side}`} style={{top:`${a.y*100}%`}}>{a.label}</span>)}
  </div>;
}
