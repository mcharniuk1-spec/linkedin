import {useEffect,useState} from 'react';
import {useTransform,type MotionValue} from 'motion/react';

const smooth=(v:number)=>{const t=Math.max(0,Math.min(1,v));return t*t*(3-2*t);};

export function useShortHeroViewport(){
  const query='(max-height:559px) and (orientation:landscape)';
  const [short,setShort]=useState(()=>matchMedia(query).matches);
  useEffect(()=>{const media=matchMedia(query),update=()=>setShort(media.matches);media.addEventListener('change',update);return()=>media.removeEventListener('change',update);},[]);
  return short;
}

/** Separate reading, shadow growth and media beats. Forward and reverse use one clock. */
export function useHeroPhases(progress:MotionValue<number>,still:boolean){
  const [phase,setPhase]=useState('intro');
  useEffect(()=>{const update=(p:number)=>setPhase(p<.22?'intro':p<.53?'shadow':p<.56?'covered':p<.78?'entering':'media');update(progress.get());return progress.on('change',update);},[progress]);
  const copyOpacity=useTransform(progress,p=>1-smooth((p-.12)/.10));
  const copyY=useTransform(progress,p=>-24*smooth((p-.12)/.10));
  const shadowScale=useTransform(progress,p=>1+4.8*smooth((p-.24)/.28));
  const shadowOpacity=useTransform(progress,p=>1-smooth((p-.48)/.05));
  const cover=useTransform(progress,p=>`circle(${94.5*smooth((p-.24)/.28)}% at 64% 66%)`);
  const mediaOpacity=useTransform(progress,p=>smooth((p-.56)/.22));
  const mediaY=useTransform(progress,p=>64*(1-smooth((p-.56)/.22)));
  const mediaScale=useTransform(progress,p=>.965+.035*smooth((p-.56)/.22));
  const cueOpacity=useTransform(progress,p=>1-smooth((p-.10)/.10));
  return {phase,ready:still||phase==='media',copyReady:still||phase==='intro',copyOpacity,copyY,shadowScale,shadowOpacity,cover,mediaOpacity,mediaY,mediaScale,cueOpacity};
}
