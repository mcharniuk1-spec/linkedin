import { useEffect, useId, useLayoutEffect, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { useReducedMotion } from 'motion/react';
import './experience.css';

export type PerspectiveVideoProps = {
  poster: string; src: string; title: string; description?: string; caption?: string;
  className?: string; onOpenChange?: (open: boolean) => void;
  tilt?: 'left' | 'right'; autoPlayOnOpen?: boolean;
};
type Pose={x:number;y:number;width:number;height:number;yaw:number;roll:number};
type Phase='perspective'|'opening'|'focused'|'closing';
const mix=(a:number,b:number,t:number)=>a+(b-a)*t;
/** A single measured media plane flies into a native dialog and returns to its
 * origin. No portal/layoutId crossfade is used. Video loads only on activation. */
export function PerspectiveVideo({poster,src,title,description,caption,className='',onOpenChange,tilt='left',autoPlayOnOpen=false}:PerspectiveVideoProps){
  const [active,setActive]=useState(false),[phase,setPhase]=useState<Phase>('perspective'),[failed,setFailed]=useState(false);
  const trigger=useRef<HTMLButtonElement>(null),originPlate=useRef<HTMLDivElement>(null),dialog=useRef<HTMLDialogElement>(null),shell=useRef<HTMLDivElement>(null),focusPlate=useRef<HTMLDivElement>(null),scrim=useRef<HTMLDivElement>(null),closeButton=useRef<HTMLButtonElement>(null),video=useRef<HTMLVideoElement>(null);
  const id=useId(),reduced=useReducedMotion(),frame=useRef(0),phaseRef=useRef<Phase>('perspective'),origin=useRef<Pose|null>(null),current=useRef<Pose|null>(null),previousOverflow=useRef<string|null>(null),hover=useRef(false),poseAngle=useRef({yaw:0,roll:0}),focusAmount=useRef(0),callback=useRef(onOpenChange);
  callback.current=onOpenChange;
  const angle=tilt==='left'?-18:18,roll=tilt==='left'?-3:3;
  const prefersStill=()=>!!reduced||matchMedia('(prefers-reduced-motion: reduce)').matches;
  function originTransform(over:boolean){hover.current=over;const yaw=prefersStill()?0:angle*(over ? .65 : 1),z=prefersStill()?0:roll*(over ? .34 : 1);poseAngle.current={yaw,roll:z};if(originPlate.current)originPlate.current.style.transform=`perspective(1400px) rotateY(${yaw}deg) rotateZ(${z}deg)`;}
  function measure():Pose{const box=trigger.current!.getBoundingClientRect(),matrix=originPlate.current?new DOMMatrix(getComputedStyle(originPlate.current).transform):null;const yaw=matrix?Math.atan2(matrix.m31,matrix.m33)*180/Math.PI:poseAngle.current.yaw,z=matrix?Math.atan2(matrix.m12,matrix.m22)*180/Math.PI:poseAngle.current.roll;return{x:box.left,y:box.top,width:box.width,height:box.height,yaw,roll:z};}
  function target():Pose{const w=Math.max(1,Math.min(1120,innerWidth-32,(innerHeight-180)*16/9));return{x:(innerWidth-w)/2,y:(innerHeight-w*9/16)/2,width:w,height:w*9/16,yaw:0,roll:0};}
  function apply(pose:Pose,amount:number){
    current.current=pose;focusAmount.current=amount;const element=shell.current,plate=focusPlate.current;if(!element||!plate)return;
    Object.assign(element.style,{left:`${pose.x}px`,top:`${pose.y}px`,width:`${pose.width}px`,height:`${pose.height}px`,visibility:'visible'});
    plate.style.transform=`perspective(1400px) rotateY(${pose.yaw}deg) rotateZ(${pose.roll}deg)`;
    element.style.setProperty('--os3-focus-reveal',String(Math.max(0,Math.min(1,(amount-.38)/.62))));
    if(scrim.current)scrim.current.style.opacity=String(amount);
    const values=[pose.x,pose.y,pose.width,pose.height,pose.yaw,pose.roll].map(n=>n.toFixed(3)).join(',');element.dataset.pose=values;element.dataset.flight=amount.toFixed(4);if(dialog.current){dialog.current.dataset.pose=values;dialog.current.dataset.flight=amount.toFixed(4);}
  }
  function flight(from:Pose,to:Pose,opening:boolean,done:()=>void){
    cancelAnimationFrame(frame.current);const started=performance.now(),duration=prefersStill()?0:620,fromFocus=focusAmount.current;
    const tick=(now:number)=>{const t=duration?Math.min(1,(now-started)/duration):1,e=t*t*(3-2*t),p={x:mix(from.x,to.x,e),y:mix(from.y,to.y,e),width:mix(from.width,to.width,e),height:mix(from.height,to.height,e),yaw:mix(from.yaw,to.yaw,e),roll:mix(from.roll,to.roll,e)};apply(p,mix(fromFocus,opening?1:0,e));if(t<1)frame.current=requestAnimationFrame(tick);else{frame.current=0;done();}};
    apply(from,fromFocus);frame.current=requestAnimationFrame(tick);
  }
  function restore(){if(previousOverflow.current!==null){document.body.style.overflow=previousOverflow.current;previousOverflow.current=null;}trigger.current?.focus({preventScroll:true});}
  function open(){if(phaseRef.current!=='perspective'||!trigger.current)return;if(prefersStill())originTransform(false);origin.current=measure();current.current=origin.current;phaseRef.current='opening';setPhase('opening');setFailed(false);setActive(true);callback.current?.(true);}
  function close(){if(phaseRef.current==='perspective'||phaseRef.current==='closing')return;video.current?.pause();phaseRef.current='closing';setPhase('closing');callback.current?.(false);const end=trigger.current?measure():origin.current!;flight(current.current??target(),end,false,()=>{dialog.current?.close();phaseRef.current='perspective';setPhase('perspective');setActive(false);restore();});}
  useLayoutEffect(()=>{originTransform(hover.current);},[tilt,reduced]);
  useLayoutEffect(()=>{
    if(!active)return;const node=dialog.current;if(!node)return;if(!node.open)node.showModal();if(previousOverflow.current===null)previousOverflow.current=document.body.style.overflow;document.body.style.overflow='hidden';
    flight(origin.current!,target(),true,()=>{if(phaseRef.current==='opening'){phaseRef.current='focused';setPhase('focused');}});
    // flight() initializes the formerly hidden plane before its close control can receive focus.
    closeButton.current?.focus({preventScroll:true});
    const resize=()=>{if(phaseRef.current==='focused')apply(target(),1);};window.addEventListener('resize',resize);return()=>window.removeEventListener('resize',resize);
  },[active]);
  useEffect(()=>()=>{cancelAnimationFrame(frame.current);video.current?.pause();dialog.current?.close();if(previousOverflow.current!==null)document.body.style.overflow=previousOverflow.current;},[]);
  return <figure className={`os3-perspective ${active?'is-open':''} ${className}`} data-state={phase} data-transition="measured-plane-620ms">
    <div className="os3-perspective__stage"><button ref={trigger} className="os3-perspective__trigger" type="button" aria-haspopup="dialog" aria-expanded={active} aria-label={`Watch: ${title}`} onClick={open} onPointerEnter={e=>{if(e.pointerType==='mouse')originTransform(true);}} onPointerLeave={()=>originTransform(false)}>
      <div ref={originPlate} data-plane="origin" className="os3-perspective__plate" style={{visibility:active?'hidden':'visible'}}><img className="os3-perspective__poster" src={poster} alt="" loading="lazy" width="1600" height="900"/><span className="os3-perspective__shade"/><span className="os3-perspective__play" aria-hidden="true"><svg viewBox="0 0 24 24" width="22" height="22"><path d="M9 5.5 19 12 9 18.5Z" fill="currentColor"/></svg></span><span className="os3-perspective__label">{title}<span>Watch the film ↗</span></span></div>
    </button></div>{caption?<figcaption>{caption}</figcaption>:null}
    {active&&typeof document!=='undefined'?createPortal(<dialog ref={dialog} aria-labelledby={`${id}-title`} aria-describedby={description?`${id}-description`:undefined} className="os3-video-dialog" data-state={phase} onCancel={e=>{e.preventDefault();close();}} onClick={e=>{if(e.target===e.currentTarget)close();}}>
      <div ref={scrim} className="os3-video-dialog__scrim" onClick={close}/><div ref={shell} className="os3-video-dialog__content" data-state={phase}>
        <div className="os3-video-dialog__top"><h2 id={`${id}-title`}>{title}</h2><button ref={closeButton} type="button" className="os3-video-dialog__close" onClick={close} aria-label="Close video">Close <span aria-hidden="true">×</span></button></div>
        <div ref={focusPlate} data-plane="focus" className="os3-perspective__plate os3-video-dialog__plate"><img className="os3-perspective__poster" src={poster} alt=""/><span className="os3-video-dialog__origin-chrome"><span className="os3-perspective__shade"/><span className="os3-perspective__play" aria-hidden="true"><svg viewBox="0 0 24 24" width="22" height="22"><path d="M9 5.5 19 12 9 18.5Z" fill="currentColor"/></svg></span><span className="os3-perspective__label">{title}<span>Watch the film ↗</span></span></span><video ref={video} src={src} poster={poster} controls playsInline preload="auto" autoPlay={autoPlayOnOpen} muted={autoPlayOnOpen} onError={()=>setFailed(true)}/></div>
        <div className="os3-video-dialog__description">{description?<p id={`${id}-description`}>{description}</p>:null}{failed?<p role="alert">The film could not load. <a href={src}>Open the video file</a>.</p>:null}</div>
      </div></dialog>,document.body):null}
  </figure>;
}
