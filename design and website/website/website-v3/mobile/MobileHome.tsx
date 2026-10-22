import {useEffect,useRef,useState,type ComponentType,type ReactNode} from 'react';
import {AnimatePresence,motion,useMotionValueEvent,useReducedMotion,useTransform,type MotionValue} from 'motion/react';
import {PerspectiveVideo} from '../../packages/experience-v3';
import content from '../content.json';
import reviewData from '../reviews.json';
import {MobileChapter} from './MobileChapter';
import {MobileExpertise} from './MobileExpertise';
import {useHeroPhases} from '../hero-phases';
import {HeroPublication} from '../HeroPublication';
import './mobile-home.css';

type Parts={
  PostCard:ComponentType<any>; MailCard:ComponentType<any>; CallButton:ComponentType<any>;
  SoundWaves:ComponentType<any>; OpinionReader:ComponentType<any>;
  services:ReactNode; process:ReactNode; pricing:ReactNode; faq:ReactNode; closing:ReactNode;
};
const emails=(reviewData as any).emails??(reviewData as any).reviews??reviewData;
const ease=[.2,.75,.2,1] as const;

function HeroScene({progress,still,CallButton,SoundWaves,PostCard}:{progress:MotionValue<number>;still:boolean}&Pick<Parts,'CallButton'|'SoundWaves'|'PostCard'>){
  const [focused,setFocused]=useState(false),phase=useHeroPhases(progress,still);
  const waveRotate=useTransform(progress,[0,1],[-9,8]);
  return <div className={'m-hero__scene m-hero__scene--v7'+(focused?' is-focused':'')} data-mobile-stage="hero" data-hero-phase={phase.phase}>
    <motion.div className="m-hero__waves" style={still?undefined:{rotate:waveRotate}}><SoundWaves/></motion.div>
    <motion.div className="m-hero__shadow" data-shadow-figure="" style={still?undefined:{opacity:phase.shadowOpacity,scale:phase.shadowScale}}><img src="/assets/revisions/v3/nature/05-real-human-shadow.webp" alt="Photographic shadow of a fictional person speaking"/></motion.div>
    <motion.div className="m-hero__copy" inert={!phase.copyReady} style={still?undefined:{opacity:phase.copyOpacity,y:phase.copyY}}>
      <p className="eyebrow">{content.home.eyebrow}</p>
      <h1>Make the <span className="highlight">right buyers</span> care about you and what you’re building.</h1>
      <p className="m-hero__value">{content.protected.vp}</p><CallButton/>
      <p className="m-hero__audience">Europe-based B2B AI SaaS · Seed to Series B</p>
    </motion.div>
    {!still?<motion.div className="v7-shadow-cover" data-shadow-cover="" aria-hidden="true" style={{clipPath:phase.cover}}/>:null}
    <motion.div className="m-hero__film" data-hero-media="" inert={!phase.ready} style={still?undefined:{opacity:phase.mediaOpacity,y:phase.mediaY,scale:phase.mediaScale}}>
      <div className="m-hero__film-copy"><p className="eyebrow">A point of view worth hearing.</p><h2>Founder thinking.<br/><span className="highlight">Buyer relevance.</span></h2></div>
      <div className="m-hero__media" data-mobile-dock="video"><PerspectiveVideo poster="/assets/revisions/v5/people/founder-blue.webp" src="/video/revisions/v5/Outspoken-v5-style-proof-landscape.mp4" title="Founder thinking. Buyer relevance." description="An original silent visual study. The people and publications shown are illustrative, not customers or client results." caption="Fictional interview image · silent visual study" onOpenChange={setFocused}/><div className="m-hero__publication" data-hero-post=""><HeroPublication post={content.posts[0]} onOpenChange={setFocused}><PostCard post={content.posts[0]}/></HeroPublication></div></div>
    </motion.div>
    {!still?<motion.div className="m-chapter-cue" style={{opacity:phase.cueOpacity}} aria-hidden="true"><span>Scroll to bring the story into focus</span><span>↓</span></motion.div>:null}
  </div>;
}

type DeckProps={progress:MotionValue<number>;still:boolean;items:any[];render:(item:any,index:number)=>ReactNode;kind:'publications'|'opinions';label:string};
/** One complete reading surface. Native vertical scrolling and explicit touch controls share the same deck. */
function ReadingDeck({progress,still,items,render,kind,label}:DeckProps){
  const [index,setIndex]=useState(0),[direction,setDirection]=useState(1);
  const lastScrollIndex=useRef(0),current=useRef(0),pointer=useRef<{x:number;y:number}|null>(null);
  const select=(next:number)=>{const normalized=(next+items.length)%items.length;setDirection(normalized>=current.current?1:-1);current.current=normalized;setIndex(normalized);};
  useMotionValueEvent(progress,'change',v=>{const next=Math.min(items.length-1,Math.floor(v*items.length));if(next!==lastScrollIndex.current){lastScrollIndex.current=next;select(next);}});
  if(still)return <div className={'m-deck-linear m-deck-linear--'+kind} data-mobile-stage={kind}>{items.map((item,i)=><div key={item.id??i}>{render(item,i)}</div>)}</div>;
  return <div className={'m-reading-deck m-reading-deck--'+kind} data-mobile-stage={kind} data-active-index={index}>
    <div className="m-deck-caption"><span>{label}</span><span aria-live="polite" aria-atomic="true">{String(index+1).padStart(2,'0')} / {String(items.length).padStart(2,'0')}</span></div>
    <div className="m-reading-deck__surface" data-mobile-dock={kind} onPointerDown={e=>{pointer.current={x:e.clientX,y:e.clientY};}} onPointerUp={e=>{const start=pointer.current;pointer.current=null;if(!start)return;const dx=e.clientX-start.x,dy=e.clientY-start.y;if(Math.abs(dx)>60&&Math.abs(dx)>Math.abs(dy)*1.5)select(current.current+(dx<0?1:-1));}} onPointerCancel={()=>{pointer.current=null;}}>
      <div className="m-deck-back m-deck-back--two" aria-hidden="true"/><div className="m-deck-back m-deck-back--one" aria-hidden="true"/>
      <AnimatePresence initial={false} custom={direction} mode="popLayout"><motion.div className="m-reading-deck__card" key={index} custom={direction} variants={{enter:(d:number)=>({x:d*90,y:20,rotateY:d*-12,rotateZ:d*2,opacity:0}),center:{x:0,y:0,rotateY:0,rotateZ:0,opacity:1},exit:(d:number)=>({x:d*-45,y:-12,scale:.96,rotateY:d*5,opacity:0})}} initial="enter" animate="center" exit="exit" transition={{duration:.5,ease}}>{render(items[index],index)}</motion.div></AnimatePresence>
    </div>
    <div className="m-deck-controls" aria-label={label+' navigation'}><button type="button" onClick={()=>select(index-1)} aria-label={'Previous '+(kind==='opinions'?'sample email':'publication example')}>←</button><span>Scroll or swipe to explore</span><button type="button" onClick={()=>select(index+1)} aria-label={'Next '+(kind==='opinions'?'sample email':'publication example')}>→</button></div>
  </div>;
}

function Publications({PostCard}:Pick<Parts,'PostCard'>){
  const [browse,setBrowse]=useState(false),section=useRef<HTMLElement>(null);
  return <section className="m-publications" id="publications" ref={section} data-block="mobile-publications">
    <div className="m-section-intro"><p className="eyebrow">A recognizable point of view</p><motion.h2 initial={{opacity:0,y:24}} whileInView={{opacity:1,y:0}} viewport={{once:true,amount:.5}} transition={{duration:.6,ease}}>One strong idea.<br/><span className="highlight">Many ways to tell it.</span></motion.h2><p>Professional posts. Personal stories. Carousels, product walkthroughs and architecture explainers. Every format starts with something worth saying.</p><button type="button" className="text-control" aria-expanded={browse} onClick={()=>{setBrowse(!browse);if(browse)section.current?.scrollIntoView({block:'start',behavior:'instant'});}}>{browse?'Return to scroll story':'Browse all publication examples'} ↗</button></div>
    {browse?<div className="m-deck-linear m-deck-linear--publications">{content.posts.map((post,i)=><PostCard key={post.id} post={post} index={i}/>)}</div>:<MobileChapter className="m-publication-chapter" pages={3.4} ariaLabel="Publication examples">{(progress,still)=><ReadingDeck progress={progress} still={still} items={content.posts} kind="publications" label="Publication examples" render={(post,i)=><PostCard post={post} index={i}/>}/>}</MobileChapter>}
  </section>;
}

function Opinions({MailCard,OpinionReader,SoundWaves}:Pick<Parts,'MailCard'|'OpinionReader'|'SoundWaves'>){
  const [reader,setReader]=useState<number|null>(null);
  return <section className="m-opinions" id="opinions" data-block="mobile-customer-opinion"><div className="m-section-intro"><p className="eyebrow">The human side of the work</p><h2>Customer<br/><span className="highlight">Opinion.</span></h2><p>Fifteen sample conversations about a clearer profile, better stories and a more useful content process. Fictional examples, shown as a design study.</p><button type="button" className="text-control" onClick={()=>setReader(0)}>Browse all 15 emails ↗</button></div><MobileChapter className="m-opinion-chapter" pages={4.5} ariaLabel="Fifteen sample emails">{(progress,still)=><><div className="m-opinions__waves"><SoundWaves/></div><ReadingDeck progress={progress} still={still} items={emails} kind="opinions" label="Customer Opinion · samples" render={(email,i)=><MailCard email={email} onOpen={()=>setReader(i)}/>}/></>}</MobileChapter>{reader!==null?<OpinionReader index={reader} onIndex={setReader} onClose={()=>setReader(null)}/>:null}</section>;
}

export function MobileHome({PostCard,MailCard,CallButton,SoundWaves,OpinionReader,services,process,pricing,faq,closing}:Parts){
  const host=useRef<HTMLDivElement>(null),reduced=useReducedMotion();
  useEffect(()=>{
    if(reduced||new URLSearchParams(location.search).has('design'))return;
    const cards=host.current?.querySelectorAll<HTMLElement>('.service-plate,.process-section li,.price-plan,.faq-section details,.closing-panel>img');
    const animations:Animation[]=[];
    const observer=new IntersectionObserver(entries=>{for(const entry of entries){if(!entry.isIntersecting)continue;const element=entry.target as HTMLElement;observer.unobserve(element);animations.push(element.animate([{opacity:.25,transform:'translateY(32px) rotateX(3deg)'},{opacity:1,transform:'translateY(0) rotateX(0)'}],{duration:650,easing:'cubic-bezier(.2,.75,.2,1)'}));}},{threshold:.12});
    cards?.forEach(card=>observer.observe(card));return()=>{observer.disconnect();animations.forEach(animation=>animation.cancel());};
  },[reduced]);
  return <div ref={host} className="mobile-home"><MobileChapter className="m-hero" pages={3} ariaLabel="Founder thinking and buyer relevance">{(progress,still)=><HeroScene progress={progress} still={still} CallButton={CallButton} SoundWaves={SoundWaves} PostCard={PostCard}/>}</MobileChapter><MobileExpertise/><Publications PostCard={PostCard}/><div className="m-flow m-flow--services">{services}</div><div className="m-flow m-flow--process">{process}</div><Opinions MailCard={MailCard} OpinionReader={OpinionReader} SoundWaves={SoundWaves}/><div className="m-flow m-flow--pricing">{pricing}</div><div className="m-flow m-flow--faq">{faq}</div><div className="m-flow m-flow--closing">{closing}</div></div>;
}
