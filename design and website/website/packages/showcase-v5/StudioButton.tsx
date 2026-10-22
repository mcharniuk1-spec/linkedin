import { forwardRef, useCallback, useEffect, useRef, type ButtonHTMLAttributes } from 'react';
import * as THREE from 'three';
import './showcase.css';

export type StudioButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: 'primary' | 'secondary';
  edge?: 'base'|'bevel'|'groove'|'cut'|'rail';
  pose?: 'front'|'left'|'right';
  loading?: boolean;
  tone?: 'navy'|'cobalt'|'white'|'citron'|'nickel'|'pearl'|'black';
  arrow?: boolean;
};
type Entry = {
  button: HTMLButtonElement; canvas: HTMLCanvasElement; ink: HTMLSpanElement;
  width: number; height: number; x: number; y: number; vx: number; vy: number;
  tx: number; ty: number; active: boolean; dirty: boolean;
  mesh: THREE.Mesh<THREE.ExtrudeGeometry, THREE.MeshPhysicalMaterial>;
};
const colors = {navy:'#162760',cobalt:'#3157D5',white:'#FFFFFF',citron:'#D4DD67',nickel:'#A9AFBA',pearl:'#F1F3F6',black:'#101218'};
const entries = new Set<Entry>();
let renderer: THREE.WebGLRenderer | undefined;
let scene: THREE.Scene | undefined;
let camera: THREE.OrthographicCamera | undefined;
let key: THREE.DirectionalLight | undefined;
let rim: THREE.PointLight | undefined;
let frame = 0, lastTime = 0, renderWidth = 1, renderHeight = 1;

function createRenderer() {
  if (renderer) return true;
  try {
    renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true, preserveDrawingBuffer: true, powerPreference: 'low-power' });
    renderer.setPixelRatio(1);
    renderer.setClearColor(0x000000, 0);
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.4;
    scene = new THREE.Scene();
    camera = new THREE.OrthographicCamera(-2, 2, 1, -1, .1, 30);
    camera.position.set(0, 0, 8);
    scene.add(new THREE.HemisphereLight(0xf9fcff, 0x101b39, 2.2));
    key = new THREE.DirectionalLight(0xffffff, 4.2); key.position.set(-3, 4, 6); scene.add(key);
    rim = new THREE.PointLight(0xd4dd67, 5, 20); rim.position.set(3, 2, 4); scene.add(rim);
    return true;
  } catch { renderer?.dispose(); renderer = undefined; return false; }
}
function geometry(aspect: number) {
  const w = aspect * 1.82, h = 1.82, radius = .26;
  const s = new THREE.Shape();
  s.moveTo(-w/2+radius,-h/2); s.lineTo(w/2-radius,-h/2);
  s.quadraticCurveTo(w/2,-h/2,w/2,-h/2+radius); s.lineTo(w/2,h/2-radius);
  s.quadraticCurveTo(w/2,h/2,w/2-radius,h/2); s.lineTo(-w/2+radius,h/2);
  s.quadraticCurveTo(-w/2,h/2,-w/2,h/2-radius); s.lineTo(-w/2,-h/2+radius);
  s.quadraticCurveTo(-w/2,-h/2,-w/2+radius,-h/2);
  return new THREE.ExtrudeGeometry(s, { depth: .09, bevelEnabled: true, bevelSegments: 3, steps: 1, bevelSize: .035, bevelThickness: .035, curveSegments: 12 });
}
function schedule() { if (!frame) frame = requestAnimationFrame(render); }
function render(time: number) {
  frame = 0;
  if (!renderer || !scene || !camera || !rim) return;
  const dt = lastTime ? Math.min((time - lastTime)/1000, .035) : 1/60;
  lastTime = time;
  let moving = false;
  for (const entry of entries) {
    const dx = entry.tx-entry.x, dy = entry.ty-entry.y;
    entry.vx += (dx*190-entry.vx*25)*dt; entry.vy += (dy*190-entry.vy*25)*dt;
    entry.x += entry.vx*dt; entry.y += entry.vy*dt;
    const unsettled = Math.abs(dx)+Math.abs(dy)+Math.abs(entry.vx)+Math.abs(entry.vy) > .0007;
    if (!entry.dirty && !unsettled) continue;
    entry.dirty = false;
    const ratio = Math.min(window.devicePixelRatio || 1, 1.75);
    const w = Math.max(1, Math.round(entry.width*ratio)), h = Math.max(1, Math.round(entry.height*ratio));
    if (entry.canvas.width !== w || entry.canvas.height !== h) {entry.canvas.width=w;entry.canvas.height=h;}
    if (w>renderWidth || h>renderHeight) {renderWidth=Math.max(renderWidth,w);renderHeight=Math.max(renderHeight,h);renderer.setSize(renderWidth,renderHeight,false);}
    renderer.setScissorTest(true); renderer.setViewport(0,0,w,h);renderer.setScissor(0,0,w,h);
    const aspect = entry.width/entry.height;
    camera.left=-aspect; camera.right=aspect;camera.top=1;camera.bottom=-1;camera.updateProjectionMatrix();
    entry.mesh.rotation.set(entry.x,entry.y,0);
    entry.mesh.material.emissiveIntensity=entry.active?.045:0;
    rim.intensity=entry.active?9:3.5; rim.position.x=3+entry.y*12;rim.position.y=2-entry.x*10;
    scene.add(entry.mesh); renderer.clear(); renderer.render(scene,camera);scene.remove(entry.mesh);
    const paint = entry.canvas.getContext('2d');paint?.clearRect(0,0,w,h);paint?.drawImage(renderer.domElement,0,renderHeight-h,w,h,0,0,w,h);
    entry.ink.style.transform=`perspective(650px) rotateX(${entry.x*180/Math.PI}deg) rotateY(${entry.y*180/Math.PI}deg)`;
    entry.button.dataset.rotation=`${entry.x.toFixed(4)},${entry.y.toFixed(4)}`;
    entry.button.dataset.renderer='three';
    moving ||= unsettled;
  }
  if (moving) schedule(); else lastTime=0;
}
function release(entry: Entry) {
  entries.delete(entry);entry.mesh.geometry.dispose();entry.mesh.material.dispose();
  if (!entries.size) {
    cancelAnimationFrame(frame);frame=0;lastTime=0;
    renderer?.dispose();renderer?.forceContextLoss();renderer=undefined;scene=undefined;camera=undefined;
    renderWidth=1;renderHeight=1;
  }
}
/** One shared offscreen WebGL renderer paints separate decorative 2D canvases.
 * Native buttons remain the hit targets. No renderer or animation loop survives offscreen. */
export const StudioButton = forwardRef<HTMLButtonElement, StudioButtonProps>(function StudioButton(
  { children, variant='primary', tone=variant==='primary'?'navy':'nickel', edge='base',pose='front', loading=false, disabled=false, arrow=true, className='', onPointerMove, onPointerLeave, onPointerCancel, onFocus, onBlur, onPointerDown, ...props }, forwardedRef,
) {
  const button = useRef<HTMLButtonElement>(null), canvas = useRef<HTMLCanvasElement>(null), ink = useRef<HTMLSpanElement>(null), entry = useRef<Entry | undefined>(undefined);
  const reduced = useRef(false), blocked = disabled || loading;
  const attach = useCallback((node: HTMLButtonElement | null) => {
    button.current=node;
    if (typeof forwardedRef==='function') forwardedRef(node); else if(forwardedRef) forwardedRef.current=node;
  }, [forwardedRef]);
  useEffect(() => {
    const target=button.current, paper=canvas.current, text=ink.current;
    if(!target||!paper||!text||blocked) return;
    const preference=matchMedia('(prefers-reduced-motion: reduce)');
    const syncPreference=()=>{reduced.current=preference.matches;if(entry.current){entry.current.tx=0;entry.current.ty=0;if(preference.matches){entry.current.x=0;entry.current.y=0;entry.current.vx=0;entry.current.vy=0;}entry.current.dirty=true;schedule();}};
    syncPreference();preference.addEventListener('change',syncPreference);
    const add=()=>{
      if(entry.current || !createRenderer()) return;
      const rect=target.getBoundingClientRect();
      const material=new THREE.MeshPhysicalMaterial({color:variant==='secondary'?'#FFFFFF':colors[tone],metalness:tone==='nickel'?.76:.38,roughness:.3,clearcoat:.42,clearcoatRoughness:.26,emissive:colors[tone],emissiveIntensity:0});
      const item:Entry={button:target,canvas:paper,ink:text,width:rect.width,height:rect.height,x:0,y:0,vx:0,vy:0,tx:0,ty:0,active:false,dirty:true,mesh:new THREE.Mesh(geometry(rect.width/rect.height),material)};
      entry.current=item;entries.add(item);schedule();
    };
    const remove=()=>{if(entry.current){release(entry.current);entry.current=undefined;}target.dataset.renderer='fallback';paper.getContext('2d')?.clearRect(0,0,paper.width,paper.height);text.style.transform='';};
    const observer=new IntersectionObserver(records=>{if(records[0].isIntersecting)add();else remove();},{rootMargin:'40px'});observer.observe(target);
    const resize=new ResizeObserver(()=>{
      const item=entry.current;if(!item)return;const rect=target.getBoundingClientRect();
      if(Math.abs(rect.width-item.width)+Math.abs(rect.height-item.height)<.5)return;
      item.width=rect.width;item.height=rect.height;item.mesh.geometry.dispose();item.mesh.geometry=geometry(rect.width/rect.height);item.dirty=true;schedule();
    });resize.observe(target);
    return()=>{observer.disconnect();resize.disconnect();preference.removeEventListener('change',syncPreference);remove();};
  }, [tone,variant,blocked]);
  const reset=()=>{const item=entry.current;if(item){item.tx=0;item.ty=0;item.active=false;item.dirty=true;schedule();}};
  const focus=()=>{const item=entry.current;if(item){item.active=true;item.dirty=true;schedule();}};
  return <button {...props} ref={attach} type={props.type??'button'} data-pose={pose} data-edge={edge} data-tone={tone} data-variant={variant} style={{'--os5-tone':colors[tone],'--os5-ink':variant==='secondary'?(tone==='cobalt'?'#3157D5':'#162760'):['navy','cobalt','black'].includes(tone)?'#FFFFFF':'#162760',...props.style} as React.CSSProperties} className={`os5-button os5-button--${tone} os5-button--${variant} ${className}`} disabled={blocked} aria-busy={loading||undefined}
    onPointerMove={e=>{const item=entry.current;if(item&&!reduced.current&&e.pointerType==='mouse'&&matchMedia('(pointer:fine)').matches){const b=e.currentTarget.getBoundingClientRect();item.tx=-((e.clientY-b.top)/b.height-.5)*.22;item.ty=((e.clientX-b.left)/b.width-.5)*.3;item.active=true;item.dirty=true;schedule();}onPointerMove?.(e);}}
    onPointerLeave={e=>{reset();onPointerLeave?.(e);}} onPointerCancel={e=>{reset();onPointerCancel?.(e);}}
    onPointerDown={e=>{focus();onPointerDown?.(e);}} onFocus={e=>{focus();onFocus?.(e);}} onBlur={e=>{reset();onBlur?.(e);}}>
    <canvas className="os5-button__canvas" ref={canvas} aria-hidden="true"/>
    <span ref={ink} className="os5-button__ink">{loading?<span className="os5-button__loading" aria-hidden="true"/>:null}<span>{children}</span>{arrow&&!loading?<span className="os5-button__arrow" aria-hidden="true">↗</span>:null}</span>
  </button>;
});
