import {useEffect,useRef,useState,type CSSProperties,type ReactNode} from 'react';
import {useReducedMotion,useScroll,type MotionValue} from 'motion/react';
import './mobile-chapter.css';

function useMediaQuery(query:string){
  const [matches,setMatches]=useState(()=>typeof window!=='undefined'&&window.matchMedia(query).matches);
  useEffect(()=>{
    const media=window.matchMedia(query),update=()=>setMatches(media.matches);
    update();media.addEventListener('change',update);
    return()=>media.removeEventListener('change',update);
  },[query]);
  return matches;
}

export function useMobileLayout(){return useMediaQuery('(max-width:800px)');}

export type MobileChapterProps={
  id?:string;
  className?:string;
  pages?:number;
  ariaLabel?:string;
  children:(progress:MotionValue<number>,still:boolean)=>ReactNode;
};

/** Native document scroll gives every chapter the same forward and reverse clock. */
export function MobileChapter({id,className='',pages=2.6,children,ariaLabel}:MobileChapterProps){
  const host=useRef<HTMLElement>(null),reduced=useReducedMotion();
  const shortLandscape=useMediaQuery('(max-height:619px) and (orientation:landscape), (max-height:699px) and (orientation:portrait)');
  const design=typeof location!=='undefined'&&new URLSearchParams(location.search).has('design');
  const still=!!reduced||shortLandscape||design;
  const {scrollYProgress}=useScroll({target:host,offset:['start start','end end']});
  const style={'--m-chapter-pages':Math.max(1,pages)} as CSSProperties;
  return <section ref={host} id={id} className={`m-chapter ${className}${still?' is-reduced':''}`} style={style} data-mobile-chapter={id||className} data-motion={still?'linear':'scroll'} aria-label={ariaLabel}>
    <div className="m-chapter__pin" data-mobile-stage={id||className}>{children(scrollYProgress,still)}</div>
  </section>;
}
