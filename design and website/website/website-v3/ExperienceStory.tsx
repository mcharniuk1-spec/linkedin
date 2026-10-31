import {useEffect,useRef,useState} from 'react';
import {motion,useReducedMotion,useScroll} from 'motion/react';
import story from './buyer-story.json';
import './experience-story.css';

/** OS-WEB-V10-001. One block for blocks 3-5: expertise, formats and the five value markers. Cards travel sideways inside a clipped frame. */
const cards=[
  {id:'experience',nav:'Experience',eyebrow:'Your personal brand positioning',title:'A clear position, built from the substance of your company.',body:'We uncover the experience, methods, tools and product judgment inside your business. Then we connect the evidence to the customer’s question.',signal:''},
  ...story.beats.map(b=>({id:b.id,nav:b.nav,eyebrow:b.eyebrow,title:b.title,body:b.approach,signal:b.signal}))
];
const sources=['Experience','Methods','Tools','Product judgment'],results=['Positioning','Profile','Content','Distribution'];
const count=cards.length,pad=(n:number)=>String(n).padStart(2,'0'),ys=[12.5,37.5,62.5,87.5];

function Schema(){
  return <figure className="xs-schema" aria-label="How substance becomes positioning: experience, methods, tools and product judgment meet the customer’s question and become positioning, profile, content and distribution.">
    <ul aria-hidden="true">{sources.map(s=><li key={s}>{s}</li>)}</ul>
    <svg viewBox="0 0 60 100" preserveAspectRatio="none" aria-hidden="true">{ys.map(y=><path key={'l'+y} d={`M0 ${y} C24 ${y},24 50,30 50`}/>)}{ys.map(y=><path key={'r'+y} d={`M30 50 C36 50,36 ${y},60 ${y}`}/>)}</svg>
    <ul aria-hidden="true">{results.map(s=><li key={s}>{s}</li>)}</ul>
    <figcaption>Substance → the customer’s question → what buyers see</figcaption>
  </figure>;
}

export function ExperienceStory({forceRail=false}:{forceRail?:boolean}){
  const host=useRef<HTMLElement>(null),view=useRef<HTMLDivElement>(null),track=useRef<HTMLUListElement>(null),reduced=useReducedMotion();
  const [wide,setWide]=useState(()=>matchMedia('(min-width:901px) and (min-height:640px)').matches),[list,setList]=useState(false),[active,setActive]=useState(0);
  const scrub=wide&&!reduced&&!list&&!forceRail&&!new URLSearchParams(location.search).has('design');
  const {scrollYProgress:p}=useScroll({target:host,offset:['start start','end end']});
  useEffect(()=>{const m=matchMedia('(min-width:901px) and (min-height:640px)'),f=()=>setWide(m.matches);m.addEventListener('change',f);return()=>m.removeEventListener('change',f)},[]);
  // Scroll-scrubbed mode: the track moves as a whole; each card reads its distance from the centre through --d.
  useEffect(()=>{
    const v=view.current,t=track.current;if(!v||!t||!scrub)return;
    const items=Array.from(t.children) as HTMLElement[];let pos=0;
    const apply=()=>{
      const w=v.clientWidth,at=(i:number)=>items[i].offsetLeft+items[i].offsetWidth/2,i0=Math.min(count-1,Math.floor(pos)),i1=Math.min(count-1,i0+1);
      t.style.transform=`translate3d(${w/2-(at(i0)+(at(i1)-at(i0))*(pos-i0))}px,0,0)`;
      items.forEach((el,i)=>el.style.setProperty('--d',Math.min(Math.abs(i-pos),2).toFixed(3)));
      const index=Math.round(pos);setActive(a=>a===index?a:index);
    };
    const update=(x:number)=>{pos=Math.min(1,Math.max(0,(x-.06)/.88))*(count-1);apply()};
    update(p.get());const off=p.on('change',update),ro=new ResizeObserver(apply);ro.observe(v);
    return()=>{off();ro.disconnect();t.style.transform='';items.forEach(el=>el.style.removeProperty('--d'))};
  },[scrub,p]);
  // Rail mode: native horizontal scrolling with snap; the active chip follows the scroll position.
  useEffect(()=>{
    const v=view.current,t=track.current;if(!v||!t||scrub||list)return;
    const items=Array.from(t.children) as HTMLElement[];
    const on=()=>{const c=v.scrollLeft+v.clientWidth/2;let best=0,dist=Infinity;items.forEach((el,i)=>{const d=Math.abs(el.offsetLeft+el.offsetWidth/2-c);if(d<dist){dist=d;best=i}});setActive(best)};
    on();v.addEventListener('scroll',on,{passive:true});return()=>v.removeEventListener('scroll',on);
  },[scrub,list]);
  const go=(i:number)=>{
    const behavior=reduced?'auto':'smooth',target=Math.min(count-1,Math.max(0,i));
    if(scrub){const n=host.current;if(!n)return;const top=n.getBoundingClientRect().top+scrollY,run=n.offsetHeight-innerHeight;scrollTo({top:top+run*(.06+.88*(target/(count-1))),behavior});}
    else if(list){(track.current?.children[target] as HTMLElement|undefined)?.scrollIntoView({block:'center',behavior});}
    else{const v=view.current,el=track.current?.children[target] as HTMLElement|undefined;if(v&&el)v.scrollTo({left:el.offsetLeft-(v.clientWidth-el.offsetWidth)/2,behavior});}
    setActive(target);
  };
  const motionOn=!reduced&&!new URLSearchParams(location.search).has('design');
  return <section ref={host} id="approach" className={'xs '+(scrub?'is-scrub':'is-rail')+(list?' is-list':'')} data-block="experience-story" data-story-mode={scrub?'scrub':list?'list':'rail'} style={scrub?{height:`calc(100dvh + ${(count-1)*54}vh)`}:undefined} aria-labelledby="xs-heading">
    <div className="xs__stage">
      <motion.header className="xs__head" initial={motionOn?{opacity:0,y:26}:false} whileInView={{opacity:1,y:0}} viewport={{once:true,amount:.35}} transition={{duration:.8,ease:[.16,1,.3,1]}}>
        <p className="eyebrow">From what you know to what buyers understand</p>
        <h2 id="xs-heading">Your experience.<br/>{' '}Your <span className="highlight">edge.</span></h2>
        <p className="xs__sub">One strong idea. <span className="highlight">Many ways</span> to tell it.</p>
        <p className="xs__lede">Posts, personal stories, carousels, walkthroughs and explainers. Every format starts with something worth saying.</p>
      </motion.header>
      <div className="xs__nav">
        <p className="xs__ask">What would make LinkedIn worth it?</p>
        <div className="xs__chips" role="group" aria-label="Choose a card">{cards.map((c,i)=><button key={c.id} type="button" aria-current={active===i?'true':undefined} onClick={()=>go(i)}><span>{pad(i+1)}</span>{c.nav}</button>)}</div>
      </div>
      <div className="xs__frame">
        <div ref={view} className="xs__view" {...(!scrub&&!list?{tabIndex:0,role:'region','aria-label':'Value markers, scroll sideways'}:{})}>
          <ul ref={track} className="xs__track">{cards.map((c,i)=><li key={c.id} id={'edge-'+c.id} className={'xs-card'+(active===i?' is-active':'')} data-card={c.id}>
            <div className="xs-card__head"><span>{c.eyebrow}</span><span>{pad(i+1)} / {pad(count)}</span></div>
            <h3>{c.title}</h3><p>{c.body}</p>
            {i===0?<Schema/>:c.signal?<div className="xs-card__signal"><span>A signal to observe</span><p>{c.signal}</p></div>:null}
          </li>)}</ul>
        </div>
      </div>
      <div className="xs__foot">
        <p><span className="xs__formats">Posts, personal stories, carousels, walkthroughs and explainers: every format starts with something worth saying. </span>Five separate kinds of value to agree and observe. Not promised results, not funnel stages.</p>
        <div className="xs__controls">
          {!scrub&&!list?<><button type="button" aria-label="Previous card" disabled={active===0} onClick={()=>go(active-1)}>←</button><button type="button" aria-label="Next card" disabled={active===count-1} onClick={()=>go(active+1)}>→</button></>:null}
          {!forceRail?<button type="button" className="xs__mode" aria-pressed={list} onClick={()=>{setList(!list);requestAnimationFrame(()=>host.current?.scrollIntoView({block:'start',behavior:'instant'}))}}>{list?'Back to the card view':'Read all as a list'}</button>:null}
          <a href="/services">Explore the services ↗</a>
        </div>
      </div>
    </div>
  </section>;
}
