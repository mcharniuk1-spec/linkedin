import {useEffect,useRef,useState} from 'react';
import {motion,useMotionValueEvent,useReducedMotion,useScroll} from 'motion/react';
import story from './buyer-story.json';
import './buyer-story.css';

/** OS-WEB-V9-001. Native scrolling; five independent value hypotheses, never a funnel. */
export function BuyerStory({forceFlow=false}:{forceFlow?:boolean}){
  const host=useRef<HTMLElement>(null),heading=useRef<HTMLHeadingElement>(null),reduced=useReducedMotion();
  const [compact,setCompact]=useState(()=>matchMedia('(max-width:359px), (max-width:800px) and (max-height:779px), (min-width:801px) and (max-height:679px)').matches);
  const [reading,setReading]=useState(()=>{try{return sessionStorage.getItem('outspoken-buyer-story-flow')==='true'}catch{return false}}),[active,setActive]=useState(0);
  const flow=forceFlow||!!reduced||compact||reading||new URLSearchParams(location.search).has('design');
  const {scrollYProgress}=useScroll({target:host,offset:['start start','end end']});
  useEffect(()=>{const m=matchMedia('(max-width:359px), (max-width:800px) and (max-height:779px), (min-width:801px) and (max-height:679px)'),update=()=>setCompact(m.matches);m.addEventListener('change',update);return()=>m.removeEventListener('change',update)},[]);
  useMotionValueEvent(scrollYProgress,'change',p=>{if(!flow)setActive(Math.min(story.beats.length-1,Math.max(0,Math.floor(p*story.beats.length))))});
  const choose=(index:number)=>{const node=host.current;if(!node)return;const top=node.getBoundingClientRect().top+scrollY;const run=node.offsetHeight-innerHeight;scrollTo({top:top+run*((index+.45)/story.beats.length),behavior:'instant'});setActive(index)};
  const readAll=()=>{try{sessionStorage.setItem('outspoken-buyer-story-flow','true')}catch{}setReading(true);requestAnimationFrame(()=>{host.current?.scrollIntoView({block:'start',behavior:'instant'});heading.current?.focus({preventScroll:true})})};
  return <><section ref={host} id="business-value" className={'buyer-story '+(flow?'is-flow':'is-pinned')} data-block="buyer-story" data-story-mode={flow?'flow':'scroll'} data-active-beat={active} aria-labelledby="buyer-story-heading">
    <div className="buyer-story__pin">
      <div className="buyer-story__resonance" aria-hidden="true"><i/><i/><i/></div>
      <header className="buyer-story__intro"><p className="eyebrow">The work. The reason for it.</p><h2 ref={heading} tabIndex={-1} id="buyer-story-heading">What would make <span>LinkedIn worth it?</span></h2><p>{story.section_intro}</p><p className="buyer-story__scope">{story.scope_label}</p>
        {!flow?<button type="button" className="buyer-story__read" onClick={readAll}>Read the full story without motion ↗</button>:null}
        <a className="buyer-story__service" href="/services">Explore the services ↗</a>
      </header>
      <div className="buyer-story__content"><nav className="buyer-story__nav" aria-label="Choose a business question">{story.beats.map((beat,i)=>flow?<a key={beat.id} href={'#buyer-'+beat.id}>{String(i+1).padStart(2,'0')}<span>{beat.nav}</span></a>:<button key={beat.id} type="button" onClick={()=>choose(i)} aria-current={active===i?'step':undefined} aria-label={'Read: '+beat.nav}><span className="buyer-story__number">{String(i+1).padStart(2,'0')}</span><span>{beat.nav}</span></button>)}</nav>
        <ol className="buyer-story__nodes">{story.beats.map((beat,i)=><motion.li key={beat.id} id={'buyer-'+beat.id} className="buyer-story__node" data-story-node={beat.id} hidden={!flow&&active!==i} initial={false} animate={{opacity:flow||active===i?1:0,y:flow||active===i?0:12}} transition={{duration:flow?0:.25,ease:[.2,.75,.2,1]}}>
          <div className="buyer-story__card-head"><span>{beat.eyebrow}</span><span>{String(i+1).padStart(2,'0')} / 05</span></div>
          <h3>{beat.title}</h3><p className="buyer-story__pain">{beat.pain}</p>
          <div className="buyer-story__work"><span className="buyer-story__label">Proposed support</span><p>{beat.approach}</p></div>
          <div className="buyer-story__signal"><span className="buyer-story__label">A signal to observe</span><p>{beat.signal}</p></div>
        </motion.li>)}</ol>
        <p className="buyer-story__value-note">Five separate value hypotheses. Choose what matters to you; no promised results or funnel stages.</p>
      </div>
    </div>
  </section><section className="buyer-story__rationale" aria-label="Why OUTSPOKEN"><p className="eyebrow">Why OUTSPOKEN</p><h3>{story.why_title}</h3><p>{story.why_body}</p><p className="buyer-story__responsibilities">Before we start, we agree interview cadence, preparation, approvals, deliverables and permissions.</p></section></>;
}
